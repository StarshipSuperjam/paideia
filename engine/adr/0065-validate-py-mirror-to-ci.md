# ADR 0065 — Mirror `validate.py` gate to GitHub Actions CI

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0131

## Context

Pre-S-0131, [`engine/tools/validate.py`](../tools/validate.py)'s 23 hard-fails and 11 soft-warns ran only at local pre-commit. A clone-without-hooks, a `--no-verify` slip, or a push from any tool that doesn't run hooks lands unguarded code. The repo went OSS (Apache 2.0) and publicly visible at S-0130 per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md), which materially increases the cost of an unprotected `main` — anyone can clone, fork, and contribute, but only local-pre-commit-run code reaches `main` with verification today.

The pre-SWE-hardening audit at session-pre-S-0124 classified CI mirroring as Tier 1, gated only by [Issue #65](https://github.com/StarshipSuperjam/paideia/issues/65) (lockfile, closed at S-0127 per [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md)). Five downstream Issues depend on this workflow existing: [#67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot (needs CI), [#69](https://github.com/StarshipSuperjam/paideia/issues/69) branch protection (must reference CI checks by name), [#70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit SAST (extends this workflow), [#71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov (extends this workflow).

Pattern source: ECC `affaan-m/everything-claude-code` reusable-validate.yml / reusable-test.yml. Judgment patterns: `addyosmani/agent-skills` `ci-cd-and-automation`. Neither adopted verbatim.

## Decision

One workflow file (`.github/workflows/validate.yml`) with two jobs (`validate`, `test`), triggered on `pull_request` to `main` and `push` to `main`. Six coupled choices mechanize the adoption.

### 1. Workflow mirrors pre-commit invocation pattern, not the Issue body's flag spec

Issue #68 specified `python engine/tools/validate.py --repo-structure --staged --code-gates`. Those flags do not exist in the current implementation — `--staged` is not a CLI flag, and `--code-gates` requires `--files`. The workflow substitutes the actual pre-commit pattern from [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit):

1. `uv lock --check` — fail-fast on lockfile drift.
2. `uv sync --frozen` — reproducible install per ADR 0064.
3. Default `validate.py` (no flags) — mirrors pre-commit line 111. Runs all three phases (structural / health-probe / graph-audit) per [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md).
4. `validate.py --code-gates --files <changed-py>` — mirrors pre-commit line 178. Changed-file discovery uses `git diff` against `${{ github.event.pull_request.base.sha }}` (PR) or `HEAD~1` (push).
5. `pytest engine/tools/` — separate `test` job; foundation for [#71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov.

The flag discrepancy is documented here so future readers don't chase phantom flags by re-reading the Issue body.

### 2. Hard-fails fail the job; soft-warns surface but exit 0

Mirrors local pre-commit semantics. The persistent-warn boot surface (per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)) remains the cross-session enforcement layer — failing CI on every soft-warn would collapse the trend signal that the archive canon depends on. Soft-warn detail is written to `$GITHUB_STEP_SUMMARY` so reviewers can see the categories without leaving the PR UI.

Expected CI soft-warns on a clean run today: `chromadb_palace_health` (no `~/.mempalace/palace` on a fresh runner — `probe_palace.py` exits 1 per its contract), `graph_audit_skipped` (no `SUPABASE_DB_URL`), `issue_collision` / `missing_rigor_score` / `orphan_leaf` (inherited from current state). None of these block.

### 3. `uv lock --check` is hard-fail in CI even though it's soft-warn locally

`uv_lock_out_of_date` is soft-warn in local pre-commit (per ADR 0064) because legitimate edits to `pyproject.toml` (comments, name, description) don't always require a relock — `uv lock --check` is the deterministic ground-truth. In CI, drift on a tracked `uv.lock` is unambiguous (CI runs against committed refs only) and a soft-warn in CI is dead surface: no one reviews CI soft-warns the way they review pre-commit ones. The asymmetry is deliberate.

### 4. Pipeline budget: 10 minutes per job

10-minute `timeout-minutes` on both jobs. Per-job concurrency cancellation cancels superseded runs (push-spam to a PR branch doesn't queue). Exceeding 10 minutes triggers an ADR-amendment optimization pass (cache, parallelism, path filters) before any "add another check" work — the no-skip philosophy means we don't make CI optional, we make it faster.

Current measured: setup ~30s + validate.py ~30s + code-gates ~30s + pytest ~60s ≈ 2.5 minutes per job on a cold runner; cache hit cuts setup to ~5s.

### 5. Routine-mode interaction: routine pushes do not wait for CI

[`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py) (per [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md)) pushes directly to `main` via `subprocess.run(['git', 'push', ...])`. The push completes when GitHub accepts the ref update; CI starts asynchronously. The routine session exits without waiting for CI green — waiting synchronously would block routine-mode lifecycle on a remote event the session has no need to gate on.

A red CI run on `main` after a routine push is the cleanup-session signal. The session-start.sh extension authored in this session (see Consequences) reads `gh run list --branch main --limit 1` at every boot and emits a LOUD line when conclusion is `failure`. The next session — interactive or routine — sees the surface and either runs the fix or HANDOFFs.

### 6. Judgment patterns from agent-skills `ci-cd-and-automation`

Baked into this ADR rather than into a separate ops doc — the patterns are short and CI-specific.

- **No-skip philosophy.** No CI check can be locally bypassed. Failed CI = fix the check or fix the code. `--no-verify`-equivalent flags do not exist for this workflow.
- **Flaky-test discipline.** Flaky tests get *fixed*, not retried. No `@pytest.mark.flaky` accepted as steady-state. Forward posture; no flaky tests today.
- **GitHub Secrets posture.** Even test-only credentials live in GitHub Secrets, never in workflow YAML. No credentials used by this workflow today; recorded as forward posture for [#70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit and [#71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov if either grows credential-touching surface.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

CI mirror qualifies as cross-cutting and requires a first-exercise readiness gate:

- ❌ Criterion 1 — new session mode. **No.**
- ❌ Criterion 2 — new validator soft-warn category. **No** (CI consumes existing categories; doesn't add).
- ✅ Criterion 3 — new state the boot procedure reads. **Yes** — `engine/tools/hooks/session-start.sh` now reads `gh run list --branch main --limit 1 --json conclusion` at every boot. Although the data lives at GitHub rather than as a tracked state file, the spirit of the criterion is satisfied: a new state surface that the AI must respond to has been introduced into the boot procedure.
- ✅ Criterion 4 — Consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `.github/workflows/validate.yml` (new), `.github/PULL_REQUEST_TEMPLATE.md` (new, co-landed with ADR 0066), `engine/tools/hooks/session-start.sh` (extended), `engine/STATE.md`, `engine/ENGINE_LOG.md`, plus this ADR and ADR 0066 = 7 surfaces.

Two criteria satisfied (3 + 4). First-exercise readiness note authored at [`engine/build_readiness/ci_mirror_first_exercise.md`](../build_readiness/ci_mirror_first_exercise.md).

### Other consequences

- **Positive — remote enforcement.** Any push to main or PR opens runs the same checks the pre-commit hook runs. Clone-without-hooks lands no longer survive.
- **Positive — downstream unblock.** [#67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot, [#69](https://github.com/StarshipSuperjam/paideia/issues/69) branch protection (co-landing this session), [#70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit, [#71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov all become directly authorable in subsequent sessions.
- **Positive — `session-start.sh` CI-red surface.** Routine sessions that push red to main now leave a readable boot-time signal at the next session. Prior posture (routine session pushes, no signal) silently accumulated breakage.
- **Cost — minutes-per-session CI burn.** Each session produces ≥1 push to main (the eager-claim `chore(session):` commit) + 1 final commit. ~5 minutes total CI per session on cold runners, ~1 minute cached. Acceptable.
- **Cost — soft-warn floor in CI.** Soft-warns visible on every PR clutter `$GITHUB_STEP_SUMMARY`. Mitigation: only the top 50 soft-warn lines are surfaced; full validate output is in the job log.
- **Out-of-scope — coverage gating.** [#71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov is a separate Issue; this workflow runs pytest without coverage measurement.
- **Out-of-scope — SAST.** [#70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit (Pairing A with [#66](https://github.com/StarshipSuperjam/paideia/issues/66)) extends this workflow with a `bandit` step.
- **Out-of-scope — secret scanning in CI.** [#66](https://github.com/StarshipSuperjam/paideia/issues/66) gitleaks pre-commit + GitHub-native secret scanning land separately.
- **Out-of-scope — re-evaluating ADR 0064's lockfile-staleness soft-warn category.** Local pre-commit keeps the soft-warn shape per ADR 0064; CI overrides to hard-fail per decision 3 above. The soft-warn category is unchanged.

## See also

- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle (the persistent-warn surface that CI deliberately preserves by exit-0-on-soft-warn).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate (this adoption qualifies; readiness note required).
- [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — `routine_lifecycle_push.py` interaction (routine pushes don't wait for CI; cleanup-session signal lives in `session-start.sh`).
- [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — validator phase model (the three phases CI runs).
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — lockfile (CI's `uv sync --frozen` consumes it; `uv lock --check` hard-fails on drift per decision 3).
- [ADR 0066](0066-pr-template-and-branch-protection.md) — co-landing PR template + branch protection (this CI workflow's checks are the required status checks for the protection rule).
- [`engine/build_readiness/ci_mirror_first_exercise.md`](../build_readiness/ci_mirror_first_exercise.md) — first-exercise readiness note.
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — Layer 1 ops doc; the pre-commit contract this workflow mirrors.
- [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68) — closes.
- [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67), [#69](https://github.com/StarshipSuperjam/paideia/issues/69), [#70](https://github.com/StarshipSuperjam/paideia/issues/70), [#71](https://github.com/StarshipSuperjam/paideia/issues/71) — downstream SWE-hardening Issues unblocked.
- Pattern source: `affaan-m/everything-claude-code` reusable workflows; `addyosmani/agent-skills` `ci-cd-and-automation` judgment patterns.
