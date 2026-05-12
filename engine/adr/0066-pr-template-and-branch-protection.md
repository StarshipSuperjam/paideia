# ADR 0066 — PR template + branch protection on `main`

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0131

## Context

Pre-S-0131, the repo had no `.github/PULL_REQUEST_TEMPLATE.md` and no branch-protection rule on `main`. Any contributor — including the maintainer via web UI — opened a PR with no checklist; no enforcement of Conventional Commits in titles, local-`validate.py`-pass declaration, ADR-touched declaration, MemPalace decision-drawer declaration, scope_lock awareness, or secret-scan acknowledgement. Direct `git push origin main` was technically allowed from any clone with credentials.

The repo went OSS (Apache 2.0) and publicly visible at S-0130 per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md). External contributors are now reachable; the PR template needs to encode Paideia's session-discipline contracts so that contributors (and the maintainer) confirm the discipline at PR-author time rather than discovering it at review time.

Co-landing with the CI mirror [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) (Pairing B per `engine/STATE.md` SWE-hardening rollout). The branch-protection rule's required-status-checks reference [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md)'s `validate` and `test` jobs by name; the pairing is hard-sequentially coupled because the protection rule cannot be configured before the CI checks exist.

## Decision

Two artifacts + one configuration. The configuration uses `gh api` directly because GitHub does not currently expose branch-protection-as-code in repo-tracked YAML; the exact invocation is recorded here for reproducibility.

### 1. `.github/PULL_REQUEST_TEMPLATE.md`

Adapted from `affaan-m/everything-claude-code` template structure; not verbatim. Sections:

- **Summary** — one paragraph what + why.
- **Conventional commit type** — radio between the seven types in active use + a separate `chore(session):` line. Eager-claim commits should be on their own commit per the session-build-lifecycle; the separate line names this rather than burying it under `chore`.
- **Discipline checklist** — seven items: local `validate.py` passes, soft-warns reviewed, ADR authored/amended if a decision landed, MemPalace `decision` drawer captured if ADR authored, first-exercise readiness note authored if cross-cutting mechanism introduced (per [ADR 0053](0053-mechanism-first-exercise-gate.md)), routine-mode `scope_lock` honored, no secrets in diff.
- **Links** — ADR / plan file / closes #issue.

Items that do not apply should be marked N/A explicitly (a comment in the template). An unchecked item reads as "skipped" in review, not "irrelevant."

### 2. Branch protection on `main` via `gh api`

