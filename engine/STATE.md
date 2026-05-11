# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. ADR collection: **61 (59 Accepted + 2 Superseded; 25 engine + 36 product)**. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0125 (2026-05-11) — SWE-hardening rollout pairings annotated + S-0121 audit findings adjudicated.** Two governance items bundled into one session per CLAUDE.md fix-in-context posture and the feedback memory "Don't split work into multiple sessions to hedge on length". **Part 1:** annotated three combined-session pairings in the "SWE-hardening rollout" section's Tier 1 + Tier 2 tables — Pairing A (#66 gitleaks + #70 bandit; shared pre-commit hook + validate.py integration surface), Pairing B (#68 CI mirror + #69 PR template + branch protection; branch protection requires CI status check, both .github/-only), Pairing C (#73 /review + #74 /security-review; identical Skill-authoring pattern, anti-rationalization table reused). Added "Combined-session pairings" subsection with the rationale table; updated Pickup rule to reference *eligible units* (Issue OR pairing). Issue bodies unchanged. **Part 2:** populated [`docs/health-checks/S-0121.md`](../docs/health-checks/S-0121.md) "User adjudication" subsection (previously blank per ADR 0057 user-buffered execution) — 6 items adjudicated. Three Issues filed for accepted-but-substantial work: [#87](https://github.com/StarshipSuperjam/paideia/issues/87) bundles Retire-C (8 ADR Consequences inline-amendment retire) + the 3 recommended governed-doc validator soft-warns (STATE.md row count / ADR `### Amendment` headers / HANDOFF long-resolved-sections) because all four share the *AI-default additive prose in governed docs* root pattern; [#88](https://github.com/StarshipSuperjam/paideia/issues/88) retires the validator `< 500ms` runtime target for tiered (structural < 500ms, graph-audit < 5s, total < 6s) + per-phase timing instrumentation; [#89](https://github.com/StarshipSuperjam/paideia/issues/89) refines `scan_orphans.py` `ops-doc-uncited` axis against false-positives. Two items landed inline per CLAUDE.md "Default to fix-in-context": **Item F** — mode-gated `empty_declared_scope` soft-warn on `current.json.mode == "routine"` in [`engine/tools/validate.py`](tools/validate.py) (the field is a routine-mode contract surface per ADR 0049; was over-firing on every interactive build session); 4 new tests added to [`engine/tools/test_validate_scope_discipline.py`](tools/test_validate_scope_discipline.py); 18/18 tests pass; ops-doc annotation in [`engine/operations/tools-validate-interpretation.md`](operations/tools-validate-interpretation.md) updated. **Item Cold** — swept user-local `/Users/shanekidd/.claude/plans/...` references from 5 ADRs (engine: 0022, 0054; product: 0033, 0034, 0035); 4 entire See-also bullets deleted, 3 body-prose occurrences tightened to drop the unresolvable path while preserving substance; `grep -l "/Users/shanekidd/.claude/plans" engine/adr/*.md product/adr/*.md` returns empty post-sweep. Closes the S-0121 audit per ADR 0057. Six commits: eager-claim, pairings annotation, Item F (with mypy fix recommit), Item Cold sweep, audit report populate, close. Previous: **S-0124 (2026-05-11) — SWE-hardening rollout authored.** Filed 22 GitHub Issues ([#65](https://github.com/StarshipSuperjam/paideia/issues/65)–[#86](https://github.com/StarshipSuperjam/paideia/issues/86)) from the audit plan at `~/.claude/plans/not-a-working-session-sequential-twilight.md` comparing Paideia's posture against [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) (GitHub-side infrastructure templates) and [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) (engineering judgment frameworks). Three tiers + analysis-outcomes: Tier 1 foundations (5 Issues; #65 lockfile, #66 secret scanning, #68 CI mirror, #69 PR template + branch protection, #67 Dependabot); Tier 2 judgment + observability (6 Issues; #70 bandit, #71 pytest-cov, #72 issue templates, #73 /review skill, #74 /security-review skill, #75 frontend-ui-engineering [`priority:urgent`]); Tier 3 composition + release + trigger-gated (8 Issues; #76 /ship orchestration, #77 doubt-driven evaluation, #78 .editorconfig, #80 CODEOWNERS, #79 perf, #82 release tagging, #83 SBOM, #84 monthly metrics); analysis-outcome additions (3 Issues; #81 ADR template, #86 revert/rollback, #85 API docs). Baked the rollout structure into [`engine/STATE.md`](STATE.md) "SWE-hardening rollout" section (per-tier dependency tables + trigger-gated re-surface table tying Phase 6/9 / deployable-artifact / collaborator-count milestones to specific Issues + explicit non-adoptions table for 9 confirmed-skip decisions). Adoption discipline (ADR + MemPalace decision drawer + first-exercise readiness note where applicable + verification + posture-interaction reasoning) baked into each Issue body so future sessions inherit everything cold. Issue #75 carries `priority:urgent` and is a precondition for any Phase 6 frontend work. No code/migrations/ADRs in this session; each Tier 1+ Issue is its own ADR-tracked downstream session. Previous: **S-0123 (2026-05-11) — Phase 5 production-audit follow-up migrations.** Authored and applied four follow-up migrations against `paideia-dev` per the S-0122 disposition matrix: `0061` retyped 17 history-terminator cross-bridges to `historical_influence` (Issue [#60](https://github.com/StarshipSuperjam/paideia/issues/60), activates the predicate's first use); `0062` flipped 15 direction reversals (Issue [#59](https://github.com/StarshipSuperjam/paideia/issues/59)) — CB-E-63 closed a 4-node Kosaraju cycle through the audit-accepted edge `propositional_attitude → intentionality` from `0040`, reverted via `0062_seed_direction_flips_revert_part1.sql` per S-0123 user adjudication and deferred to Phase 6 cluster re-scope (Issue [#64](https://github.com/StarshipSuperjam/paideia/issues/64)); `0063` pruned 4 weak edges + annotated 5 retain-with-annotation cases (Issue [#61](https://github.com/StarshipSuperjam/paideia/issues/61)); `0064` backfilled evidence on 7 defensible-with-annotation edges (Issue [#63](https://github.com/StarshipSuperjam/paideia/issues/63)). Each migration applied via [`engine/tools/apply_migration.py`](tools/apply_migration.py) (eighth through eleventh load-bearing exercises of the wrapper after S-0050 → S-0075 routine batch); all Layer 2.5 assertions passed at apply time. Final graph state: 380 nodes / 532 edges / 515 `pedagogical_prerequisite` + 17 `historical_influence`; 44 edges with non-NULL evidence (44 = 17 retypings + 14 retained flips + 1 CB-E-63 revert annotation + 5 0063 annotates + 7 0064 annotates). Soft-warn delta: +1 `orphan_leaf` for `phenomenology` (its only inbound `pedagogical_prerequisite` was retyped to `historical_influence`; expected). |

