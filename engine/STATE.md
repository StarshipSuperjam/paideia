# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 CLOSED, Tier 2 partial.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks + #70 bandit (S-0132 / ADR 0067 + ADR 0068); #67 Dependabot (S-0133 / ADR 0069). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66); Pairing C #73 `/review` + #74 `/security-review` (S-0134 / ADR 0070 + ADR 0071); #75 frontend-ui-engineering modular split via `/frontend-discipline` + `/paideia-frontend-overlays` (S-0135 / ADR 0072 + ADR 0073); **#71 pytest-cov coverage floor (S-0136 / ADR 0074; measured baseline 80%, floor 78%)**. Tier 2 open: #72 issue templates (only remaining unit). ADR collection: **76 (72 Accepted + 4 Superseded; 39 engine + 37 product)** — engine ADR 0074 landed at S-0136. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0136 (2026-05-12) — SWE-hardening Tier 2 Issue #71: pytest-cov coverage measurement with measured floor.** One engine ADR ([0074](adr/0074-pytest-cov-coverage-floor.md)) + one MemPalace `decision` drawer (`drawer_paideia_decisions_56caa016b49491e0c90e3eee`) + one first-exercise readiness note ([`pytest_cov_first_exercise.md`](build_readiness/pytest_cov_first_exercise.md)). Closes [Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71). Pattern source: `addyosmani/agent-skills/ci-cd-and-automation` + project precedent in [ADR 0068](adr/0068-bandit-sast-pre-commit-and-ci.md). **Measured baseline at S-0136: 80% coverage** (7115 stmts, 1418 missed, 1222 tests passing in 3:39 on workstation); **chosen floor 78%** (baseline − 2pp) baked into `.github/workflows/validate.yml` as `--cov-fail-under=78`. Seven coupled decisions in the ADR: pytest-cov pinned in `pyproject.toml`; coverage config in `[tool.coverage]` (chosen over a separate `.coveragerc` for consistency with ruff/mypy/pytest); floor-procedure trend-watching not aspirational (moves up only via ADR amendment); CI-gate-only (no pre-commit step — coverage is per-suite); no validate.py soft-warn (gates via coverage exit code, mirrors ADR 0068); exclusion list with inline reason-comment discipline; PR template "Coverage delta acknowledged" checkbox. **T1-A + T1-B both closed empirically in-session**: T1-A — GitHub Actions run [25753339781](https://github.com/StarshipSuperjam/paideia/actions/runs/25753339781) on SHA `9f8ea63` concluded `success` (both `validate.py` + `pytest engine/tools` jobs exit 0; `Run pytest engine/tools with coverage` step green at 80% ≥ floor 78%). T1-B — direct `uv run coverage report --fail-under=99` exits 2 + emits `Coverage failure: total of 80 is less than fail-under=99`; `--fail-under=78` exits 0 — gate semantics provably wired upstream of pytest-cov's CLI integration. ADR 0065 engine's forward-pointer "Coverage gating arrives in a follow-up Issue (#71 pytest-cov)" honored; ADR 0068's Tier 3 "Coverage gate composition with #71 pytest-cov" honored. **ADR 0053 rubric** evaluated explicitly: criterion 4 satisfied (6 surfaces touched) → first-exercise readiness note required (authored). Three commits this session: eager-claim + deliverable batch + closeout. Soft-warns persistent only — `issue_collision` 22 (stable, -1 from S-0135 because #71 closes), `missing_rigor_score` 360 (stable), `orphan_leaf` 1 (stable). No new soft-warn categories. ADR collection: **76 (72 Accepted + 4 Superseded; 39 engine + 37 product)** — engine ADR 0074 landed at S-0136. |


## Next session work item

**S-0137 — pick the next eligible SWE-hardening unit per the rollout's Pickup rule below.** Tier 1 closed at S-0133 (Dependabot via ADR 0069). Tier 2 Pairing C closed at S-0134 (/review + /security-review via ADRs 0070 + 0071). Tier 2 Issue #75 closed at S-0135 (modular split via ADRs 0072 + 0073). Tier 2 Issue #71 closed at S-0136 (pytest-cov via ADR 0074). The only remaining Tier 2 unit is:

