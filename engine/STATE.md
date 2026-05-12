# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 nearly closed, Tier 2 partial.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks (S-0132 / ADR 0067). Tier 1 open: [#67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot (last). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66). Tier 2 open: #71 pytest-cov + #72 issue templates + Pairing C (#73 + #74 code-review skills) + #75 frontend-ui-engineering (priority:urgent, Phase 6 entry precondition). ADR collection: **70 (66 Accepted + 4 Superseded; 33 engine + 37 product)** — engine ADRs 0067 + 0068 landed at S-0132. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0132 (2026-05-12) — Pairing A: gitleaks + bandit pre-commit/CI security gates + MemPalace rogue-wing cleanup.** Two engine ADRs ([0067](adr/0067-gitleaks-pre-commit-secret-scanning.md) gitleaks pre-commit + GitHub-native secret scanning, [0068](adr/0068-bandit-sast-pre-commit-and-ci.md) bandit SAST pre-commit + CI) + two first-exercise readiness notes ([`engine/build_readiness/gitleaks_first_exercise.md`](build_readiness/gitleaks_first_exercise.md) T1-A/B/C all closed empirically; [`engine/build_readiness/bandit_first_exercise.md`](build_readiness/bandit_first_exercise.md) T1-A closed via direct gate invocation + T1-B closed via CI run [25741717146](https://github.com/StarshipSuperjam/paideia/actions/runs/25741717146)) + two MemPalace `decision` drawers + new project configs [`engine/tools/gitleaks.toml`](tools/gitleaks.toml) (inherits gitleaks 8.x defaults + `.env.example` + ADR/operations/build_readiness path allowlists) and [`engine/tools/bandit.yaml`](tools/bandit.yaml) (skip B101 globally for pytest convention) + new "External tool prerequisites" subsection in [`engine/operations/dependency-discipline.md`](operations/dependency-discipline.md) naming gitleaks 8.30.1 / gh / uv. Pre-commit hook gains both gates: gitleaks step after worktree settings.json sync check; bandit step after code-discipline gates (`-ll -ii -q` threshold, medium-severity AND medium-confidence floor). `.github/workflows/validate.yml` validate job extended with full-tree bandit step. `pyproject.toml` adds `bandit>=1.7.0` (resolved 1.9.4 + stevedore transitive in uv.lock). GitHub-native secret scanning + push protection enabled via `gh api -X PATCH repos/StarshipSuperjam/paideia` (round-trip verified). **Baseline triage**: pre-S-0132 bandit reported 2577 findings (2557 LOW + 20 MEDIUM + 0 HIGH); 2313 B101 skipped (pytest convention) + 244 LOW filtered by `-ll` threshold + 19 of 20 MEDIUM annotated with inline `# nosec BXXX  # reason` (placeholder SQL construction for B608, scheme-allowlist urlopen vetted by ADR 0059 for B310, test-fixture strings for B108) + 1 MEDIUM filtered by `-ii` confidence threshold. Three production functions refactored to extract SQL into named `sql = ...` variable so nosec lives on the line bandit flags (shape-preserving — 241 tests pass post-refactor). **MemPalace cleanup**: [Issue #2](https://github.com/StarshipSuperjam/paideia/issues/2) (`upstream` + `bug`) re-fired with a new full-encoded-path wing `-Users-...-happy-williams-640cca` (37 drawers); signal-probe-first verified zero high-signal content (37/37 in `room: general`, `added_by: mempalace`); pruned via `prune_mempalace.py --audit-historical-paths --apply` (backup at `/tmp/mempalace-prune-backup-s0132`); Issue #2 commented with recurrence forensics (S-0043 upstream fix incomplete for `.claude/worktrees/<name>` path shape); Issue stays OPEN. Eight commits this session: eager-claim + gitleaks deliverables + gitleaks T1-A/B/C closure + bandit deliverables + bandit T1-A/B closure + ENGINE_LOG/STATE/index updates + MP cleanup + closeout. Mid-session out-of-band push by maintainer (`Update README.md` commit `39e92ee`) required a worktree-branch rebase onto the new origin/main — clean (no README touch in this session's scope). Soft-warns persistent only — `issue_collision` 24 (down from S-0131's 26 because two scope-collision Issues — #66 + #70 — closed this session), `missing_rigor_score` 360 (stable), `orphan_leaf` 1 (stable), `validator_runtime_phase_regression` 1 (new — bandit step's subprocess time crossed phase regression threshold per [ADR 0063](adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md); informational only, not gating). ADR collection: **70 (66 Accepted + 4 Superseded; 33 engine + 37 product)** — engine ADRs 0067 + 0068 landed at S-0132. |


