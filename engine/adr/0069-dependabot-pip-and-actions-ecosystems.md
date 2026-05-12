# ADR 0069 — Dependabot for `pip` and `github-actions` ecosystems

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0133

## Context

Pre-S-0133, Paideia has no automated dependency vulnerability surfacing. The lockfile contract from [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) makes the transitive graph deterministic, but a CVE in `psycopg`, `chromadb`, `mempalace`, `pdfplumber`, `pypdfium2`, `bandit`, or any of the ~99 transitives surfaces only when someone manually runs `pip-audit` or notices a downstream tool break. The repo went OSS at S-0130 per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) — vulnerability hygiene is now also a posture toward future contributors, not just an internal habit.

[Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) named the adoption as Tier 1 of the SWE-hardening rollout. It is the last open Tier 1 item: #65 lockfile (S-0127 / ADR 0064), #66 gitleaks + #70 bandit (S-0132 / ADRs 0067 + 0068 as Pairing A), #68 CI mirror + #69 PR template + branch protection (S-0131 / ADRs 0065 engine + 0066 as Pairing B) are all in. The Tier 1 prerequisites this Issue named — lockfile (so floors can be bumped against a known transitive graph) + CI mirror (so Dependabot PRs are validated by the same gates a human PR runs through) — are both satisfied.

Pattern source: [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) `.github/dependabot.yml` (config shape, grouping discipline, max-PR cap baseline). GitHub's Dependabot is free for public repos under GitHub Advanced Security's free tier. No alternative scanner under serious consideration — `pip-audit` and `safety` produce CLI reports but no PR pipeline; renovate is heavier and not warranted at this surface size.

## Decision

Five coupled choices mechanize the adoption. The config landing at `.github/dependabot.yml`.

### 1. Two ecosystems: `pip` (repo-root manifest) + `github-actions` (workflows directory)

The `pip` ecosystem reads `pyproject.toml`'s `[project.dependencies]` at the repo root per [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md). When a CVE or minor/patch release is available, Dependabot bumps the floor pin and opens a PR. The PR diff touches `pyproject.toml` only — Dependabot's pip ecosystem does not regenerate `uv.lock`. The reviewer (or a future auto-rebase action) runs `uv lock && uv sync` and amends the PR with the regenerated lockfile before merge. The PR template's lockfile-regen reminder line (amended in the same session) surfaces the regen step to human reviewers at PR time.

`engine/tools/requirements.txt` is the deprecated one-line redirect pointer (S-0127 per ADR 0064) and is NOT scanned — Dependabot's `pip` ecosystem with `directory: "/"` only reads the manifest in the named directory, not nested paths. The deprecation surface is unchanged by this adoption.

The `github-actions` ecosystem reads `.github/workflows/validate.yml` (the single CI workflow per [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md)). When an action version pin (`astral-sh/setup-uv@v3`, `actions/checkout@v4`, etc.) has a minor/patch release available, Dependabot opens a PR. Action pins are typically major-version-locked; minor/patch updates are usually backward-compatible.

### 2. Weekly cadence on Mondays

Dependabot's `schedule.interval: weekly` + `schedule.day: monday` aligns the batch review with start-of-week. Aligns with Dependabot's documented default cadence. Tighter cadences (daily, twice-weekly) produce churn; looser cadences (monthly) delay CVE response. Weekly is the standard.

