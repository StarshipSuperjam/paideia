# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening Pairing B (Issues [#68](https://github.com/StarshipSuperjam/paideia/issues/68) + [#69](https://github.com/StarshipSuperjam/paideia/issues/69)) closed at S-0131** — GitHub Actions CI mirror of `validate.py` + PR template + branch protection on `main` ([ADR 0065 engine](adr/0065-validate-py-mirror-to-ci.md) + [ADR 0066](adr/0066-pr-template-and-branch-protection.md)); first-exercise readiness gate T1-A closed both halves empirically. ADR collection: **68 (64 Accepted + 4 Superseded; 31 engine + 37 product)** — engine ADRs 0065 + 0066 landed at S-0131. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0131 (2026-05-12) — Pairing B: GitHub Actions CI mirror + PR template + branch protection.** Two engine ADRs ([0065](adr/0065-validate-py-mirror-to-ci.md) CI mirror, [0066](adr/0066-pr-template-and-branch-protection.md) PR template + branch protection) + first-exercise readiness note ([`engine/build_readiness/ci_mirror_first_exercise.md`](build_readiness/ci_mirror_first_exercise.md) per ADR 0053; T1-A closed both halves empirically, T1-B/T1-C open awaiting natural exercise) + [`engine/tools/hooks/session-start.sh`](tools/hooks/session-start.sh) CI-red-on-main surface (LOUD block at boot when `gh run list --branch main --limit 1` returns conclusion=failure; silent when success/unknown/no-gh). New top-level `.github/` directory holding [`workflows/validate.yml`](../.github/workflows/validate.yml) (two-job workflow: `validate.py` mirrors pre-commit invocation including `uv lock --check` hard-fail + default-mode validate.py + `--code-gates --files <changed>`; `pytest engine/tools` separate job for #71 pytest-cov foundation) and [`PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md) (seven-item discipline checklist adapted from `affaan-m/everything-claude-code`). Branch protection applied via `gh api` (recorded verbatim in ADR 0066): required status checks `validate.py` + `pytest engine/tools` with `strict: true`; `required_linear_history: true`; `allow_force_pushes: false`; `allow_deletions: false`; `required_conversation_resolution: true`; `enforce_admins: false` (load-bearing — preserves [ADR 0054](adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) `routine_lifecycle_push.py` admin-bypass for unattended routine mode). The first CI exercise on main (run 25714671338) surfaced **six pre-existing test-fixture portability bugs** — fix-in-context per CLAUDE.md: (a) `engine/tools/conftest.py` autouse `_scrub_project_env` strips `SUPABASE_DB_URL` so a leak from `test_load_env.test_load_dotenv_walk_up_finds_main_repo_env_from_worktree` (monkeypatch.delenv-after-direct-os.environ-assign undo semantics) cannot break `test_validate.TestMain.test_default_mode_clean_returns_non_two`; (b) both `_make_origin_with_clone` helpers in `test_routine_eager_claim_recovery.py` and `test_routine_lifecycle_push.py` now pass `--initial-branch=main` to `git init --bare` so runners with `init.defaultBranch=master` (GitHub Actions default) don't end up with a bare HEAD pointing at a nonexistent `master` ref. Five commits this session: eager-claim + Pairing B deliverables + ADR README index + CI-portability fixes + (this closeout). Second CI run (25714935236) green; deliberate-fail PR [#93](https://github.com/StarshipSuperjam/paideia/pull/93) (closed, branch deleted) confirmed `validate.py --code-gates` step catches syntax errors as expected (run 25715091632 failed in 12s on the right step). Soft-warns persistent only — `issue_collision` 26 (down from S-0130's 29 because two scope-collision Issues — #68 + #69 — closed this session), `missing_rigor_score` 360 (stable), `orphan_leaf` 1 (stable); no new categories. New top-level `.github/` directory added per ADR 0065 + ADR 0066. |


## Next session work item