- **[Issue #72](https://github.com/StarshipSuperjam/paideia/issues/72)** GitHub issue templates — Tier 2; zero blockers; small surface (8 type-label YAML templates + config.yml + ADR + cross-references in `engine/operations/issue-discipline.md` + cascade entry in `engine/operations/cascade-discipline.md`). Templates encode existing discipline (the body-shape posture already documented in `issue-discipline.md`) mechanically rather than relying on author discipline alone. **No first-exercise readiness note required** per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md) rubric (standard GitHub feature, no novel cross-cutting mechanism — re-evaluate explicitly in the new ADR's Consequences per S-0133/S-0135 precedent).

After #72 closes, Tier 2 is fully closed; Tier 3 items are trigger-gated (#76 `/ship` blocked by closed #73/#74/#71; #77 doubt-driven-development evaluation; #78 `.editorconfig`; #79 performance-optimization trigger-gated; #80 CODEOWNERS ADR-promotion-gated; #82 release tagging trigger-gated; #83 SBOM trigger-gated; #84 repo-health metrics trigger-gated). Analysis-outcome additions #81 (ADR template enhancement) and #86 (revert/rollback discipline ops-doc) remain open and pickable.

**Tier 1 verification still pending**: wait until Monday 2026-05-18 for the first Dependabot run. Expected: at most one PR per ecosystem (pip + github-actions), grouped minor/patch, commit message `chore(deps): bump ...`. Verification recorded in ADR 0069's "Empirical record" subsection or in the next session's `outcome_summary`.

**Pairing C verification still pending**: first real invocation of `/review` and `/security-review` against substantive changes. Captured in ADR 0070's + ADR 0071's "Empirical record (pending)" subsections, or in the invoking session's `outcome_summary`. AI may surface invocation as a suggestion on substantive code changes (the user adjudicates).

**S-0135 verification still pending**: first real invocation of `/frontend-discipline` + `/paideia-frontend-overlays` against substantive frontend code (marketing-site authoring, knowledge-graph visualizer authoring, or Phase 6 SwiftUI entry — whichever opens first). Captured in ADR 0072 + 0073 "Empirical record (pending)" subsections.

**S-0136 verification closed in-session**: T1-A (CI green on deliverable push) verified via run [25753339781](https://github.com/StarshipSuperjam/paideia/actions/runs/25753339781) on SHA `9f8ea63` — both jobs `validate.py` + `pytest engine/tools` exit 0; `Run pytest engine/tools with coverage` step green against the post-S-0136 corpus (coverage 80% ≥ floor 78%). T1-B (gate fires red above floor) verified empirically in-session via direct `uv run coverage report --fail-under=99` → exit 2. Both Tier 1 readiness criteria closed; Tier 2 + Tier 3 forward-pointers per `pytest_cov_first_exercise.md`.

**Visual-identity ADR (future product session)**: needed before `/paideia-frontend-overlays` overlay 5 tightens from `FYI` to `Required`. Triggered when the user is ready to commit palette/type/motif specs to ADR contract; until then, overlay 5 references the working prototype as load-bearing context. Cascade per ADR 0041 will update the overlay skill in the same session the ADR lands.

**ADR 0035 ambiguity**: the user's S-0135 clarification surfaced an ambiguity in ADR 0035 — "no web app" plausibly applies to consumer product distribution only, not to marketing-site or knowledge-graph visualizer surfaces. Filed as a separate GitHub Issue at S-0135 close for product-session adjudication; ADRs 0072 + 0073 cross-reference the ambiguity in their See-also sections.

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 CLOSED (#65/#66/#67/#68/#69/#70); Tier 2 CLOSED so far (#71 + #73 + #74 + #75); Tier 2 open: #72 issue templates only; Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration. Issue #2 (mempalace wing-name derivation) stays OPEN with S-0132 recurrence comment; upstream-blocked.

Plan file (S-0136 approved): [`~/.claude/plans/radiant-booping-pixel.md`](~/.claude/plans/radiant-booping-pixel.md).

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
| ~~[#67](https://github.com/StarshipSuperjam/paideia/issues/67)~~ | ~~Dependabot for `pip` + `github-actions` ecosystems~~ — **closed at S-0133 per ADR 0069** | — | — |

### Tier 2 — judgment + observability (adopt during Phase 6 entry)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| ~~[#70](https://github.com/StarshipSuperjam/paideia/issues/70)~~ | ~~`bandit` SAST in pre-commit + CI~~ — **closed at S-0132 per ADR 0068** | — | ~~A~~ closed |
| ~~[#71](https://github.com/StarshipSuperjam/paideia/issues/71)~~ | ~~`pytest-cov` coverage reporting with measured floor~~ — **closed at S-0136 per ADR 0074 (measured baseline 80%, floor 78%)** | — | — |
| [#72](https://github.com/StarshipSuperjam/paideia/issues/72) | GitHub issue templates for 8 type labels | — | — |
| ~~[#73](https://github.com/StarshipSuperjam/paideia/issues/73)~~ | ~~Project-wired `/review` skill (five-axis + anti-rationalization)~~ — **closed at S-0134 per ADR 0070** | — | ~~C~~ closed |
| ~~[#74](https://github.com/StarshipSuperjam/paideia/issues/74)~~ | ~~Project-wired `/security-review` skill (OWASP Top 10)~~ — **closed at S-0134 per ADR 0071** | — | ~~C~~ closed |
| ~~[#75](https://github.com/StarshipSuperjam/paideia/issues/75)~~ | ~~`frontend-ui-engineering` skill~~ — **closed at S-0135 per ADRs 0072 + 0073 (modular split into `/frontend-discipline` + `/paideia-frontend-overlays`)** | — | — closed |

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