If a CVE is announced mid-week and warrants out-of-cadence handling, the session author can edit `pyproject.toml` directly per the existing security-update workflow in [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — Dependabot is the *batched* refresh procedure, not the only one.

### 3. Grouped minor/patch updates per ecosystem; major-version bumps separate

Dependabot's `groups` feature bundles multiple deps' minor/patch updates into one PR per ecosystem per week. Without grouping, a week with five package releases produces five PRs in the `pip` ecosystem alone (plus N for github-actions); review overhead accumulates quickly. With grouping, the week is one PR per ecosystem at most.

Major-version bumps (`update-types: ["major"]`) are deliberately NOT included in the group — major version changes may break contracts (config schema migrations, API changes, removal of deprecated features) and require deliberation. Each major-version bump opens its own PR for individual review. A major-version bump may require an ADR amendment per the dependency-discipline.md major-version posture (named in the same session's amendment to dependency-discipline.md).

### 4. Max 10 open PRs per ecosystem (`open-pull-requests-limit: 10`)

Matches the `affaan-m/everything-claude-code` baseline. Caps the surface a reviewer faces if Dependabot opens PRs faster than they are reviewed (post-Phase-6 + post-second-collaborator the surface scales). Tune from observation — if the cap binds (Dependabot pauses new PRs), either review faster or raise.

### 5. Auto-rebase on conflict (`rebase-strategy: "auto"`)

Dependabot's auto-rebase is the default; the config names it explicitly for readability. When a PR's base (main) advances and the Dependabot PR no longer applies cleanly, Dependabot rebases the PR branch against the new base. Reduces stale-PR friction; preserves the PR's CI green history (CI re-runs on each rebase).

### 6. Conventional Commits via `commit-message.prefix: chore` + `include: scope`

Dependabot's commit messages become `chore(deps): bump <pkg> from <a> to <b>` for the pip ecosystem and `chore(deps): bump <action> from <a> to <b>` for github-actions. Matches the project's [Conventional Commits](https://www.conventionalcommits.org/) discipline named in `CLAUDE.md`. The `deps` scope is Dependabot's convention; not invented by this ADR.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

Dependabot adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.**
- ❌ Criterion 2 — new validator soft-warn category. **No.** The existing `uv_lock_out_of_date` soft-warn (per ADR 0064) catches Dependabot PRs where the lockfile is stale; no new category needed.
- ❌ Criterion 3 — new state the boot procedure (or any standing tool) reads. **No.** The session apparatus does not read Dependabot PR state at boot; Dependabot PRs are external-apparatus artifacts that appear in `gh pr list` like any other PR.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches: `.github/dependabot.yml` (new), this ADR, `engine/operations/dependency-discipline.md` (amendment), `.github/PULL_REQUEST_TEMPLATE.md` (one-line amendment), `engine/STATE.md` (Tier 1 closure). Four surfaces; under the threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Matches Issue #67's body declaration. Verification of first-PR-arrival is handled inline (recorded in this ADR's empirical record below as a follow-up commit) — see "Empirical record" subsection.

### Other consequences

- **Positive — automated CVE surfacing.** Any minor/patch release with a security advisory in the deps' upstream surface (or in GitHub's vulnerability DB) is bumped automatically. Pre-S-0133 the only path was manual `pip-audit` or noticing a downstream tool break.
- **Positive — batched review surface.** Grouping caps the surface at one PR per ecosystem per week. Without grouping, the same minor/patch surface would produce 5–10 individual PRs in a typical week.
- **Positive — defense-in-depth with [ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md) and [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md).** The three layers — gitleaks (committed secrets) + bandit (insecure-pattern code) + Dependabot (vulnerable dep versions) — cover three distinct exploit surfaces. None of the three substitutes for either of the others.
- **Positive — `github-actions` ecosystem catches action drift.** `astral-sh/setup-uv@v3` and similar pins drift as upstream releases new minor versions. Pre-S-0133 the pins age silently; post-S-0133 they update on the weekly cadence.
- **Cost — Dependabot PRs do NOT regenerate `uv.lock`.** Dependabot's pip ecosystem reads `pyproject.toml` floors and bumps them; it does not invoke `uv lock`. Reviewer responsibility: run `uv lock && uv sync` against the Dependabot PR branch and amend before merge. The PR template's lockfile-regen reminder (amended in this session) surfaces the step at human-review time. A future auto-rebase GitHub Action that regenerates the lockfile on Dependabot PR branches would close this gap; deferred (separate evaluation; not warranted today at single-maintainer scale).
- **Cost — review-overhead amortization.** Even with grouping, a weekly PR per ecosystem is two PRs per week minimum. At the current single-maintainer scale this is bounded; at ≥2 collaborators per `engine/STATE.md`'s SWE-hardening trigger surface, re-evaluate the cadence (Dependabot supports per-ecosystem cadence overrides).
- **Cost — false-positive risk on transitive bumps.** A minor bump in a transitive that breaks our import-site is possible (rare, but non-zero). Mitigation: CI (`validate.py` + bandit + tests via [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md)) runs on every Dependabot PR. A PR that breaks CI is held for review; the reviewer adjudicates whether to pin around it (`>=X.Y.Z,<X.Y+1`) or skip the bump.
- **Out-of-scope — auto-merge.** Dependabot supports `auto-merge` via `@dependabot merge` PR comments or repo-level auto-merge gates. **Not configured in this session.** Posture rule: user merges. CI green is necessary but not sufficient.
- **Out-of-scope — `pip-audit` or `safety` as a pre-commit or CI gate.** Either could provide an additional layer (scanning the lockfile against the OSV database at every commit / CI run). Deferred — Dependabot covers the CVE-surfacing surface with PR-level granularity; a per-commit gate adds latency and most of its value duplicates Dependabot's. Re-evaluate if Dependabot's coverage proves insufficient in practice.
- **Out-of-scope — product-side dependencies.** This ADR scopes Dependabot to `pyproject.toml` + `.github/workflows/`. Phase 6+ may introduce product-side dependency surfaces (iOS SPM packages per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) Apple platform commitment; backend API runtime deps if a future backend surfaces). Each new surface triggers a Dependabot ecosystem addition via ADR amendment, not silent expansion.
- **Out-of-scope — vendor-update digest cadence.** Dependabot supports `digest` (auto-bump every Dependabot run) for vendored dependencies. Paideia has none.

### Routine-mode interaction (load-bearing)

Routine sessions per [ADR 0051](0051-routine-mode-and-engine-loop.md) operate within a `scope_lock` that names the active task's `allowed_paths`. `pyproject.toml` and `uv.lock` are never in any task's `allowed_paths` per [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) decision 5; routine sessions cannot bump deps.

**Dependabot PRs are NOT routine-mode commits.** They originate from GitHub's external apparatus, not from an `auto_target.json` task, and merge via human review on the `main` branch (not via routine-mode slot claim). Routine-mode scope_lock therefore does not apply to a Dependabot PR's diff — the routine apparatus never sees the PR. The "intentional-only — no drive-by refreshes" rule from `dependency-discipline.md` lines 47–54 governs *session conduct*; Dependabot's weekly cadence IS the intentional refresh procedure, externalized to a schedule.

The pre-commit hook (`engine/tools/hooks/pre-commit`) does NOT run on Dependabot PR commits because the hooks live in the local clone and Dependabot's commits originate server-side. CI (`.github/workflows/validate.yml` per ADR 0065 engine) IS the gate for Dependabot PRs. The asymmetric `uv_lock_out_of_date` posture (soft-warn locally per ADR 0064; hard-fail in CI per ADR 0065 decision 3) means a Dependabot PR with a stale `uv.lock` fails CI hard, surfacing the regen step before merge.

### Major-version bumps require ADR or amendment

Grouped minor/patch updates are routine — the weekly PR merges (after reviewer regen of `uv.lock` and CI green) without ceremony. Major-version bumps (`update-types: ["major"]`, NOT included in the group per decision 3) require:

- **Compatibility scan.** The reviewer reads the upstream changelog and identifies contract changes.
- **Local exercise.** The reviewer runs `uv sync` against the bumped lockfile locally and verifies the engine test suite + a representative `engine/tools/*.py` invocation against live state.
- **ADR amendment if the bump changes named contracts.** A major bump in `psycopg`, `bandit`, `mempalace`, or any tool with named decision in an ADR (per dependency-discipline.md's "tool prerequisites" tracking) amends the citing ADR with the new pin and updated empirical record.

Drive-by major-version merges without this discipline are forbidden by posture (no mechanical gate; posture-only).

### Empirical record

**S-0133 (authoring):** `.github/dependabot.yml` committed at HEAD. GitHub validates dependabot.yml syntax on push; a syntax error surfaces as a repo-level Dependabot alert (visible via `gh api repos/StarshipSuperjam/paideia/dependabot/alerts` or in the repo Insights → Dependency graph → Dependabot panel). Pre-commit `validate.py` passes (no schema check for dependabot.yml — GitHub-side validation is the gate).

**First-PR-arrival verification (pending).** Wait one week (until the first Monday post-S-0133, 2026-05-18). Expected behavior: Dependabot opens at most one PR per ecosystem (pip + github-actions), each grouped minor/patch updates, each labeled `dependencies` (Dependabot auto-creates if absent), each commit message in the form `chore(deps): bump ...`. The PR triggers CI per `.github/workflows/validate.yml` per ADR 0065 (engine). Verification recorded as a follow-up commit to this ADR's "Empirical record" subsection, or in the next session's `outcome_summary` per `engine/operations/session-shutdown-sequence.md`.

## See also

- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv discipline (the venv is what `uv sync` populates after a Dependabot lockfile regen).
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — routine-mode scope_lock (Dependabot PRs are non-routine, named explicitly above).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate (this adoption does NOT qualify; criteria evaluation above).
- [ADR 0064](0064-uv-lockfile-and-reproducible-builds.md) — lockfile contract (`pyproject.toml` + `uv.lock` are the bumpable surface).
- [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) — CI mirror (Dependabot PRs are validated by the same workflow as human PRs).
- [ADR 0066](0066-pr-template-and-branch-protection.md) — PR template + branch protection (Dependabot PRs see the discipline checklist; required status checks gate merge).
- [ADR 0067](0067-gitleaks-pre-commit-secret-scanning.md) — defense-in-depth sibling (secret-scan layer).
- [ADR 0068](0068-bandit-sast-pre-commit-and-ci.md) — defense-in-depth sibling (SAST layer).
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — Layer 1 ops doc; security-update workflow section updated in the same session to past-tense citing this ADR.
- [`.github/PULL_REQUEST_TEMPLATE.md`](../../.github/PULL_REQUEST_TEMPLATE.md) — discipline checklist; lockfile-regen reminder line amended in the same session.
- [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) — closes; last Tier 1 SWE-hardening Issue.
- Pattern source: `affaan-m/everything-claude-code` `.github/dependabot.yml`.