## Next session work item

**S-0133 — pick the next eligible SWE-hardening unit (Issue or pairing) per the rollout's Pickup rule below.** Pairing A (#66 + #70) closed at S-0132 — Tier 1 now has only [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot remaining. The naturally-next eligible units are:

- **[Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) Dependabot** — last open Tier 1 item. Standalone, small surface (`.github/dependabot.yml` + ADR). Closing it completes Tier 1.
- **[Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov** — Tier 2. Coverage measurement + measured floor authoring; extends `.github/workflows/validate.yml` (Pairing B's foundation).
- **Pairing C** ([#73](https://github.com/StarshipSuperjam/paideia/issues/73) `/review` + [#74](https://github.com/StarshipSuperjam/paideia/issues/74) `/security-review`) — Tier 2. Skills authoring under `.claude/skills/`; zero blockers. Defense-in-depth on the SAST gate landed at S-0132.
- **[Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72)** GitHub issue templates — Tier 2; zero blockers; small surface.

**Note**: [Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) (`frontend-ui-engineering` skill, `priority:urgent`) is a precondition for Phase 6 frontend entry but Phase 6 entry is independently blocked behind OQ-DEC1 settlement, so the priority is "land before any Phase 6 frontend session opens", not "land before any other work."

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 #67 Dependabot (last open); Tier 2 #71 pytest-cov + #72 issue templates + Pairing C (#73 + #74) + #75 priority:urgent skill; Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration. Issue #2 (mempalace wing-name derivation) stays OPEN with S-0132 recurrence comment; upstream-blocked.

Plan file (S-0132 approved): [`~/.claude/plans/mossy-beaming-squid.md`](~/.claude/plans/mossy-beaming-squid.md).

## SWE-hardening rollout

> Authored at session-pre-S-0124 (date 2026-05-11) from the audit plan at `~/.claude/plans/not-a-working-session-sequential-twilight.md`. Comparing Paideia's posture against [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) and [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) produced 22 GitHub Issues (#65–#86) across three tiers + analysis-outcomes. **Each adoption is ADR-tracked per its discipline; sessions default to single-Issue scope BUT may bundle declared pairings (see "Combined-session pairings" below — three pairings declared at S-0125).** Cross-cutting mechanisms additionally require a first-exercise readiness note per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md).

**Pickup rule.** A future session reads this section and picks the next *eligible unit* (single Issue OR a declared combined-session pairing — see "Combined-session pairings" below) with no remaining blockers. The boot surface (per [`issue-discipline.md`](operations/issue-discipline.md)) counts the underlying Issues in the standard backlog totals; this section adds the dependency + trigger + pairing structure the count cannot encode.

### Tier 1 — foundations (adopt before any non-trivial code lands)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| ~~[#65](https://github.com/StarshipSuperjam/paideia/issues/65)~~ | ~~`uv lock` lockfile for reproducible builds~~ — **closed at S-0127 per ADR 0064** | — | — |
| ~~[#66](https://github.com/StarshipSuperjam/paideia/issues/66)~~ | ~~`gitleaks` pre-commit + GitHub-native secret scanning~~ — **closed at S-0132 per ADR 0067** | — | ~~A~~ closed |
| ~~[#68](https://github.com/StarshipSuperjam/paideia/issues/68)~~ | ~~Mirror `validate.py` to GitHub Actions CI~~ — **closed at S-0131 per ADR 0065 engine** | — | — |
| ~~[#69](https://github.com/StarshipSuperjam/paideia/issues/69)~~ | ~~PR template + branch protection on `main`~~ — **closed at S-0131 per ADR 0066** | — | — |
| [#67](https://github.com/StarshipSuperjam/paideia/issues/67) | Dependabot for `pip` + `github-actions` ecosystems | — | — |

### Tier 2 — judgment + observability (adopt during Phase 6 entry)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| ~~[#70](https://github.com/StarshipSuperjam/paideia/issues/70)~~ | ~~`bandit` SAST in pre-commit + CI~~ — **closed at S-0132 per ADR 0068** | — | ~~A~~ closed |
| [#71](https://github.com/StarshipSuperjam/paideia/issues/71) | `pytest-cov` coverage reporting with measured floor | — | — |
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
