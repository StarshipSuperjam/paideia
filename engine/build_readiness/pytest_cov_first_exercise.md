# pytest-cov coverage floor — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the pytest-cov CI coverage gate landed at S-0136 per [ADR 0074](../adr/0074-pytest-cov-coverage-floor.md) (Issue [#71](https://github.com/StarshipSuperjam/paideia/issues/71)).

## Trigger criteria evaluation

Per ADR 0053 the mechanism qualifies for a readiness note when ANY of:

- ❌ Criterion 1 — introduces new session mode. **No.**
- ❌ Criterion 2 — introduces new validator soft-warn category. **No** (gates via `--cov-fail-under` exit code, not validate.py categories — per ADR 0074 decision 5, mirroring ADR 0068 decision rejecting validate.py integration for bandit).
- ❌ Criterion 3 — introduces new state the boot procedure (or any standing tool) reads. **No** — coverage is per-CI-run, not durably stored. The pre-commit hook does NOT read coverage. The boot procedure does not read coverage. State is CI-internal.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `pyproject.toml` (dep + coverage config), `uv.lock` (regenerated), `.github/workflows/validate.yml` (extended), `.github/PULL_REQUEST_TEMPLATE.md` (extended), ADR 0074, this readiness note = 6 surfaces.

One criterion satisfied (4) → readiness note required.

## Mechanism

A single mechanism landing in CI only:

1. **CI step extension** — `.github/workflows/validate.yml`'s `test` job's pytest step replaces the prior `uv run pytest engine/tools/ --tb=short` with:

   ```bash
   uv run pytest engine/tools/ --tb=short \
     --cov=engine/tools \
     --cov-report=term-missing \
     --cov-report=xml \
     --cov-fail-under=78
   ```

   `--cov-fail-under=78` is the measured baseline (80%) minus 2pp per ADR 0074 decision 3. Coverage's `--fail-under` exits with code 2 (not 1) on threshold breach; pytest-cov inherits. The wrapper's `STATUS != 0` check catches both pytest failure (exit 1) AND coverage failure (exit 2).

   Coverage summary surfaces in `$GITHUB_STEP_SUMMARY` on pass AND fail so PR reviewers see per-module breakdown without scraping logs.

2. **No pre-commit step.** Coverage measurement is per-suite; pre-commit gates per-staged-file or per-targeted-pytest. Composing coverage with the existing pre-commit `validate.py code-gates` phase would require either re-running the full 3:39 suite per commit (intolerable) or partial-coverage-mismeasure on subsets (wrong). CI is the right surface. (ADR 0074 decision 4.)

## Readiness criteria

### Tier 1 — must close this session

- **T1-A — CI step lights up green on the deliverable push.** After deliverables land on `main`, observe GitHub Actions `validate` workflow → `test` job → `Run pytest engine/tools with coverage` step; confirm exit 0 (post-FF). Closes empirically in-session post-FF.
- **T1-B — `--cov-fail-under` empirically fires the gate red.** `uv run coverage report --fail-under=99` against the post-pytest `.coverage` artifact exits with code 2 + emits `Coverage failure: total of 80 is less than fail-under=99` — the threshold gate fires correctly above floor. Closes empirically in-session (no CI dispatch required — coverage's `--fail-under` semantics are upstream of pytest-cov's invocation, so the gate is provably wired regardless of which entrypoint invokes it).

### Tier 2 — settle-in-advance, document, non-blocking

- **First natural coverage-floor breach on `main`.** A future commit lands red on CI with coverage below 78%. Cleanup-session signal per ADR 0065 (engine)'s CI-red surface via `engine/tools/hooks/session-start.sh`. Record the trigger + the fix (restore coverage OR amend the floor per ADR 0074 decision 3).
- **First floor-raise ADR amendment.** When coverage rises sustainedly (e.g., a session adds substantial tests for the low-coverage modules and total rises to 84%+), a future session may amend ADR 0074 to raise the floor (e.g., to 82%). Track the time-to-first-amendment as a posture-holding signal: amendments are deliberate locks, not drive-by adjustments.
- **pytest-cov / coverage version drift.** uv.lock pins exact versions (pytest-cov 7.1.0 + coverage 7.14.0 at S-0136). Major-version bumps may change `--cov-fail-under` semantics OR the `[tool.coverage]` config schema; reviewer regenerates uv.lock + runs full pytest before merging per [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md). Per ADR 0069 + dependency-discipline.md major-version-bump rule, major bumps require an ADR amendment.

### Tier 3 — named-and-deferred forward-pointers

- **Branch coverage.** Currently `branch = false` (line coverage only) per ADR 0074 decision 2. Revisit if line-coverage gate produces too many false-positive passes (e.g., conditional branches with one side never exercised but the surrounding line marked covered).
- **Coverage on `engine/tools/hooks/*.sh`.** Bash; out-of-scope for pytest-cov. Would need `bashcov` or `shellcheck-coverage` if hook complexity warrants — deferred.
- **Coverage on `product/seed-graph/migrations/*.sql`.** SQL; not Python.
- **Coverage on Phase 6+ application code (SwiftUI).** XCTest + xcov (or equivalent) is its own adoption, gated on Phase 9 entry per ADR 0065 product.
- **CI runtime budget composition with bandit (per [ADR 0068](../adr/0068-bandit-sast-pre-commit-and-ci.md) Tier 3 forward-pointer).** Bandit ~2s + pytest with coverage ~3:44 (3:39 pytest + ~5s coverage) = ~3:46 in the test+validate jobs. Well within the 10-minute CI budget per ADR 0065 (engine) decision 4. Re-evaluate at Phase 6 entry when the corpus is larger; if combined runtime crosses 5 minutes, ADR-amendment optimization pass (cache, parallelism, path filters) per ADR 0065.