## Next session work item

**S-0126 — open candidates** (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue backlog). The S-0125 governance bundle landed cleanly; no in-flight transition state requires immediate pickup. The user picks among:

- **Add the 4 validator soft-warns from the audit-system-input report** (Issue [#62](https://github.com/StarshipSuperjam/paideia/issues/62)). Three are gate-feasible immediately; one (`historical_node_as_prereq_source`) waits on a node-class schema extension.
- **S-0121 audit follow-up Issues** (filed at S-0125): [#87](https://github.com/StarshipSuperjam/paideia/issues/87) Retire-C bundle (8 ADR amendments + 3 governed-doc soft-warns); [#88](https://github.com/StarshipSuperjam/paideia/issues/88) validator tiered runtime + per-phase timing; [#89](https://github.com/StarshipSuperjam/paideia/issues/89) `ops-doc-uncited` axis refinement.
- **OQ-DEC1-A through OQ-DEC1-D settlement** — Phase 6 self-correction master plan is blocked behind these.
- **Phase 6 audit infrastructure design** — the natural surface for re-scoping the 4-node intentionality/meaning/proposition/propositional_attitude cluster per Issue [#64](https://github.com/StarshipSuperjam/paideia/issues/64) (CB-E-63 cycle deferral).
- **SWE-hardening rollout (Issues [#65](https://github.com/StarshipSuperjam/paideia/issues/65)–[#86](https://github.com/StarshipSuperjam/paideia/issues/86))** — see "SWE-hardening rollout" section below for combined-session pairings. **Issue [#75](https://github.com/StarshipSuperjam/paideia/issues/75) (`frontend-ui-engineering` skill) carries `priority:urgent` and is a precondition for any Phase 6 frontend work.**

## SWE-hardening rollout

> Authored at session-pre-S-0124 (date 2026-05-11) from the audit plan at `~/.claude/plans/not-a-working-session-sequential-twilight.md`. Comparing Paideia's posture against [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) and [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) produced 22 GitHub Issues (#65–#86) across three tiers + analysis-outcomes. **Each adoption is ADR-tracked per its discipline; sessions default to single-Issue scope BUT may bundle declared pairings (see "Combined-session pairings" below — three pairings declared at S-0125).** Cross-cutting mechanisms additionally require a first-exercise readiness note per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md).

**Pickup rule.** A future session reads this section and picks the next *eligible unit* (single Issue OR a declared combined-session pairing — see "Combined-session pairings" below) with no remaining blockers. The boot surface (per [`issue-discipline.md`](operations/issue-discipline.md)) counts the underlying Issues in the standard backlog totals; this section adds the dependency + trigger + pairing structure the count cannot encode.

### Tier 1 — foundations (adopt before any non-trivial code lands)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| [#65](https://github.com/StarshipSuperjam/paideia/issues/65) | `uv lock` lockfile for reproducible builds | — (next eligible) | — |
| [#66](https://github.com/StarshipSuperjam/paideia/issues/66) | `gitleaks` pre-commit + GitHub-native secret scanning | — (next eligible; parallel-safe with #65) | [**A**](#combined-session-pairings) (with Tier 2 #70) |
| [#68](https://github.com/StarshipSuperjam/paideia/issues/68) | Mirror `validate.py` to GitHub Actions CI | #65 | [**B**](#combined-session-pairings) (with #69) |
| [#69](https://github.com/StarshipSuperjam/paideia/issues/69) | PR template + branch protection on `main` | #65, #68 | [**B**](#combined-session-pairings) (with #68) |
| [#67](https://github.com/StarshipSuperjam/paideia/issues/67) | Dependabot for `pip` + `github-actions` ecosystems | #68 | — |

### Tier 2 — judgment + observability (adopt during Phase 6 entry)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| [#70](https://github.com/StarshipSuperjam/paideia/issues/70) | `bandit` SAST in pre-commit + CI | #65, #68 | [**A**](#combined-session-pairings) (with Tier 1 #66) |
| [#71](https://github.com/StarshipSuperjam/paideia/issues/71) | `pytest-cov` coverage reporting with measured floor | #65, #68, #69 | — |
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
