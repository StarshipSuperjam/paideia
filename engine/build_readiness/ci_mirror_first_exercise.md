# CI mirror — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the GitHub Actions CI mirror of `validate.py` landed at S-0131 per [ADR 0065 (engine)](../adr/0065-validate-py-mirror-to-ci.md) (Issue [#68](https://github.com/StarshipSuperjam/paideia/issues/68)).

## Trigger criteria evaluation

Per ADR 0053 the mechanism qualifies for a readiness note when ANY of:

- ❌ Criterion 1 — introduces new session mode. **No.**
- ❌ Criterion 2 — introduces new validator soft-warn category depending on session-side discipline. **No** (CI consumes existing categories; doesn't add).
- ✅ Criterion 3 — introduces new state the boot procedure (or any standing tool) reads. **Yes** — `engine/tools/hooks/session-start.sh` now reads `gh run list --branch main --limit 1 --json conclusion` at every session boot. Although the state lives at GitHub rather than as a tracked state file, the spirit of the criterion is satisfied: a new state surface that the AI must respond to has been introduced into the boot procedure.
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — touches `.github/workflows/validate.yml` (new), `.github/PULL_REQUEST_TEMPLATE.md` (new, co-landed via ADR 0066), `engine/tools/hooks/session-start.sh` (extended), `engine/STATE.md`, `engine/ENGINE_LOG.md`, plus ADR 0065 + ADR 0066 = 7 surfaces.

Two criteria satisfied → readiness note required.

## Mechanism

Three coupled mechanisms in this session:

1. **`.github/workflows/validate.yml`** — two jobs (`validate`, `test`) triggered on `pull_request` to `main` and `push` to `main`. Mirrors the pre-commit invocation pattern: `uv lock --check` (hard-fail in CI per ADR 0065 decision 3) → `uv sync --frozen` → default `validate.py` → `validate.py --code-gates --files <changed>` → `pytest engine/tools/`.
2. **Branch protection on `main` (via `gh api`)** — required status checks `validate.py` + `pytest engine/tools` reference the workflow's job names. `enforce_admins=false` preserves the [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) `routine_lifecycle_push.py` bypass pattern. Configured by ADR 0066.
3. **`session-start.sh` CI-red surface** — reads `gh run list --branch main --limit 1 --json conclusion` at every session boot; emits a LOUD `[session-start] CI RED on main` block when the most recent main-branch run concluded `failure`. The cleanup-session signal for routine-mode pushes that bypass the synchronous CI wait.

## Readiness criteria

- **T1-A — first PR exercises CI green and red.** Author one deliberate-fail PR (e.g., introduce an ADR with a missing Status field, or otherwise trip a hard-fail in `validate.py`) and confirm CI red surfaces in the PR. Revert and confirm CI green. Closes in S-0131.
- **T1-B — first routine-mode lifecycle push to `main` after branch protection lands.** Verify `routine_lifecycle_push.py` succeeds against the protection rule via the admin-bypass path. The empirical hypothesis is that `enforce_admins=false` permits the maintainer's admin-token push to bypass `required_status_checks`. Closes at the next natural routine fire.
- **T1-C — first CI-red on `main` → `session-start.sh` surface fires correctly.** Manually break a downstream commit on `main` (or wait for natural occurrence) and confirm next session boot surfaces the LOUD block. Synthetic test of the surface lands in S-0131 by stubbing `gh run list` output locally; T1-C closes empirically at the first natural red-on-main.

Tier 2 (settle-in-advance, document, non-blocking):

- **10-minute pipeline budget measured on first natural PR.** Per-job `timeout-minutes: 10` is enforced by GitHub; expected runtime ~2.5 minutes cold, ~30s cached. Record at first natural PR.
- **`uv` cache hit-rate measured on second run.** `astral-sh/setup-uv@v3` with `cache-dependency-glob: uv.lock` should produce a hit on the second run of a PR.

Tier 3 (named-and-deferred forward-pointers):

- **Eager-claim `chore(session):` commits do not require PR review.** Routine-pushed eager-claim commits land directly on main via the admin-bypass path. Re-evaluate when CODEOWNERS lands ([#80](https://github.com/StarshipSuperjam/paideia/issues/80) trigger; ≥2 collaborators).
- **Routine-pushed-then-CI-red recovery procedure.** When a routine session pushes red to main, the next session sees the LOUD surface and must adjudicate: fix-in-context if scope-compatible, else open a cleanup-session Issue. Document the procedure once natural occurrence happens.
- **Branch-protection drift detection.** Today, drift between ADR 0066's documented `gh api` invocation and the actual GitHub-side configuration is detectable only by manual round-trip read. If drift becomes a real cost, author a `validate.py` soft-warn that runs `gh api repos/.../branches/main/protection` and diffs against the ADR's documented shape.

## Status

- **T1-A — closed at S-0131.** Verification exercise during this session ran a deliberate-fail commit on the worktree branch + confirmed CI red via `gh run list`, then reverted + confirmed CI green. (See session outcome_summary for exact run URLs.)
- **T1-B — open.** Awaits first routine-mode lifecycle push post-S-0131. The hypothesis is empirically testable but not exercise-able in this interactive session.
- **T1-C — synthetic test closed at S-0131; empirical close awaits first natural red-on-main.**

## Risk surface (deliberate posture)

**Bootstrap risk.** GitHub Actions runners do not have `~/.mempalace/palace`, `SUPABASE_DB_URL`, or any project-credential surface. `validate.py` is expected to produce soft-warns on every CI run (`chromadb_palace_health` exit-1 from `probe_palace.py`; `graph_audit_skipped` from absent `SUPABASE_DB_URL`; plus current-state inheritances `issue_collision`, `missing_rigor_score`, `orphan_leaf`). All collapse to exit-1, which is below the hard-fail threshold. If a future `validate.py` change reclassifies any of these as hard-fail in a CI-applicable context, CI will turn red until the discipline catches up. Mitigation: the persistent-warn boot surface per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) catches drift cross-session.

**Routine-push interaction risk.** `routine_lifecycle_push.py` does not synchronously wait for CI green. The cleanup-session signal is the `session-start.sh` surface. If the surface itself is broken (e.g., `gh` not on the venv PATH at hook fire-time, or the JSON shape changes upstream), routine red-on-main accumulates silently until manual detection. Mitigation: the surface is synthetically tested at S-0131; empirical T1-C tracks the first natural fire.

**Cost-overrun risk.** 10-minute hard cap per job. Currently ~2.5 minutes cold; ~30s cached. If a future Issue (e.g., #71 pytest-cov, #70 bandit) extends the workflow such that runtime crosses 10 minutes, the job hard-fails and an ADR-amendment optimization pass is required per ADR 0065 decision 4. The no-skip philosophy means we don't make CI optional, we make it faster.

**Branch-protection bypass risk.** `enforce_admins=false` means the maintainer can bypass all checks with a direct push. This is intentional — it preserves the routine-mode push pattern. The gap is undisciplined direct pushes from the maintainer's terminal, which the session-build-lifecycle Skill is designed to prevent (all session pushes go through the lifecycle Skill, which runs local pre-commit hooks). Re-evaluate when a second collaborator joins ([#80](https://github.com/StarshipSuperjam/paideia/issues/80)).

## Cross-references

- [ADR 0065 (engine)](../adr/0065-validate-py-mirror-to-ci.md) — the contract.
- [ADR 0066](../adr/0066-pr-template-and-branch-protection.md) — co-landing PR template + branch protection (the protection rule's required status checks ARE this workflow's jobs).
- [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — `routine_lifecycle_push.py`; preserved by `enforce_admins=false`.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate itself.
- [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) — `uv.lock` + `uv sync --frozen` (CI's reproducible install).
- [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68) — closes.
- [Issue #69](https://github.com/StarshipSuperjam/paideia/issues/69) — co-closes (via ADR 0066).
- [Issue #80](https://github.com/StarshipSuperjam/paideia/issues/80) — re-evaluate `enforce_admins=false` when this triggers.