**S-0132 — pick the next eligible SWE-hardening unit (Issue or pairing) per the rollout's Pickup rule below.** Pairing B (#68 + #69) closed at S-0131, which unblocked the largest remaining cluster. The naturally-next eligible units are:

- **Pairing A** ([#66](https://github.com/StarshipSuperjam/paideia/issues/66) gitleaks + [#70](https://github.com/StarshipSuperjam/paideia/issues/70) bandit pre-commit security scanners) — now fully unblocked (was waiting on #65 + #68; both closed). Lands two pre-commit scanners in one session.
- **[Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot** — newly unblocked (was waiting on #68). Standalone, small surface.
- **[Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov** — newly unblocked (was waiting on #65 + #68 + #69). Coverage measurement + measured floor authoring; extends `.github/workflows/validate.yml`.
- **Pairing C** ([#73](https://github.com/StarshipSuperjam/paideia/issues/73) `/review` + [#74](https://github.com/StarshipSuperjam/paideia/issues/74) `/security-review`) — Skills authoring under `.claude/skills/`; zero blockers.
- **[Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72)** GitHub issue templates — zero blockers; small surface.

**Note**: [Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) (`frontend-ui-engineering` skill, `priority:urgent`) is a precondition for Phase 6 frontend entry but Phase 6 entry is independently blocked behind OQ-DEC1 settlement, so the priority is "land before any Phase 6 frontend session opens", not "land before any other work."

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 Pairing A (#66 + #70) + #67 Dependabot; Tier 2 #71 pytest-cov + #72 issue templates + Pairing C (#73 + #74) + #75 priority:urgent skill; Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration.

Plan file (S-0131 approved): [`~/.claude/plans/functional-soaring-goblet.md`](~/.claude/plans/functional-soaring-goblet.md).

## SWE-hardening rollout

> Authored at session-pre-S-0124 (date 2026-05-11) from the audit plan at `~/.claude/plans/not-a-working-session-sequential-twilight.md`. Comparing Paideia's posture against [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) and [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) produced 22 GitHub Issues (#65–#86) across three tiers + analysis-outcomes. **Each adoption is ADR-tracked per its discipline; sessions default to single-Issue scope BUT may bundle declared pairings (see "Combined-session pairings" below — three pairings declared at S-0125).** Cross-cutting mechanisms additionally require a first-exercise readiness note per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md).

**Pickup rule.** A future session reads this section and picks the next *eligible unit* (single Issue OR a declared combined-session pairing — see "Combined-session pairings" below) with no remaining blockers. The boot surface (per [`issue-discipline.md`](operations/issue-discipline.md)) counts the underlying Issues in the standard backlog totals; this section adds the dependency + trigger + pairing structure the count cannot encode.

### Tier 1 — foundations (adopt before any non-trivial code lands)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| ~~[#65](https://github.com/StarshipSuperjam/paideia/issues/65)~~ | ~~`uv lock` lockfile for reproducible builds~~ — **closed at S-0127 per ADR 0064** | — | — |
| [#66](https://github.com/StarshipSuperjam/paideia/issues/66) | `gitleaks` pre-commit + GitHub-native secret scanning | — | [**A**](#combined-session-pairings) (with Tier 2 #70) |
| ~~[#68](https://github.com/StarshipSuperjam/paideia/issues/68)~~ | ~~Mirror `validate.py` to GitHub Actions CI~~ — **closed at S-0131 per ADR 0065 engine** | — | — |
| ~~[#69](https://github.com/StarshipSuperjam/paideia/issues/69)~~ | ~~PR template + branch protection on `main`~~ — **closed at S-0131 per ADR 0066** | — | — |
| [#67](https://github.com/StarshipSuperjam/paideia/issues/67) | Dependabot for `pip` + `github-actions` ecosystems | — (newly unblocked at S-0131) | — |

### Tier 2 — judgment + observability (adopt during Phase 6 entry)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| [#70](https://github.com/StarshipSuperjam/paideia/issues/70) | `bandit` SAST in pre-commit + CI | — (newly unblocked at S-0131) | [**A**](#combined-session-pairings) (with Tier 1 #66) |
| [#71](https://github.com/StarshipSuperjam/paideia/issues/71) | `pytest-cov` coverage reporting with measured floor | — (newly unblocked at S-0131) | — |
| [#72](https://github.com/StarshipSuperjam/paideia/issues/72) | GitHub issue templates for 8 type labels | — | — |
| [#73](https://github.com/StarshipSuperjam/paideia/issues/73) | Project-wired `/review` skill (five-axis + anti-rationalization) | — | [**C**](#combined-session-pairings) (with #74) |
| [#74](https://github.com/StarshipSuperjam/paideia/issues/74) | Project-wired `/security-review` skill (OWASP Top 10) | — | [**C**](#combined-session-pairings) (with #73) |
| [#75](https://github.com/StarshipSuperjam/paideia/issues/75) | **`frontend-ui-engineering` skill** [`priority:urgent`] | — — **PRECONDITION for any Phase 6 frontend work** | — (standalone) |

### Tier 3 — composition, release engineering, trigger-gated

| Issue | Title | Status / Trigger |
|---|---|---|
| [#76](https://github.com/StarshipSuperjam/paideia/issues/76) | `/ship` multi-model orchestration | Blocked by #73, #74, #71 |
| [#77](https://github.com/StarshipSuperjam/paideia/issues/77) | Evaluate `doubt-driven-development` workflow | — (evaluation → ADR / amendment / wontfix) |
| [#78](https://github.com/StarshipSuperjam/paideia/issues/78) | `.editorconfig` (cleanup) | — |
| [#80](https://github.com/StarshipSuperjam/paideia/issues/80) | CODEOWNERS for engine/ vs product/ | — (ADR-promotion trigger: ≥2 collaborators) |
| [#79](https://github.com/StarshipSuperjam/paideia/issues/79) | `performance-optimization` skill | **Trigger-gated:** deployable surface exists |
| [#82](https://github.com/StarshipSuperjam/paideia/issues/82) | Release tagging + CHANGELOG automation | **Trigger-gated:** Phase 9 approach OR pre-launch beta |
| [#83](https://github.com/StarshipSuperjam/paideia/issues/83) | SBOM generation | **Trigger-gated:** deployable artifact exists |
| [#84](https://github.com/StarshipSuperjam/paideia/issues/84) | Monthly repo-health metrics workflow | **Trigger-gated:** ≥2 collaborators OR Phase 6 complete |

### Analysis-outcome additions (from agent-skills cross-checks)

| Issue | Title | Status / Trigger |
|---|---|---|
| [#81](https://github.com/StarshipSuperjam/paideia/issues/81) | ADR template enhancement — Alternatives Considered + PROPOSED state + DEPRECATED label | — |
| [#86](https://github.com/StarshipSuperjam/paideia/issues/86) | Revert/rollback discipline ops-doc | — |
| [#85](https://github.com/StarshipSuperjam/paideia/issues/85) | API documentation discipline skill | **Trigger-gated:** Phase 6+ backend API surface OR Python public surface > 5 functions |

### Combined-session pairings

Three pairings declared at S-0125 after audit of the S-0124 rollout. Per the feedback memory "Don't split work into multiple sessions to hedge on length", session-per-Issue was the default — not a hard constraint. Each pairing lands two ADRs + two MemPalace `decision` drawers + (where applicable) two first-exercise readiness notes in one session.

| Pairing | Issues | Rationale |
|---|---|---|
| **A — pre-commit security scanners** | [#66](https://github.com/StarshipSuperjam/paideia/issues/66) + [#70](https://github.com/StarshipSuperjam/paideia/issues/70) | Both extend `engine/tools/hooks/pre-commit`, both add tooling config + version pin, both add `validate.py` integration, both add first-exercise readiness notes. #70's Issue body explicitly declares *"Pairs with: #66"*. Ordering: #70 is blocked by #65 + #68, so the combined session lands after #65 and #68 close. |
| **B — GitHub gating layer** | [#68](https://github.com/StarshipSuperjam/paideia/issues/68) + [#69](https://github.com/StarshipSuperjam/paideia/issues/69) | Hard sequential coupling — #69's branch-protection rule requires #68's CI status check to exist before configuration makes sense. Both touch `.github/` exclusively; same scope_lock surface. Splitting forces the second session to rebuild eager-claim/routine-push posture context cold. |
| **C — code-review skills** | [#73](https://github.com/StarshipSuperjam/paideia/issues/73) + [#74](https://github.com/StarshipSuperjam/paideia/issues/74) | Both author Skills in `.claude/skills/` adapted from `addyosmani/agent-skills`; identical authoring pattern (`disable-model-invocation: true`, scope_lock awareness, ADR-citation requirement). #73's anti-rationalization table is explicitly reused by #74. |

Issue bodies remain individually trackable; the pairings are surfaced here as the routing layer.

### Trigger surface — re-check at every session boot

| When this becomes true | Action |
|---|---|
| Phase 6 frontend stack is being chosen | **#75 must already be done.** If not, halt Phase 6 entry until it lands. |
| Phase 6 frontend session opens | Re-evaluate #79 for first-pass perf budgets |
| Phase 6 backend API surface opens | Action #85 |
| Phase 9 approach OR pre-launch beta decided | Action #82 |
| Deployable artifact (container, bundle, package) exists | Action #83; re-evaluate #79 with real measurements |
| Second collaborator added | Promote #80 to ADR-tracked; action #84 |
| Phase 6 complete (audit-style review window) | Action #84 |

### Explicit non-adoptions (no Issue filed; decision recorded here)

| Item | Source | Reason for skip |
|---|---|---|
| ECC agents (`planner`, `chief-of-staff`, `loop-operator`, `e2e-runner`) | ECC | Conflict with [ADR 0044](adr/0044-skill-conversion-recipe-vs-reference.md), [ADR 0049](adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md), [ADR 0051](adr/0051-routine-mode-and-engine-loop.md) — existing session/Skill/scope apparatus covers this surface differently and more rigorously |
| ECC skills under `agent-*` / `agentic-engineering` | ECC | Same conflict |
| ECC slash commands wrapping agents/skills | ECC | Not portable; tied to ECC harness |
| ECC `ecc_dashboard.py`, identity / package-manager configs | ECC | Bound to ECC harness model |
| ECC per-language build resolvers | ECC | Python-only on engine; multi-language coverage is a Phase 6 stack-specific decision in-context |
| agent-skills `using-agent-skills` meta-skill | agent-skills | ADR 0044 Skill discipline (recipe-vs-reference partition) is more rigorous |
| agent-skills `git-workflow-and-versioning` (wholesale) | agent-skills | Trunk-based-default conflicts with session ritual; compatible patterns extracted into #86 (revert/rollback discipline) |
| agent-skills `ci-cd-and-automation` (wholesale) | agent-skills | ECC workflows are the pattern source; judgment patterns (no-skip philosophy, 10-min budget, flaky-test discipline, GitHub-Secrets-for-test-creds) baked directly into #68 body |
| Build Cop role from CI skill | agent-skills | Solo-dev not applicable; promote when ≥2 collaborators |

Rejecting any of these later requires explicit reversal (new ADR or amendment to this rollout section).

### Cross-references

- Plan file: `~/.claude/plans/not-a-working-session-sequential-twilight.md`
- Source repos: [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code), [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills)
- Adoption discipline: each Issue body names its ADR requirement, MemPalace decision-drawer requirement, first-exercise readiness note (per ADR 0053) where applicable, verification steps, and posture-interaction reasoning.
