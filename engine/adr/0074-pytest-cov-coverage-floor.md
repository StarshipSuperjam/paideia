# ADR 0074 — `pytest-cov` coverage reporting with measured floor

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0136

## Context

Pre-S-0136, the engine corpus has 1222 tests across 45 test files (`engine/tools/test_*.py`) covering 38+ production `engine/tools/*.py` modules, but **no coverage measurement.** `pytest engine/tools/` returns binary success/failure; no visibility into what fraction of production code is exercised, no regression alarm when coverage drops.

[Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) named the adoption as Tier 2 of the SWE-hardening rollout. [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) S-0131 explicitly named pytest-cov as the follow-up gated on CI workflow existence (validate.yml's pytest step comment: *"Coverage gating arrives in a follow-up Issue (#71 pytest-cov), gated on this CI workflow per ADR 0065"*). [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) Tier 3 forward-pointer already named "Coverage gate composition with #71 pytest-cov" — the integration shape was anticipated. This ADR honors both pointers.

Phase 6+ code surface will grow fast (the SwiftUI codebase is its own coverage frontier per ADR 0065 product; this ADR scopes to the engine corpus). Without a baseline + floor, coverage silently degrades; with one, regressions surface in CI before they merge.

Pattern source: [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) and the project's existing sister-Tier-2 adoption [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md).

## Decision

Seven coupled choices mechanize the adoption.

### 1. pytest-cov pinned in `pyproject.toml`; venv install via `uv sync`

`pytest-cov>=4.0.0` added to `[project.dependencies]` matching the ruff/mypy/pytest/bandit pattern. `uv.lock` regenerated in the same commit; current resolved version `pytest-cov` 7.1.0 + transitive `coverage` 7.14.0. Refresh discipline per [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md). CI invokes `uv run pytest ... --cov ...` so the gate runs against the lockfile-pinned version, not a maintainer's brew-installed copy.

### 2. Coverage config in `pyproject.toml` `[tool.coverage]`

Chosen pyproject.toml-rooted config over a separate `.coveragerc`. Rationale: the project's existing pattern is config-in-pyproject when possible (ruff, mypy, pytest already live there; bandit is the lone exception because bandit requires YAML). A separate `.coveragerc` would introduce a new dot-file without proportional benefit; the pyproject section keeps tool config discoverable from a single root file.

Initial config:

```toml
[tool.coverage.run]
source = ["engine/tools"]
omit = [
    "engine/tools/test_*.py",          # tests themselves, not the subject
    "engine/tools/_venv_reexec.py",    # exec-replaces; coverage cannot trace
    "engine/tools/conftest.py",        # pytest fixture loader
]
branch = false

[tool.coverage.report]
show_missing = true
skip_covered = false
```

### 3. Floor procedure: floor = baseline - 2pp; moves up only via ADR amendment; never down silently

**Trend-watching, not aspirational.** A coverage drop is a regression alarm requiring discussion; a coverage rise is locked in via an ADR amendment that raises the floor so the new high becomes the new normal. The floor never decreases without explicit ADR amendment naming why.

Measured baseline at S-0136 (this session): **80%** (7115 statements, 1418 missed, 1222 tests passing). Rounded down from the empirical 80.07%.

Chosen floor: **78%** (baseline 80 − 2pp). Baked into `.github/workflows/validate.yml` as `--cov-fail-under=78`. Future amendments to the floor:

1. Author a new ADR amending this one (or supersede this ADR if the floor procedure itself changes).
2. Update `.github/workflows/validate.yml` `--cov-fail-under=<new>` in the same PR.
3. Record the new baseline + new floor in the amending ADR's Empirical record.

Per the user's standing direction `feedback_no_pilot_wait_and_see.md`: the floor lands with measurement, not "we'll set the floor once we see how it behaves."

### 4. CI gate only; no pre-commit coverage step

Pre-commit hooks gate per-staged-file (`bandit` per ADR 0068) or per-fast-targeted-pytest (`validate.py code-gates` phase per ADR 0038). Coverage measurement is per-suite: it requires running the full pytest suite to get accurate totals. Adding coverage to pre-commit would either (a) re-run the full 3.5-minute suite per commit (intolerable latency), or (b) partial-coverage-mismeasure on staged-file pytest subsets (wrong). CI is the right surface — full suite, full coverage, regression alarm at PR + push time. Pre-commit's `validate.py code-gates` continues to run targeted pytest on changed files (per ADR 0038 + ADR 0063) without coverage instrumentation.

### 5. No `validate.py` soft-warn category

pytest-cov gates via coverage's `--fail-under` exit code (exit 2 on threshold breach; pytest-cov inherits). validate.py's soft-warn categories are orthogonal — they live in the `validate.py` invocation's stderr stream, gated separately by `validate.py`'s own exit code logic per ADR 0042. Mixing them would re-implement the gate in two places without defense-in-depth value. Same posture as ADR 0068 decision rejecting validate.py integration for bandit (which gates via bandit's own exit code).

Defense-in-depth lives entirely in the CI surface: `--cov-fail-under` exit code (gate) + `$GITHUB_STEP_SUMMARY` extraction (per-PR visibility) + the persistent-warn boot surface only insofar as future amendments to validate.py reference this gate (none currently planned).

### 6. Exclusion list discipline

`omit` patterns must have an inline comment naming the reason — mirror of the `# nosec`-with-reason discipline from ADR 0068 decision 5 + the dep-justification discipline from ADR 0064 + [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) "Adding a new dependency" step 2. Silent suppressions accumulate and lose meaning. Adding a new omit requires the same-session reason annotation.

Initial omits at S-0136:

- `engine/tools/test_*.py` — tests are the subject's measurement instrument, not the subject.
- `engine/tools/_venv_reexec.py` — `os.execv()` replaces the process; coverage instrumentation cannot trace past the exec, so the file appears uninstrumented regardless of whether the code path ran.
- `engine/tools/conftest.py` — pytest fixture loader; not production code under test.

### 7. PR template extension

`.github/PULL_REQUEST_TEMPLATE.md` Discipline checklist gains a "Coverage delta acknowledged" item (per [ADR 0066](0066-pr-template-and-branch-protection.md)'s checklist pattern). A floor amendment requires an ADR amendment to this ADR plus the corresponding `--cov-fail-under=` update in `.github/workflows/validate.yml`; the PR template's checkbox surfaces the check at human-review time.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

pytest-cov adoption qualifies as cross-cutting and requires a first-exercise readiness gate:

- ❌ Criterion 1 — new session mode. **No.**
- ❌ Criterion 2 — new validator soft-warn category. **No** (gates via `--cov-fail-under` exit code per decision 5).
- ❌ Criterion 3 — new state the boot procedure (or any standing tool) reads. **No** — coverage is per-CI-run, not durably stored; the pre-commit hook does NOT read coverage; the boot procedure does not read coverage. CI-internal state only.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `pyproject.toml` (dep + coverage config), `uv.lock` (regenerated), `.github/workflows/validate.yml` (extended), `.github/PULL_REQUEST_TEMPLATE.md` (extended), this ADR, the readiness note = 6 surfaces.

One criterion satisfied (4) → readiness note required. Authored at [`engine/build_readiness/pytest_cov_first_exercise.md`](../build_readiness/pytest_cov_first_exercise.md).

### Other consequences

- **Positive — regression alarm.** Coverage measurement provides a concrete signal when refactors silently delete test coverage along with code. The floor catches floor-crossing regressions at PR time before they merge.
- **Positive — pairing with [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md).** ADR 0068's Tier 3 forward-pointer ("Coverage gate composition with #71 pytest-cov") is now honored. Both gates live in the same `test` and `validate` jobs of `.github/workflows/validate.yml`; the combined CI runtime grows by ~5s (xml report writing + `--cov-fail-under` evaluation) on top of the existing 3:39 pytest runtime. Well within the 10-minute CI budget per ADR 0065 (engine) decision 4.
- **Positive — visibility surface.** `$GITHUB_STEP_SUMMARY` extraction surfaces per-module coverage in every CI run. A reviewer looking at a PR's checks tab sees what fraction of the corpus is exercised and which modules have the lowest coverage, without spelunking through the log.
- **Cost — uv.lock churn.** Adding pytest-cov pulled in `coverage` v7.14.0 as a transitive (pytest-cov's coverage backend). Lockfile regenerated; 2 new packages in the venv.
- **Cost — CI runtime.** ~5s added to the pytest step (xml report + term-missing + threshold evaluation). Within the 10-minute CI budget per ADR 0065 (engine) decision 4. Composition with bandit (per ADR 0068 Tier 3) keeps the `validate` + `test` jobs well under the cap; re-evaluate at Phase 6 entry when the corpus is larger.
- **Out-of-scope — branch coverage.** Line coverage only (`branch = false`). Branch coverage adds noise without proportional value at this corpus size; revisit if line-coverage produces too many false-positive passes.
- **Out-of-scope — coverage on `engine/tools/hooks/*.sh`.** Bash; pytest-cov is Python-only. Tier 3 deferral; could pursue `bashcov` or `shellcheck-coverage` if hook complexity warrants.
- **Out-of-scope — coverage on `product/seed-graph/migrations/*.sql`.** SQL; not Python.
- **Out-of-scope — aspirational target (e.g., 90% goal).** Trend-watching, not aspirational. The floor is the regression-alarm threshold, not a target to push toward via test-padding.
- **Out-of-scope — Phase 6+ application code (SwiftUI).** XCTest + xcov (or equivalent) is its own adoption, gated on Phase 9 entry per ADR 0065 product.

### Empirical record of S-0136 baseline measurement

`uv run pytest engine/tools/ --cov=engine/tools --cov-report=term-missing` against the post-S-0135 corpus reports:

- **TOTAL: 7115 statements, 1418 missed, 80% coverage** (rounded down from 80.07%).
- **Tests: 1222 passing in 3:39 (219.5s) on the workstation `.venv` baseline.**

Five lowest-coverage production modules (targets for future test-authoring effort, not blockers):

| Module | Stmts | Cover |
|---|---|---|
| `probe_repo.py` | 43 | 0% |
| `probe_session_dir.py` | 58 | 0% |
| `probe_palace.py` | 103 | 20% |
| `mempalace_rebuild_hnsw.py` | 244 | 52% |
| `audit_mempalace_attribution.py` | 381 | 53% |

Five highest-coverage production modules (the floor is well-defended by these — drops here would surface fast):

| Module | Stmts | Cover |
|---|---|---|
| `scrub_env.py` | 10 | 100% |
| `timestamps.py` | 21 | 100% |
| `audit_side_discoveries.py` | 109 | 99% |
| `scan_issue_backlog.py` | 103 | 98% |
| `fetch_structural_reference.py` | 183 | 97% |

`uv run coverage report --fail-under=78` against the same `.coverage` artifact returns exit 0 (gate inert at floor). `uv run coverage report --fail-under=99` returns exit 2 with `Coverage failure: total of 80 is less than fail-under=99` — the gate fires correctly above floor (T1-B closeout evidence in the readiness note).

The chosen floor `78%` admits a 2-percentage-point regression budget — small enough that mass test removal cannot slide under it silently, large enough that a single refactor session shouldn't trip it under normal circumstances.

## See also

- [ADR 0038](0038-three-layer-expression-contract-ai-authored-code.md) — three-layer expression contract; this gate is Layer 2 sibling for the coverage surface.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle (this gate fires via `--cov-fail-under` exit code, not validate.py soft-warn — orthogonal).
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv resolution (pytest-cov invoked via `uv run`).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this adoption qualifies via criterion 4.
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — `pyproject.toml` + `uv.lock` (pytest-cov pinned here; coverage config in pyproject.toml).
- [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) — CI mirror (this gate extends `.github/workflows/validate.yml`'s pytest step; the existing comment naming `#71 pytest-cov` is now honored).
- [ADR 0066](0066-pr-template-and-branch-protection.md) — PR template (extended with coverage-delta checkbox).
- [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) — sister Tier 2 adoption + Tier 3 forward-pointer "Coverage gate composition with #71 pytest-cov" honored here.
- [`engine/build_readiness/pytest_cov_first_exercise.md`](../build_readiness/pytest_cov_first_exercise.md) — first-exercise readiness note.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — dependency-update procedure.
- [Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) — closes.
- Pattern source: `addyosmani/agent-skills` `ci-cd-and-automation`; existing project precedent in ADR 0068.