## Status

- **T1-A — closed at S-0136 (empirically verified).** GitHub Actions run [25753339781](https://github.com/StarshipSuperjam/paideia/actions/runs/25753339781) on push of `9f8ea63` (the S-0136 deliverable batch + `.gitignore`) to `main` concluded `success`. Both jobs — `validate.py` AND `pytest engine/tools` — exit 0. The `Run pytest engine/tools with coverage` step inside the `pytest engine/tools` job exited 0 against the post-S-0136 corpus (coverage 80% ≥ floor 78%, `--cov-fail-under=78` inert). Two non-blocking annotations on the run: (a) Node.js 20 deprecation notice for `actions/checkout@v4` + `astral-sh/setup-uv@v3` — cosmetic, fixed by future action-version bumps; not a soft-warn for this session. (b) GitHub-Actions cache service transient `Failed to save` / `Failed to restore: Cache service responded with 400` — runner installed deps from scratch instead of cache; non-functional impact. Run completed in ~5 min wall clock (cold install path due to cache miss).
- **T1-B — closed at S-0136 (empirically verified via direct gate invocation).** `uv run coverage report --fail-under=78 > /dev/null 2>&1; echo $?` → `0` (gate inert at floor). `uv run coverage report --fail-under=99 > /dev/null 2>&1; echo $?` → `2` (gate fires red; stderr emits `Coverage failure: total of 80 is less than fail-under=99`). The threshold gate semantics are provably wired upstream of pytest-cov's CLI integration — pytest-cov inherits coverage's `--fail-under` exit code as the gate.
  - **Why no CI-dispatch test:** the gate semantics live in coverage's `report` command (read by `--cov-fail-under` in pytest-cov), independent of which entrypoint generates the `.coverage` artifact. Direct invocation against the post-pytest `.coverage` is functionally equivalent to the CI step's gate; the CI step's only addition is generating the `.coverage` artifact in the first place (covered by T1-A).

## Risk surface (deliberate posture)

**Floor-amendment laxity risk.** If amendments are easy, the floor drifts upward unstoppably and becomes aspirational. Mitigation: ADR 0074 decision 3 requires an ADR amendment (or supersession) for any floor change; the amendment must be PR-reviewed; the PR template's coverage-delta checkbox surfaces the change at review time. Posture: amendments are deliberate locks, not drive-by adjustments.

**Coverage gaming risk.** A session under pressure could add trivial tests purely to raise the floor (low-value `assert True` patterns, single-statement smoke tests). Mitigation: the floor is trend-watching, not aspirational (ADR 0074 decision 3) — pressure to *raise* the floor must come from substantive test additions. The persistent-warn-style boot surface that would otherwise pressure a session to raise the floor mid-session does not exist; the floor sits at baseline-2 until the user (or the ADR-amendment author) judges that a raise is warranted.

**Coverage-as-quality-proxy risk.** 80% line coverage does not mean 80% behavioral coverage. Modules with low-quality tests (assertions on side effects without verifying the side effect's semantics; mocking the system under test) can show high coverage without high quality. Mitigation: this gate is a regression-alarm, not a quality measure. The deeper quality surface lives in code review (ADR 0066 PR template's discipline checklist) + ADR-tracked design discipline.

**Untested-on-purpose modules risk.** `probe_repo.py` and `probe_session_dir.py` are at 0% coverage. They are diagnostic probes invoked rarely (typically via shell, not pytest). Mitigation: the cost of writing tests for them is non-zero, and their behavior is shape-verified at every invocation via the probe-itself contract. Acceptable as-is; not in the omit list (so they continue to be measured), but the low coverage is documented in ADR 0074 Empirical record so future sessions know the picture is intentional, not negligence.

**`--cov-fail-under` exit-code discrepancy risk.** Coverage uses exit 2 (not 1) on threshold breach. The CI wrapper's `STATUS != 0` check catches both pytest failure (exit 1) and coverage failure (exit 2). If a future refactor moves to `STATUS == 1` (or similar), coverage failures could escape — mitigation is the existing check shape + a comment in `.github/workflows/validate.yml` naming the exit-2 inheritance.

**Test-suite runtime drift risk.** Current 3:39 pytest runtime. Coverage instrumentation adds ~5s. If the suite grows to 8+ minutes, the 10-minute CI budget tightens. Mitigation: ADR 0065 (engine) decision 4 names the 10-minute budget; ADR 0068 Tier 3 forward-pointer names the combined runtime as a re-evaluation trigger; this readiness note's Tier 3 inherits the trigger.

## Cross-references

- [ADR 0074](../adr/0074-pytest-cov-coverage-floor.md) — the contract.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate itself.
- [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) — pytest-cov pinned in `pyproject.toml` + `uv.lock`.
- [ADR 0065 (engine)](../adr/0065-validate-py-mirror-to-ci.md) — CI mirror (this gate extends the workflow); the pytest step's existing comment naming `#71 pytest-cov` is now honored.
- [ADR 0066](../adr/0066-pr-template-and-branch-protection.md) — PR template (extended with coverage-delta checkbox).
- [ADR 0068](../adr/0068-bandit-sast-pre-commit-and-ci.md) — sister Tier 2 adoption; Tier 3 forward-pointer "Coverage gate composition" honored here.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — refresh procedure for pytest-cov + coverage.
- [`engine/build_readiness/bandit_first_exercise.md`](bandit_first_exercise.md) — shape model for this readiness note.
- [Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) — closes.