```bash
cat <<'EOF' | gh api -X PUT repos/StarshipSuperjam/paideia/branches/main/protection --input -
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["validate.py", "pytest engine/tools"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

(`--input -` with heredoc JSON is the reliable form. The `--field`-flag form with bracket syntax for arrays and empty values for `null` has fragile shell-escape semantics and was rejected during S-0131 first-apply.)

Verify round-trip via `gh api repos/StarshipSuperjam/paideia/branches/main/protection`.

The two `required_status_checks.contexts` entries are the `name:` fields from `.github/workflows/validate.yml` (`validate.py` and `pytest engine/tools`). Renaming a job in the workflow requires a coordinated `gh api` update; both surfaces are tracked in this ADR's "See also" so a future rename catches both.

`strict: true` means CI must run on the PR's head SHA after rebase/merge of `main` into the PR — keeps stale-base-ref PRs from merging untested code.

### 3. `enforce_admins=false` is load-bearing

The maintainer holds admin rights to the repo. `enforce_admins=false` preserves the [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) `routine_lifecycle_push.py` bypass pattern — admin permissions exempt the push from the protection rule, so routine-mode lifecycle pushes continue to land on `main` without going through a PR. The wrapper itself is the mechanical verification layer for routine-mode pushes; PRs would defeat the unattended-routine model.

Explicit trigger to re-evaluate: **when a second collaborator joins** (Tier 3 [#80](https://github.com/StarshipSuperjam/paideia/issues/80) CODEOWNERS trigger), this decision needs revisiting. Options at that time: (a) keep `enforce_admins=false` and rely on maintainer discipline for direct pushes; (b) flip to `true` and adopt a routine-PR pattern (routine sessions open a PR and auto-merge after CI green; significantly more complex).

### 4. `required_pull_request_reviews=null` — solo-dev posture

No review requirement. Solo-dev means the maintainer is both author and reviewer. Promote when CODEOWNERS lands ([#80](https://github.com/StarshipSuperjam/paideia/issues/80) trigger).

### 5. Multi-commit PR accommodation

A session that produces 5+ commits (a normal Phase-5-style seeded build) PRs them together. The template's prose accommodates — no per-commit-Conventional-Commit assertion, just the PR-title type. The eager-claim `chore(session):` commit is its own commit per session-build-lifecycle and is named separately in the checklist so the PR title type can reflect the substantive work, not the slot-claim ritual.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

PR template + branch protection do NOT qualify for a first-exercise readiness gate:

- ❌ Criterion 1 — new session mode. No.
- ❌ Criterion 2 — new validator soft-warn category. No.
- ❌ Criterion 3 — new state file the boot procedure reads. No (the PR template is read by GitHub on `gh pr create`; not by any boot procedure).
- ❌ Criterion 4 — Consequences span ≥3 ops docs OR ≥5 tooling files. No (touches `.github/PULL_REQUEST_TEMPLATE.md`, this ADR, and the `gh api` invocation = 3 surfaces, none of which are ops docs or tooling files in the criterion sense).

The Issue #69 body explicitly named no readiness note required, and this evaluation confirms.

### Other consequences

- **Positive — discipline at PR-author time.** Contributors confirm the seven discipline contracts before the PR opens; reviewers don't re-derive whether `validate.py` ran.
- **Positive — direct-push protection.** Non-admin clones (any future contributor) cannot bypass the workflow by pushing directly to `main`. CI red on `main` becomes structurally impossible for non-admin pushes.
- **Positive — linear history preserved.** `required_linear_history=true` enforces rebase-or-squash. The eager-claim → in-session-commits → final-commit shape stays readable in `git log`.
- **Positive — conversation resolution required.** Inline review comments must be resolved before merge — prevents "looks good, merge anyway" with open threads.
- **Cost — maintainer self-discipline for direct pushes.** With `enforce_admins=false`, the maintainer can still `git push origin main` directly and bypass the checks. Mitigation: the template-required local `validate.py` declaration applies to all main-touching work; the routine `routine_lifecycle_push.py` wrapper applies its own mechanical verification for routine pushes; eager-claim and final-commit pushes are owned by the session-build-lifecycle Skill, which runs the pre-commit hook locally. The gap is only un-eager-claimed manual `git push origin main` from the maintainer's terminal, which doesn't happen in practice.
- **Cost — branch protection isn't repo-tracked YAML.** The `gh api` invocation lives in this ADR. GitHub Settings UI is the runtime location. A future config drift between this ADR and the actual rule is detectable manually via `gh api repos/.../branches/main/protection` round-trip read; no automated drift detection today.
- **Out-of-scope — required PR reviews.** Solo-dev; promote when CODEOWNERS lands.
- **Out-of-scope — auto-merge on green.** No automation today. Manual merge after CI green.
- **Out-of-scope — protection on other branches.** Only `main` is protected. Worktree-`claude/*` branches are short-lived; no protection rule.

## See also

- [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — `routine_lifecycle_push.py` admin-bypass interaction (the load-bearing reason `enforce_admins=false`).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate (this adoption does not qualify; evaluation in Consequences).
- [ADR 0065 (engine)](0065-validate-py-mirror-to-ci.md) — co-landing CI mirror (the protection rule's required status checks).
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — the discipline contracts the template encodes.
- [Issue #69](https://github.com/StarshipSuperjam/paideia/issues/69) — closes.
- [Issue #80](https://github.com/StarshipSuperjam/paideia/issues/80) — CODEOWNERS; re-evaluate `enforce_admins` + `required_pull_request_reviews` when this triggers (≥2 collaborators).
- Pattern source: `affaan-m/everything-claude-code` PR template structure.
