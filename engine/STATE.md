# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 CLOSED, Tier 2 CLOSED entirely.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks + #70 bandit (S-0132 / ADR 0067 + ADR 0068); #67 Dependabot (S-0133 / ADR 0069). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66); Pairing C #73 `/review` + #74 `/security-review` (S-0134 / ADR 0070 + ADR 0071); #75 frontend-ui-engineering modular split via `/frontend-discipline` + `/paideia-frontend-overlays` (S-0135 / ADR 0072 + ADR 0073); #71 pytest-cov coverage floor (S-0136 / ADR 0074; measured baseline 80%, floor 78%); #72 GitHub issue templates (S-0137 / ADR 0075). **S-0138 closed the S-0137 in-context harness-allowlist over-reach** via `engine/tools/build_lifecycle_push.py` (sibling to `routine_lifecycle_push.py` per ADR 0054) + new engine ADR 0076. **S-0139 closed analysis-outcome [Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81)** (narrowed at boot — lifecycle-state half already in place) via engine ADR 0077: "Alternatives Considered" template section + Deprecated ADRs join `validate_adr_back_reference_orphan`. ADR collection: **80 (76 Accepted + 4 Superseded; 43 engine + 37 product)** — engine ADR 0078 landed at S-0140. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0140 (2026-05-12) — Revert and rollback discipline: new Layer-1 ops doc + engine ADR 0078; closes Issue #86.** New engine ADR ([0078](adr/0078-revert-and-rollback-discipline.md)) + new ops doc [`engine/operations/revert-and-rollback-discipline.md`](operations/revert-and-rollback-discipline.md). Five-section ops doc: when to revert vs forward-fix (decision criteria); revert procedure via PR flow with `revert: <subject> [reverts <sha>]` Conventional Commits prefix; five named project-mechanism interactions (lifecycle-push wrappers refuse `revert:` in deliverable mode by design — PR flow is the right surface; `routine_eager_claim_recovery.py` HEAD-shape regex does not match `revert:` so the recovery script does not false-trigger; `apply_migration.py` handles in-flight SQL rollback via BEGIN/COMMIT but a SUCCESSFUL apply requires a separate `NNNN_rollback_<reason>_partN.sql` migration per `migration-discipline.md`'s existing rollback-authorship rule; ADR supersession via successor ADR + Status: Superseded by ADR NNNN, not deletion; MemPalace `decision` drawers are immutable — reverts author a new drawer alongside the original); hotfix flow for critical production bugs; "What does NOT change for reverts" section recording the ADR 0078 rejection rationale. **Premise correction discovered at boot** — Issue #86's body said "verify `revert:` is in `validate.py` allowed Conventional Commits types; add if missing"; on inspection, `validate.py` does not validate commit subjects at all (no `commit_type` / `conventional` / `allowed_types` surface). The actual prefix gate lives in [`engine/tools/routine_lifecycle_push.py:99`](tools/routine_lifecycle_push.py) (`DELIVERABLE_SUBJECT_RE`) and is inherited by [`engine/tools/build_lifecycle_push.py:166`](tools/build_lifecycle_push.py). The Issue body's own framing — "reverts go through PR flow, not the wrapper" — is internally consistent with leaving the wrapper regex strict. Disposition: **no code change to wrappers or `validate.py`**; the ops doc + ADR document the PR-flow disposition explicitly, closing the future re-litigation surface ("should I add `revert:` to the wrapper?"). **ADR 0078 dogfoods the canonical "Alternatives Considered" section per ADR 0077** — four rejected alternatives with full What/Pros/Cons/Rejected-because structure: (1) extend `code-discipline.md` instead of authoring a new ops doc (rejected: "one concern per file" convention; expression contract is a different surface from procedural revert/rollback); (2) add `revert:` to `DELIVERABLE_SUBJECT_RE` (rejected: scope mismatch + review-bypass risk); (3) author a separate ADR specifically for migration rollback (rejected: rule already exists in `migration-discipline.md`, cross-reference suffices); (4) defer the ops doc and address per-incident (rejected: deferral-without-mechanism is silent indefinite deferral per `feedback_no_pilot_wait_and_see.md` + `feedback_no_preemptive_deferral.md`). No first-exercise readiness note per ADR 0053 — procedural ops doc + ADR is not a cross-cutting mechanism (no new tool wraps a harness gate; no novel cross-session protocol; no shape-verification logic ships; mirrors the negative-finding precedent from ADRs 0069/0070/0071/0072/0073/0075/0077 as the **8th consecutive** ADR applying the discipline). Cascade landings: `engine/operations/README.md` index gains a bullet under "Decisions and review"; `engine/operations/cross-references.md` gains ADR 0078 row + ops-doc row; `code-discipline.md` + `migration-discipline.md` See-also sections gain sibling cross-references; CLAUDE.md "Topical pointers" gains a bullet; ADR README index gains row 0078 (engine count corrected 41 → 43, total 78 → 80 — pre-S-0140 prose had drifted to "41 / 78"; the S-0140 update lands on the correct counts). Three commits: eager-claim bf7bd0b + deliverable (pending) + closeout (pending). Deliverable push landed via `build_lifecycle_push.py deliverable` — third natural exercise of the wrapper's deliverable mode after S-0138/S-0139. ADR collection 79 → 80 (Accepted 75 → 76; Superseded 4 stable; engine 42 → 43; product 37 stable). Soft-warns persistent only — baseline carryover (22 issue_collision at eager-claim time, 360 missing_rigor_score, 1 orphan_leaf). |


