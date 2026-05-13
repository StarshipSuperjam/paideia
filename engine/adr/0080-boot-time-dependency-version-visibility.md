# ADR 0080 — Boot-time dependency version visibility + stale Dependabot PR surface

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0147

## Context

The S-0144→S-0146 MemPalace troubleshooting arc surfaced two distinct invisibility gaps that compounded into version confusion at debug time:

**Gap 1 — Dependabot PRs have no escalation surface after adoption.** [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (S-0133) adopted Dependabot with the explicit "user merges" posture and "First-PR-arrival verification (pending)" empirical-record line. By S-0147, 11 Dependabot PRs (#94–#105, all major-version bumps Dependabot's `pip-minor-and-patch` group correctly does not bundle per [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) decision 3) have accumulated, and ADR 0069's empirical record is still "pending" — no session has updated it since adoption. The boot surface counts Issues via [`scan_issue_backlog.py`](../tools/scan_issue_backlog.py) per [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md), but never queries `gh pr list`. A Dependabot PR can sit indefinitely without any session ever seeing it; the "user merges" posture has no enforcement, no reminder, no escalation path.

**Gap 2 — AI cannot verify which Python + chromadb + mempalace versions it's actually running.** [ADR 0050](0050-project-venv-and-hook-path-wiring.md) pins the venv stack via `scrub_env.sh`'s PATH wiring (worktree-local `.venv/` → main-repo `.venv/` → silent no-op). The wiring is opaque without a visibility surface. Confirmed live drift at S-0147 boot in worktree `cool-wilbur-b54023`:

| Resolver | Python | chromadb | mempalace |
|---|---|---|---|
| Main venv | 3.12.13 | 1.5.9 | 3.3.5 |
| System Python | 3.9.6 | 1.4.1 | 3.3.3 |

When a sub-shell, hook subprocess, or worktree without `scrub_env.sh` sourced resolves through system Python, the AI silently gets stale versions and misdiagnoses. The S-0146 `mempalace_diary_write -32000` debugging exercise spent measurable effort on "is this 3.3.5-specific or 3.3.3-residual?" — the answer would have been an immediate fact-anchor with version telemetry at boot.

The two gaps share a structural cause: information that distinguishes "what versions am I running" + "what's blocking dependency hygiene" is recoverable on demand but invisible by default. The boot surface is the natural carrier for both.

## Decision

Author three coordinated mechanisms that surface both gaps at every session boot.

### 1. Boot-time version telemetry via `engine/tools/probe_versions.py`

A small Python tool emits one line at boot showing the active venv's Python + chromadb + mempalace versions plus which resolver won (worktree-local, main-repo, or MISCONFIGURED). Wired into [`session-start.sh`](../tools/hooks/session-start.sh) immediately after `scrub_env.sh` is sourced and the logging functions are defined.

Shape:

```
[session-start] Versions: python=3.12.13 chromadb=1.5.9 mempalace=3.3.5 venv=<path> (worktree-local|main-repo|MISCONFIGURED)
```

The `MISCONFIGURED` label fires when `sys.prefix` matches neither expected `.venv/` path; the inline marker `(LIKELY MISCONFIGURED — scrub_env.sh did not source; system Python won)` makes the failure mode unmistakable. The probe never installs or repairs — it surfaces facts. Recovery is the user's `uv sync` step.

Best-effort discipline (per [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md)'s gh-failure pattern): missing `python3` or missing tool file emits a stderr log via the existing `log_fail` helper and the hook proceeds. Always exits 0.

### 2. Boot-time Dependabot PR surface via `engine/tools/scan_dependabot_prs.py`

Sibling to [`scan_issue_backlog.py`](../tools/scan_issue_backlog.py). Wraps `gh pr list --author "app/dependabot" --state open --json number,createdAt,title,mergeable,headRefName`. Three modes by count + age:

- **Quiet** (0 PRs): no output line.
- **FYI** (1–4 PRs, all <7 days): single-line FYI naming count + oldest age.
- **LOUD** (≥5 PRs OR any ≥7 days): multi-line attention block listing each PR with age, mergeable status, and a one-line next-action hint (per `next_action_hint` — `github-actions` PRs → "verify action release notes; merge"; pip minor/patch → "regenerate uv.lock and merge"; pip major → "major bump — verify ADR 0069 contract; regenerate uv.lock").

Threshold rationale (7 days): one full Dependabot weekly cadence per [`.github/dependabot.yml`](../../.github/dependabot.yml). A PR uncrossed across one Monday refresh is stale by definition. The LOUD-count threshold (5) trips on volume before age — five fresh PRs is still review pressure worth surfacing.

Wired into [`session-start.sh`](../tools/hooks/session-start.sh) immediately after the issue-backlog scan. Same best-effort discipline: gh failure emits stderr log; hook proceeds.

### 3. Validator soft-warn `dependabot_pr_stale` in `validate.py`

Per-PR soft-warn for any open Dependabot PR aged ≥ 7 days. Lives in [`validate.py`](../tools/validate.py) in the `health_probe` phase per [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md)'s four-phase model (alongside `validate_uv_lock_freshness` — both shell out to external tools). Imports `scan_dependabot_prs` lazily for the fetch + age + hint helpers, keeping the validator and the boot-surface tool sharing one source-of-truth for those functions.

Soft-warn (not hard-fail) because (a) the project's posture is "user merges" not "block on review pressure" and (b) network failures (`gh pr list` timeout) should not block commits. The soft-warn lands in `outcome_summary_soft_warns` so the persistent-warn 3-of-5 surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) escalates when stale PRs accumulate across sessions — turning a one-session lapse into a multi-session-visible signal.

### 4. Operations-doc surface in `dependency-discipline.md`

New subsection "Stale Dependabot PR handling" in [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) names the 7-day threshold, the boot surfaces (D2 + D3), and the two valid responses on encountering stale PRs: (a) process the PR (regenerate uv.lock, merge); or (b) close-with-justification (the dep should not bump). The third valid response — file a follow-up Issue and defer — is also named, for the case where a single session genuinely cannot triage 11 backlogged PRs.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

- ❌ Criterion 1 — new session mode. **No.**
- ✅ Criterion 2 — new validator soft-warn category. **Yes — `dependabot_pr_stale`.**
- ✅ Criterion 3 — new state the boot procedure reads. **Yes — `gh pr list` for Dependabot PRs; the version-probe surface reads sys.prefix + module imports.**
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. Touches `dependency-discipline.md` + `tools-validate-interpretation.md` (2 ops docs); `probe_versions.py` + `scan_dependabot_prs.py` + `validate.py` + `session-start.sh` (4 tooling files). Under the threshold on both axes.

Criteria 2 + 3 satisfied → **first-exercise readiness note required.** Authored at [`engine/build_readiness/dependabot_visibility_first_exercise.md`](../build_readiness/dependabot_visibility_first_exercise.md). T1-A (first natural exercise) closes in-session at S-0147 via the Phase B 11-PR triage that exercises the LOUD path, the next-action-hint procedure, and the validator soft-warn against simulated-age input.

### Other consequences

- **Positive — version drift is no longer silent.** Every session boot publishes the active venv's chromadb/mempalace/Python versions; an AI debugging a MemPalace cold-start has the exact version in transcript-recoverable form at turn 1 instead of inferring from `which mempalace` later. The MISCONFIGURED label catches the silent-system-Python case directly.
- **Positive — Dependabot PRs have an escalation gradient.** Fresh + few → FYI; fresh + many → LOUD; stale at any count → LOUD + per-PR detail. The persistent-warn 3-of-5 surface escalates further if PRs sit across sessions. The "user merges" posture stays; the gradient just makes lapses visible.
- **Positive — the two surfaces share idiom with existing boot output.** `scan_issue_backlog.py`'s shape (FYI line / LOUD block) and `validate_uv_lock_freshness`'s shape (soft-warn category in health_probe phase) are the templates. AI and human reviewers reading boot output don't learn a new pattern.
- **Cost — boot-surface density.** Two new lines (Versions + Dependabot FYI) plus a potential LOUD block. The LOUD case is informational pressure, not error; the AI should triage during a session, not at boot, but the surface must be readable. Mitigation: quiet mode for 0 Dependabot PRs (no line); single-line FYI for the common case (1–4 fresh); LOUD only when count or age says action is overdue.
- **Cost — additional `gh` call per boot.** `scan_dependabot_prs.py` queries `gh pr list` (one HTTP roundtrip). Adds ~200–500ms to boot. Acceptable: comparable to the existing `scan_issue_backlog.py` call. Both are bounded by the gh client's own timeouts and the network state.
- **Cost — `dependabot_pr_stale` soft-warn could persist if PRs accumulate.** A session that boots with 11 stale PRs and doesn't triage them carries 11 soft-warns into `outcome_summary` and (eventually) into the persistent-warn surface. This is the *intended* signal: the surface fires until the PRs land. The annotation in `tools-validate-interpretation.md` documents the legitimate response (process PRs; not "suppress the warn").
- **Out-of-scope — auto-merge for Dependabot.** Explicitly rejected at S-0133 per ADR 0069. Re-considering would require a separate ADR; not in scope here.
- **Out-of-scope — extending the surface to non-Dependabot PRs.** This mechanism scopes to Dependabot authorship specifically. Human PR review pressure is a different problem with different ergonomics; not bundled here.
- **Out-of-scope — auto-rebase or lockfile-regen automation.** `routine_lifecycle_push.py` / `apply_migration.py`-style automation that regenerates `uv.lock` on a Dependabot PR branch and pushes is deferred. The mechanism's value is *visibility*, not automation; the reviewer doing `uv lock && uv sync` remains the human-in-the-loop step.

## Alternatives Considered

Per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

### Amend ADR 0069 in place (no new ADR)

What: Treat the boot surfaces as part of the original Dependabot adoption decision; rewrite the relevant Consequences sub-bullets in declarative present-truth form per ADR 0062, no new ADR.

Pros: Single ADR for the Dependabot surface; future readers see the full mechanism in one place.

Cons: ADR 0069's named decision was specifically "adopt Dependabot with weekly cadence + grouping + manual merge." The boot-surface mechanism is a *new* decision (with its own alternatives — see below) that builds on but doesn't subsume the original. Folding the new decision into the original ADR loses the second decision's deliberation record. ADR 0069's own "First-PR-arrival verification" empirical-record line gets its expected S-0147 update; the new mechanism gets its own ADR.

Rejected because: The mechanism has its own four-criteria evaluation (two satisfied vs ADR 0069's zero), its own first-exercise readiness gate, its own alternatives surface. Conflating those deliberations into ADR 0069's record obscures both.

### Stop at the boot surface; no validator soft-warn

What: Author `scan_dependabot_prs.py` (D2) + version telemetry (D1) but no `dependabot_pr_stale` soft-warn (skip D3).

Pros: Smaller mechanism; one boot line per surface; nothing in `outcome_summary` to track across sessions.

Cons: A boot surface fires once and is gone. A session that ignores the boot LOUD has no other reminder; the next boot fires the same LOUD; the user-or-AI iteration loop is "see LOUD → ignore → see LOUD → ignore." The validator soft-warn turns the same signal into a persistent-warn surface per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — three sessions of inaction across a 5-archive window emit the 3-of-5 persistent-warn at the next boot, distinct from the per-session LOUD. The soft-warn IS what makes "user merges" enforceable as policy.

Rejected because: The soft-warn is the load-bearing escalation mechanism; the boot LOUD alone is informational pressure, not policy enforcement. The cost of the soft-warn (~30 lines + 7 tests) is small relative to the policy value.

### Hard-fail validator gate instead of soft-warn

What: Promote `dependabot_pr_stale` to hard-fail at some threshold (≥3 stale, or ≥10d age).

Pros: Mechanical enforcement; the AI literally cannot land a commit while stale PRs sit.

Cons: A network blip (`gh pr list` timeout) becomes a commit block. CVE response would be blocked by unrelated stale PRs. The "user merges" posture is deliberately human-paced; hard-failing the validator on unrelated stale PRs blocks unrelated work.

Rejected because: The user has explicit final say on what gets merged when. Hard-failing on count or age subverts that. Soft-warn-with-persistent-escalation is the right strength.

### Combined version-and-PR scanner as one tool

What: Single `scan_session_health.py` that emits version + PR + lockfile-freshness + Issue counts in one combined surface.

Pros: One tool, one boot line, one place to extend.

Cons: Diverging concerns. Version telemetry is a sys.prefix + import question; Dependabot PR scan is a `gh pr list` question; Issue counts are a separate `gh issue list` question. Combining them couples failure modes — if the Issue query fails, the version telemetry should still emit. Separate tools per concern is the existing pattern (`scan_issue_backlog.py` is independent of `validate.py`); the new mechanism follows that pattern.

Rejected because: Tool composition discipline favors small concerns with clear contracts. Composing them at the call-site (session-start.sh) keeps each tool independently testable and each failure mode independently surfaced.

## See also

- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle (the persistent-warn 3-of-5 surface is what makes the new soft-warn load-bearing across sessions).
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — issue-discipline + the `scan_issue_backlog.py` pattern this ADR's scanner is the sibling of.
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv discipline; the version probe verifies its wiring at every boot.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; this mechanism's first-exercise note at `engine/build_readiness/dependabot_visibility_first_exercise.md` closes T1-A at S-0147 via Phase B.
- [ADR 0062](0062-governed-docs-no-amendment-headers.md) — declarative-present-truth amendment discipline; ADR 0069's empirical-record update at S-0147 follows it.
- [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — validator four-phase model; new soft-warn lives in `health_probe` phase per the model.
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — lockfile contract; the dependency surface this mechanism makes visible.
- [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) — Dependabot adoption; ADR 0069's empirical record amended in the same session.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — Alternatives Considered template section.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — new "Stale Dependabot PR handling" subsection.
- [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — persistent-warn annotation for `dependabot_pr_stale`.
- [`engine/build_readiness/dependabot_visibility_first_exercise.md`](../build_readiness/dependabot_visibility_first_exercise.md) — first-exercise readiness note.
- [`engine/tools/probe_versions.py`](../tools/probe_versions.py) — D1 implementation.
- [`engine/tools/scan_dependabot_prs.py`](../tools/scan_dependabot_prs.py) — D2 implementation.
- [`engine/tools/validate.py`](../tools/validate.py) — D3 implementation (`validate_dependabot_pr_stale`).
- [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) — wire-in for D1 + D2.
