# ADR 0068 — `bandit` SAST in pre-commit + CI

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0132

## Context

Pre-S-0132, the engine corpus has `ruff` (lint) and `mypy --strict` (type) gates as part of the code-discipline stack per [ADR 0038](0038-three-layer-expression-contract-ai-authored-code.md). Both catch style/type-shape issues. Neither catches semantic vulnerabilities: `eval(user_input)`, `subprocess(shell=True, ...)` with non-literal command, hardcoded passwords, weak `random` use for security tokens, use of `pickle.load` on untrusted data, etc. Bandit is the Python-ecosystem standard SAST scanner for these classes.

[Issue #70](https://github.com/StarshipSuperjam/paideia/issues/70) named the adoption as Tier 2 of the SWE-hardening rollout; Pairing A bundles this with [Issue #66](https://github.com/StarshipSuperjam/paideia/issues/66) gitleaks per the rollout table in `engine/STATE.md` because both extend the pre-commit hook + tooling config + add a first-exercise readiness note. Pairing A unblocks once Issue #65 lockfile (closed at S-0127 per ADR 0064) and Issue #68 CI mirror (closed at S-0131 per ADR 0065 engine) are in. Both are in.

Pre-Phase-6 the engine corpus is internal tooling, but `engine/tools/` runs against the Supabase pooler via `psycopg` calls, fetches HTTP from third-party structural references via `urllib`, and shells out to `gh`/`git`/`uv`/`mempalace` via `subprocess`. A future regression that adds `eval()` to a config-parser, or `subprocess(shell=True, cmd_from_user)` to a CLI tool, would be undetected by ruff/mypy and would only surface in code review. Bandit makes the gap mechanical.

Pattern source: [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `ci-cd-and-automation` (judgment patterns) and `affaan-m/everything-claude-code` (config-shape).

## Decision

Two layers landing in the same session per Pairing A: pre-commit (staged Python files, hard-fail) + CI (full-tree on `engine/` + `product/seed-graph/`, hard-fail). Five coupled choices mechanize the adoption.

### 1. Bandit pinned in `pyproject.toml`; venv install via `uv sync`

`bandit>=1.7.0` added to `[project.dependencies]` matching the ruff/mypy/pytest pattern. `uv.lock` regenerated in the same commit; current resolved version 1.9.4. Refresh discipline per [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md). Pre-commit hook + CI invoke `uv run bandit ...` so the gate runs against the lockfile-pinned version, not a maintainer's brew-installed copy.

### 2. Pre-commit step: staged Python files, hard-fail

The pre-commit hook (`engine/tools/hooks/pre-commit`) gains a new step between the gitleaks step (authored in the same session per ADR 0067) and the code-discipline gates. Invocation:

```bash
uv run bandit -c engine/tools/bandit.yaml -ll -ii -q <STAGED_PY_FILES>
```

- `-c engine/tools/bandit.yaml` — project config (skip B101 globally; see decision 3).
- `-ll -ii` — gate threshold (medium-severity / medium-confidence floor; see decision 4).
- `-q` — quiet mode, required for bandit to exit non-zero on findings (without `-q`, bandit prints findings to stdout but exits 0; with `-q` the exit code reflects gate status).
- `<STAGED_PY_FILES>` — list of staged Python files under `engine/` discovered via `git diff --cached --diff-filter=ACMR`.

If no Python files are staged, the step is a silent no-op. Hard-fail on findings.

### 3. Config skips B101 globally (pytest convention)

`engine/tools/bandit.yaml` sets `skips: [B101]`. B101 (`assert_used`) fires on every `assert` statement because asserts can be stripped under `python -O`. The engine corpus is not run under `-O` (per `.python-version` 3.12 + `uv sync`-managed install; no `-O` invocation anywhere in the pre-commit, CI, or session apparatus). Pytest itself uses asserts pervasively as the standard assertion mechanism — keeping B101 active produces 2313 false-positive findings (single largest category in the S-0132 baseline) and drowns the actionable signal. Skip is documented in the config inline with rationale per the no-silent-suppressions discipline (decision 4).

`assert_used.skips` additionally exempts `**/test_*.py` and `**/*_test.py` as defense-in-depth in case the global skip is overridden in a future config edit.

### 4. Gate threshold: medium-severity AND medium-confidence; below-threshold findings informational only

CLI flags `-ll -ii` set the gate at MEDIUM+ severity AND MEDIUM+ confidence. Below-threshold findings (LOW severity OR LOW confidence) are not gating but remain visible in bandit's report. Rationale:

- **B404 (`import subprocess`):** flagged as LOW for any module that imports subprocess. The engine corpus imports subprocess in ~15 tools to shell out to `gh`/`git`/`uv`/`mempalace` with static arg lists; the pattern is intentional.
- **B603 (`subprocess_without_shell_equals_true`):** flagged as LOW for `subprocess.run(["gh", ...])` and similar list-form calls. `shell=False` is the default; the calls are not user-input-driven; the LOW severity reflects bandit's heuristic that explicit `shell=False` would be marginally clearer. Not a real risk.
- **B607 (`start_process_with_partial_path`):** flagged as LOW for `subprocess.run(["gh", ...])` (partial path resolved via PATH). The engine tools resolve `gh`, `git`, `uv`, `mempalace` via PATH deliberately — ADR 0050 venv resolution + `scrub_env.sh` PATH prepend.

Each of B404, B603, B607 fires hundreds of times in the engine corpus. Gating at LOW would either require silent-suppression of these tests entirely (rejected per decision 5) or annotating every call site with `# nosec` (refused as drive-by noise without real risk). The MEDIUM+ threshold gates the actionable classes (B608 SQL string construction, B310 urlopen scheme allowance, B108 hardcoded tmp paths, B307 use_of_eval, B306 use_of_mktemp, etc.) — these ARE worth blocking on.

For genuinely actionable below-threshold findings, the path is to fix in code (preferred) or annotate inline. Severity-threshold gating is not a permanent ceiling.

### 5. Rule-skip discipline: inline `# nosec BXXX  # reason`; no blanket allowlists

Per the feedback memory "Default to fix-in-context" + plan-approved S-0132 scope: when bandit's first run against the engine corpus surfaced 20 MEDIUM-severity findings, each was triaged individually. 19 carry inline `# nosec BXXX  # <reason>` annotations naming the false-positive class (placeholder-string construction for B608, scheme-allowlist for B310, test-fixture strings for B108). 1 was filtered out by the MEDIUM-confidence threshold (B608 with LOW confidence on test_apply_migration.py's f-string-writing-SQL-fixture pattern — bandit flags it but at LOW confidence because the f-string is a test fixture write, not a query construction).

**No blanket baseline file.** `bandit --baseline` produces a file that any future finding falls outside — well-suited for retrofitting on legacy code, ill-suited for an engine corpus where new findings should surface for adjudication. The inline `# nosec` discipline keeps each suppression auditable in git blame.

**Adding a new `# nosec` requires the same-session inline comment naming the reason.** Silent suppressions accumulate and lose meaning. Same posture as gitleaks' allowlist discipline per ADR 0067 decision 3 + the future `# nosec BXXX` review by reviewer attention.

### 6. CI extension: full-tree scan on `engine/` + `product/seed-graph/`

`.github/workflows/validate.yml`'s `validate.py` job gains a new step after the existing `Run validate.py --code-gates on changed engine/*.py` step:

```yaml
- name: Run bandit SAST on engine/ + product/seed-graph/
  run: |
    uv run bandit -r engine/ product/seed-graph/ -c engine/tools/bandit.yaml -ll -ii -q
```

Full-tree scan (not staged-only) is the CI-side defense-in-depth complement to the pre-commit's staged-file fast-fail. A change merged via the web UI or a clone-without-hooks would bypass the local gate; CI catches it.

Adding the step in the existing `validate.py` job (rather than as a third job) keeps the 10-minute pipeline budget (per ADR 0065 decision 4) — bandit runs in <2s against the current corpus + product/seed-graph/ has no Python files yet (Phase 5 seeds are SQL).

### 7. Bandit divergence from gitleaks: bandit IS in CI; gitleaks ISN'T

Per ADR 0067 decision 5, gitleaks does not gain a CI step because GitHub-native secret scanning provides the server-side defense. Bandit takes the opposite stance because GitHub has no SAST-equivalent server-side scan — adding bandit to CI is the only way to get full-tree coverage of insecure-pattern code.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

Bandit adoption qualifies as cross-cutting and requires a first-exercise readiness gate:

- ❌ Criterion 1 — new session mode. **No.**
- ❌ Criterion 2 — new validator soft-warn category. **No** (bandit gates via its own exit code, not validate.py categories).
- ✅ Criterion 3 — new state the boot procedure (or any standing tool) reads. **Yes** — every commit now runs `bandit` as a hard-fail gate via the pre-commit hook; the venv must contain bandit 1.9.4 (or later compatible). The pre-commit hook surfaces an actionable `uv sync` error if bandit is missing.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `engine/tools/hooks/pre-commit` (extended), `engine/tools/bandit.yaml` (new), `.github/workflows/validate.yml` (extended), `pyproject.toml` (bandit dep added), `uv.lock` (regenerated), 6 production-tool files + 4 test files with `# nosec` annotations or refactor for nosec placement = >10 surfaces.

Two criteria satisfied (3 + 4) → readiness note required. Authored at [`engine/build_readiness/bandit_first_exercise.md`](../build_readiness/bandit_first_exercise.md).

### Other consequences

- **Positive — semantic-vulnerability gate.** `eval()`, `subprocess(shell=True, dynamic)`, `pickle.load(untrusted)`, `hashlib.md5(password)`, etc. now hard-fail at pre-commit and CI. The engine corpus is small enough that the gate is a meaningful regression-prevention layer.
- **Positive — pairing with [ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md).** Defense-in-depth: gitleaks catches *committed secrets*; bandit catches *insecure-pattern code* that creates exploit-class antipatterns. Both extend the same pre-commit hook; both pair-land in S-0132.
- **Positive — CI server-side defense.** Push-to-main via web UI or a clone-without-hooks runs the full-tree scan. Local-only gates leave a gap; CI closes it.
- **Cost — uv.lock churn.** Adding bandit pulled in `stevedore` as a transitive (extension framework bandit uses for plugin loading). Lockfile regenerated; ~2 new packages in the venv.
- **Cost — refactor for nosec placement.** Three production-tool functions (`audit_mempalace_attribution.attribute_drawer_metadata`, `mempalace_rebuild_hnsw.fetch_metadata_rows`, three call sites in `prune_mempalace`) were refactored to extract their SQL into a named `sql = ...` variable so the `# nosec B608` annotation lives on the line bandit flags. Pre-S-0132 the SQL was inline-passed to `conn.execute(f"...", args)`. The refactor is shape-preserving (same args, same return shape, same test surface — 241 tests pass post-refactor) and arguably more readable (separates query construction from execution).
- **Cost — pre-commit time impact.** Bandit's staged-file scan adds ~100ms; full-tree CI scan ~2s. Within the 10-minute CI budget; not noticeable in local pre-commit.
- **Out-of-scope — `bandit-baseline` integration.** No baseline file; the inline `# nosec` discipline is the auditable substitute.
- **Out-of-scope — extending to `app/` / iOS native code.** Bandit is Python-only; Swift-side static analysis (SwiftLint security rules, Periphery) would be its own adoption, gated on Phase 9 entry per ADR 0065 product.
- **Out-of-scope — bandit's auto-fix or batch-skip via path patterns.** Inline `# nosec` is the project's discipline.

### Empirical record of S-0132 baseline triage

Pre-S-0132 `uv run bandit -r engine/` reported 2577 findings total: 2557 LOW (2313 B101 assert_used + 102 B603 subprocess + 87 B607 partial_path + 48 B404 import subprocess + 5 B112 + 1 B606 + 1 B110), 20 MEDIUM (7 B608 SQL string construction + 2 B310 urlopen + 11 B108 hardcoded /tmp), 0 HIGH.

Post-S-0132 baseline:
- B101 globally skipped (pytest convention).
- LOW-severity findings filtered by `-ll` threshold (B404, B603, B607, B112, B606, B110 surface in `bandit` output without `-l` flag but do not gate).
- 19 of 20 MEDIUM findings annotated with `# nosec BXXX  # reason`. 1 finding filtered by `-ii` confidence threshold.

`uv run bandit -r engine/ -c engine/tools/bandit.yaml -ll -ii -q` returns exit 0 — clean at gate threshold. Synthetic test against a scratch `eval(user_input)` confirms the gate fires on B307 (HIGH/HIGH) and exits 1.

## See also

- [ADR 0038](0038-three-layer-expression-contract-ai-authored-code.md) — three-layer expression contract; this gate is Layer 2 sibling for the SAST surface.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle (bandit findings gate via exit code, not validate.py soft-warn — orthogonal).
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv resolution (bandit invoked via `uv run`).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this adoption qualifies.
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — `pyproject.toml` + `uv.lock` (bandit pinned here).
- [ADR 0083 (engine)](0083-validate-py-mirror-to-ci.md) — CI mirror (this ADR extends `.github/workflows/validate.yml`).
- [ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md) — Pairing A sibling (gitleaks secret scanning).
- [`engine/build_readiness/bandit_first_exercise.md`](../build_readiness/bandit_first_exercise.md) — first-exercise readiness note.
- [`engine/tools/bandit.yaml`](../tools/bandit.yaml) — config file.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — dependency-update procedure.
- [Issue #70](https://github.com/StarshipSuperjam/paideia/issues/70) — closes.
- Pattern source: `addyosmani/agent-skills` `ci-cd-and-automation`; `affaan-m/everything-claude-code` (config shape).