## Next session work item

**S-0141 — cadence audit DUE.** The slot is the cadence-aligned slot: `slots_since = 141 - 121 = 20 = cadence`. Per [ADR 0022](adr/0022-periodic-project-health-checks.md) and [`engine/operations/health-check.md`](operations/health-check.md), the trigger fires at boot. The session boot surface should propose: *"Next slot is S-0141. Cadence trigger fires for a project health check. Run the audit now or defer?"* User accepts (the session's work is the audit; `health_check.py` bumps `last_audit_session` to S-0141 at report-emit) or defers (proceed with planned work; trigger fires again next session and becomes overdue).

If the user defers, eligible alternative units (zero-blocker, ready-to-execute):

- **[Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)** — `/ship` multi-model orchestration skill (composes #73 `/review` + #74 `/security-review` + #71 pytest-cov). All blockers closed. First-exercise of the layered review stack. Medium density (skill body + synthesis template + ADR + first-exercise readiness note).

Tier 3 items remain trigger-gated (#77 doubt-driven-development; #78 `.editorconfig`; #79 performance-optimization; #80 CODEOWNERS ADR-promotion-gated; #82 release tagging; #83 SBOM; #84 repo-health metrics; #85 API documentation discipline trigger-gated on Phase 6+).

**Tier 1 verification still pending**: wait until Monday 2026-05-18 for the first Dependabot run. Expected: at most one PR per ecosystem (pip + github-actions), grouped minor/patch, commit message `chore(deps): bump ...`. Verification recorded in ADR 0069's "Empirical record" subsection or in the next session's `outcome_summary`.

**Pairing C verification still pending**: first real invocation of `/review` and `/security-review` against substantive changes. Captured in ADR 0070's + ADR 0071's "Empirical record (pending)" subsections, or in the invoking session's `outcome_summary`. AI may surface invocation as a suggestion on substantive code changes (the user adjudicates).

**S-0135 verification still pending**: first real invocation of `/frontend-discipline` + `/paideia-frontend-overlays` against substantive frontend code (marketing-site authoring, knowledge-graph visualizer authoring, or Phase 6 SwiftUI entry — whichever opens first). Captured in ADR 0072 + 0073 "Empirical record (pending)" subsections.

**S-0136 verification closed in-session**: T1-A (CI green on deliverable push) verified via run [25753339781](https://github.com/StarshipSuperjam/paideia/actions/runs/25753339781) on SHA `9f8ea63` — both jobs `validate.py` + `pytest engine/tools` exit 0; `Run pytest engine/tools with coverage` step green against the post-S-0136 corpus (coverage 80% ≥ floor 78%). T1-B (gate fires red above floor) verified empirically in-session via direct `uv run coverage report --fail-under=99` → exit 2. Both Tier 1 readiness criteria closed; Tier 2 + Tier 3 forward-pointers per `pytest_cov_first_exercise.md`.

**Visual-identity ADR (future product session)**: needed before `/paideia-frontend-overlays` overlay 5 tightens from `FYI` to `Required`. Triggered when the user is ready to commit palette/type/motif specs to ADR contract; until then, overlay 5 references the working prototype as load-bearing context. Cascade per ADR 0041 will update the overlay skill in the same session the ADR lands.

**ADR 0035 ambiguity**: the user's S-0135 clarification surfaced an ambiguity in ADR 0035 — "no web app" plausibly applies to consumer product distribution only, not to marketing-site or knowledge-graph visualizer surfaces. Filed as a separate GitHub Issue at S-0135 close for product-session adjudication; ADRs 0072 + 0073 cross-reference the ambiguity in their See-also sections.

**S-0137 verification (pending — first natural Issue filing)**: first real authoring through the new templates exercises the template chooser, required-field UI block, and auto-label behavior. Captured in ADR 0075's "Empirical record (pending)" subsection or the invoking session's `outcome_summary`.

**S-0138 verification (Tier 1 closed in-session at S-0138; Tier 2 partial after S-0139)**: `build_lifecycle_push.py` Tier 1 closed at S-0138 close via the session's own deliverable + close push exercises (dogfood). **Eager-claim mode first exercise closed at S-0139 boot** (commit `a739106` pushed via `python3 engine/tools/build_lifecycle_push.py eager-claim` → exit 0 + parent main FF'd cleanly; S-0139 deliverable + close pushes are the second + third natural deliverable-mode exercises). Tier 2 remaining forward-pointers per [`engine/build_readiness/build_lifecycle_push_first_exercise.md`](build_readiness/build_lifecycle_push_first_exercise.md): first refusal exercise (malformed lifecycle commit); first push-rejection exit-3 exercise.

**S-0139 verification (closed in-session)**: ADR 0077's deliverables verified end-to-end. Template change visible in `adr-authoring.md` between Decision and Consequences. ADR 0077 dogfoods the new section with four full Pros/Cons/Rejected-because alternatives. Validator extension: all 169 validate-tests green; 6 orphan-check tests green including the 2 new Deprecated coverage tests; full `validate.py` pass exits 0 with no new soft-warns (baseline carryover only: 23 issue_collision / 360 missing_rigor_score / 1 orphan_leaf). Issue #81 closed at session shutdown with comment naming ADR 0077 and the narrowed-scope discovery. MemPalace decision drawer `drawer_paideia_decisions_14689598e4bbbac248e785db` captures the four-alternative deliberation + the narrowed-scope discovery as load-bearing pattern.

**S-0140 verification (closed in-session)**: ADR 0078's deliverables verified end-to-end. New ops doc `engine/operations/revert-and-rollback-discipline.md` covers all five named interactions (lifecycle wrappers / `routine_eager_claim_recovery.py` / `apply_migration.py` / ADR supersession / MemPalace drawers) with concrete file:line citations and verified shapes. ADR 0078 dogfoods the "Alternatives Considered" section per ADR 0077 with four full What/Pros/Cons/Rejected-because alternatives. Premise correction recorded explicitly in both the ops doc ("What does NOT change for reverts" section) and the ADR ("Alternatives Considered" → "Add `revert:` to `DELIVERABLE_SUBJECT_RE`" rejected) — closes the future re-litigation surface. No code change to `validate.py`, `routine_lifecycle_push.py`, `build_lifecycle_push.py`, `routine_eager_claim_recovery.py`, or `apply_migration.py` (per the disposition). Full `validate.py` pass exits 0 with no new soft-warns (baseline carryover only). MemPalace `decision` drawer authored at shutdown capturing the premise correction + the four-alternative deliberation + the PR-flow disposition. 8th consecutive negative-finding for first-exercise readiness criteria per ADR 0053 (mirrors ADRs 0069/0070/0071/0072/0073/0075/0077).

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 CLOSED (#65/#66/#67/#68/#69/#70); Tier 2 CLOSED entirely (#71 + #72 + #73 + #74 + #75); Analysis-outcome additions partially closed (#81 closed at S-0139; #86 closed at S-0140; #85 trigger-gated); Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration. Issue #2 (mempalace wing-name derivation) stays OPEN with S-0132 recurrence comment; upstream-blocked.

Plan file (S-0140 approved): [`~/.claude/plans/partitioned-waddling-flask.md`](~/.claude/plans/partitioned-waddling-flask.md).

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
| ~~[#72](https://github.com/StarshipSuperjam/paideia/issues/72)~~ | ~~GitHub issue templates for 8 type labels~~ — **closed at S-0137 per ADR 0075** | — | — |
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
| ~~[#86](https://github.com/StarshipSuperjam/paideia/issues/86)~~ | ~~Revert/rollback discipline ops-doc~~ — **closed at S-0140 per ADR 0078** | — closed |
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
