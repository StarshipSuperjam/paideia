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

T1-A through T1-C closeouts recorded here as the mechanism is exercised. Phase B 11-PR triage runs immediately after Phase A commit + push, and updates this record at session close.
