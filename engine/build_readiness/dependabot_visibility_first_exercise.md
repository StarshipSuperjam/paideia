# dependabot visibility + version telemetry — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. [ADR 0080](../adr/0080-boot-time-dependency-version-visibility.md) criteria evaluation: Criterion 2 (new validator soft-warn `dependabot_pr_stale`) ✅ + Criterion 3 (new state read at boot — `gh pr list` for Dependabot PRs) ✅. Two criteria satisfied → readiness note required.

## Tier 1 — close in-session (S-0147, the session shipping ADR 0080)

Three Tier 1 criteria close at S-0147:

- **T1-A — boot-time version telemetry surface fires.** `engine/tools/probe_versions.py` invoked from `session-start.sh` emits a line of the form `[session-start] Versions: python=3.12.13 chromadb=1.5.9 mempalace=3.3.5 venv=<path> (worktree-local|main-repo)`. Verified at S-0147 boot in worktree `cool-wilbur-b54023`. Recorded in S-0147 `outcome_summary`.

- **T1-B — boot-time Dependabot PR surface fires (LOUD mode).** `engine/tools/scan_dependabot_prs.py` invoked from `session-start.sh` emits the LOUD attention block listing each of the 11 open Dependabot PRs (#94–#105) with age + mergeable status + next-action hint. Verified at S-0147 boot — mode `loud` because count (11) ≥ `LOUD_COUNT_THRESHOLD` (5).

- **T1-C — validator soft-warn `dependabot_pr_stale` is reachable.** `validate.py` invocation in the `health_probe` phase consults the scanner. Verified via `--simulate-age 10` injection that the soft-warn fires correctly for stale PRs; verified at S-0147 boot that the soft-warn does NOT fire (no stale PRs — all 11 are 1 day old).

The natural progression from T1-A→T1-C to a "real" first-exercise is the Phase B 11-PR triage in this same session. Phase B exercises:

- The next-action-hint procedure (per-PR: `gh pr checkout`, `uv lock`, `uv sync`, push, merge).
- The major-bump ADR-review posture per ADR 0069 (each pip PR is a major bump).
- The github-actions PR procedure (PR #95 + #98).
- The persistent-warn surface decay (boot LOUD goes to FYI → quiet as PRs land).

Phase B closeout is captured in S-0147's `outcome_summary` and updated here.

## Tier 2 — close on next natural occasions

- **First natural stale-PR fire.** When a future Dependabot PR is open ≥ 7 days, the LOUD path fires with `STALE` markers and the validator soft-warn fires per stale PR. Record in the surfacing session's `outcome_summary`.

- **First persistent-warn 3-of-5 fire for `dependabot_pr_stale`.** If `dependabot_pr_stale` fires in 3+ of 5 consecutive archives, the boot-time persistent-warn surface escalates per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). Record the response: process the backlog, or adjust policy (raise the cadence, change the threshold via an ADR amendment).

- **First MISCONFIGURED label fire.** When `probe_versions.py` detects `sys.prefix` not matching either expected `.venv/` path, the LOUD `(LIKELY MISCONFIGURED — scrub_env.sh did not source; system Python won)` marker fires. Record the recovery (`uv sync` typically; the marker is informational, not blocking).

## Tier 3 — defer indefinitely (recorded for future audit)

- **Performance budget.** D2 adds one `gh pr list` HTTP roundtrip per boot (~200–500ms). Comparable to existing `scan_issue_backlog.py` cost. Re-audit if boot-time noticeably regresses.

- **gh-failure resilience.** Both `probe_versions.py` and `scan_dependabot_prs.py` are best-effort (graceful failure → stderr log + boot proceeds). The validator's `dependabot_pr_stale` also no-ops on gh failure. The version probe no-ops on import failure. No proactive defense beyond the existing pattern.

- **Combined-tool refactor.** ADR 0080's Alternatives Considered names "combined version-and-PR scanner" as rejected. Re-evaluate if maintenance burden across the two tools shows actual drift; trigger: 2+ instances of "fixed in one tool, missed in the other."

## Empirical record

### S-0147 (the session that authored ADR 0080 + the mechanism) — 2026-05-13

**T1-A — version telemetry surface verified GREEN.** Boot-time run in worktree `cool-wilbur-b54023` emitted `[session-start] Versions: python=3.12.13 chromadb=1.5.9 mempalace=3.3.5 venv=.../.venv (main-repo)` immediately after `scrub_env.sh` source. The MISCONFIGURED branch was empirically verified via direct invocation under system `python3` (Python 3.9.6; chromadb 1.4.1; mempalace 3.3.3) — surface correctly emitted `(LIKELY MISCONFIGURED — scrub_env.sh did not source; system Python won)`. Also surfaced live drift: the worktree had no local `.venv` at session start, then `uv run pytest` auto-created `.claude/worktrees/cool-wilbur-b54023/.venv/`; the next boot's surface correctly switched the classification from `main-repo` to `worktree-local`, validating the resolver-decision visibility this mechanism was built for.

**T1-B — Dependabot PR LOUD boot surface verified GREEN.** With 11 PRs open at S-0147 boot, `scan_dependabot_prs.py` emitted the multi-line attention block in mode `loud` (count 11 ≥ 5). Each PR listed with age (`1d`), mergeable status (`MERGEABLE` post-rebase; `UNKNOWN` initially), and next-action hint discriminated correctly: pip major bumps → "major bump — verify ADR 0069 contract; regenerate uv.lock"; github-actions PRs → "verify action release notes; merge". `--simulate-age 10` injection verified the LOUD `STALE` per-PR marker.

**T1-C — `dependabot_pr_stale` validator soft-warn verified GREEN.** `validate.py` boot pass against the live state showed `dependabot_pr_stale: 0` (correctly — all 11 PRs were 1 day old, below the 7d threshold). 7 pytests against the validator's `_scanner_module` injection point cover no-PRs / gh-missing / fresh / stale / boundary / multiple-stale.

**Phase B — 11-PR triage as first natural exercise of the mechanism (GREEN).** All 11 Dependabot PRs (#94–#105) merged sequentially during S-0147. Pattern per PR: `gh pr checkout` → `git rebase origin/main` → `uv lock` (or skip for github-actions PRs) → `git commit --amend --no-edit` → `git push --force-with-lease` → `gh pr checks --watch` until green → `gh pr merge --squash --delete-branch`. CI green on every PR (validate.py + pytest engine/tools); no smoke-test surfaced any contract change. The installed transitive resolution predated the floor bumps in 10 of 11 cases (reportlab was the lone outlier — uv lock moved 4.5.0→4.5.1 to satisfy the new floor); the bumps tightened the floor pins to reality. The mechanism's purpose was vindicated empirically: 11 PRs that had been invisible to every pre-S-0147 boot were surfaced loudly and processed within one session.

**Tier 2 forward-pointers remain pending** (first natural stale-PR fire; first persistent-warn 3-of-5 escalation; first natural MISCONFIGURED fire post-session). The Tier 1 closeout above empirically validates the mechanism; Tier 2 firings will accumulate as the project continues to receive Dependabot's weekly PR cadence.
