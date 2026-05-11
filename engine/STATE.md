# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (private) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 532 edges (was 536 pre-S-0123; -4 from 0063 prunes); 515 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan blocked behind OQ-DEC1 settlement; the audit-side closeout + follow-up execution is complete. **An OSS pivot plus BYOK refactor is in flight as a three-session sequence — Session A landed at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE / PII cleanup / OSS hygiene / public-flip).** ADR collection: **66 (62 Accepted + 4 Superseded; 29 engine + 37 product)** — ADR 0065 landed at S-0128. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last build session** | **S-0128 (2026-05-11) — Session A of three-session OSS+BYOK refactor.** New product [ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes [ADR 0029](../product/adr/0029-personal-financial-cost-ceiling.md) and [ADR 0035](../product/adr/0035-multi-platform-apple-expansion.md) with the eight-commitment OSS+BYOK disposition: (1) Apple platforms preserved verbatim; (2) free download + one-time IAP unlock (dollar amount deferred to Phase 8/9); (3) builder operating cost retires to infrastructure-only floor (~$200–300/yr); (4) consumer BYOK adopted, institutional BYOK / licensing / grants / acquisition remain foreclosed; (5) cost-ceiling mechanism per ADR 0029 retires (no Paideia-controlled API account exists under BYOK); (6) static polish / minimum-shape maintenance preserved verbatim; (7) [new] source open under Apache 2.0, attribution to "The Paideia Project Contributors"; (8) [new] user's API key lives only on-device in iOS Keychain, server stays key-blind via [ADR 0026](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md)'s transcript-non-persistence guarantee. [ADR 0032](../product/adr/0032-personal-project-disposition.md) NOT re-superseded — already Superseded by 0035; chain 0002→0032→0035→0065. [`product/docs/tensions.md`](../product/docs/tensions.md) updates: OQ-BYOK-REGIME reopened-and-re-resolved (consumer BYOK adopted via in-app onboarding flow that mitigates the freshman-self-selection concern; institutional BYOK foreclosed); OQ-WALL-BEHAVIOR closed (cost-cap framing retires; pedagogical-degradation principle absorbs into [ADR 0014](../product/adr/0014-sonnet-teaches-opus-reviews.md)'s role split). Apple App Store compliance posture for BYOK app committed in advance (Guidelines 5.1.1 / 4.0 / 3.1.1 / 3.2.2; Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`; no iCloud sync; no key in logs / crash reports). Milestone-bound repo-migration trigger recorded — migrate `StarshipSuperjam/paideia` to an organizational GitHub account before first App Store submission; to be added to ROADMAP Phase 8 success criteria in Session B. Trademark on "Paideia" deferred-reactive. MemPalace decision drawer `drawer_paideia_decisions_cb5585958acc4043495228dc` captures the conversational reasoning verbatim including the mechanism-vs-justification amend-vs-supersede discipline pair with the S-0012 ADR 0029 amendment drawer (this session is mechanism-changes-supersedes; S-0012 was justification-changes-amends). Three commits: eager-claim, substantive ADR work, closeout. Soft-warns: persistent issue_collision / missing_rigor_score / orphan_leaf only (no new categories). Pre-existing engine ADR count off-by-one (said 28; actual 29) fixed inline. Two pre-existing side discoveries surfaced and filed as Issues [#91](https://github.com/StarshipSuperjam/paideia/issues/91) (duplicate ADR number 0052 across engine/product partition) and [#92](https://github.com/StarshipSuperjam/paideia/issues/92) (`cohort_id` lingers despite ADR 0032 S-0012 removal commitment). Prior sessions: see [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` for S-0127 (Issues #65 + #90 closed) and S-0126 (three audit follow-ups #87/#88/#89). |

## Next session work item

**S-0129 — Session B of three-session OSS+BYOK refactor: downstream doc rewrites per [ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) Consequences.** Plan file: [`~/.claude/plans/i-want-to-shift-hidden-hedgehog.md`](https://github.com/StarshipSuperjam/paideia). Mechanical follow-up to S-0128's contract; every change cites ADR 0065. Files to rewrite:

- [`product/docs/business.md`](../product/docs/business.md) — Operating Cost Model retitles to "Infrastructure Operating Cost — ~$300/yr, independent of user count"; Annual Operating Subsidy Budget retires; Pricing and Distribution rewrites against free-download + one-time IAP unlock (dollar amount TBD); Cost Amplification with Session Length stays but reframes from builder-perspective to user-perspective.
- [`product/docs/infrastructure.md`](../product/docs/infrastructure.md) — Deployment Target rewrites against client-side-direct architecture; new "BYOK key handling" subsection naming Keychain storage and the no-proxy commitment.
- [`ROADMAP.md`](../ROADMAP.md) — Phase 8 success criteria remove cost-cap-mechanism wiring; add user API key configuration / Keychain storage / `/v1/messages` round-trip test. Phase 9 success criteria add BYOK onboarding flow as first-class UI primitive alongside delete-account and data-export. **Add milestone-bound repo-migration trigger** (migrate `StarshipSuperjam/paideia` → org account before first App Store submission) as Phase-9-entry gate.
- [`product/docs/MISSION.md`](../product/docs/MISSION.md) — Disposition section + commitment 2 reframes (threat shape inverts from builder-funnel-mechanic to user-funnel-mechanic; same discipline answers both).

**S-0130 (Session C, follows S-0129)** — LICENSE / PII cleanup / OSS hygiene / public-flip cycle: Apache 2.0 LICENSE with "The Paideia Project Contributors" attribution; NOTICE / CONTRIBUTING / CODE_OF_CONDUCT authored; SECURITY.md rewritten; README rewritten; 137 PII-bearing tracked files swept (`/Users/shanekidd/` → `~/`); 3 files with "Shane Kidd" scrubbed; `.claude/settings.json` lines 4–10 cleaned (move to local settings or rewrite as portable patterns); `.env.example` updated; public flip via `gh repo edit StarshipSuperjam/paideia --visibility public`.

The user may choose to interleave SWE-hardening Issues (#66 gitleaks; Pairing B #68+#69 CI mirror + PR template / branch protection; #67 Dependabot) between Sessions B and C if desired, but the dependency chain (A → B → C) means B and C cannot reorder — B's doc rewrites cite A's ADR; C's public-flip requires LICENSE replacement and PII cleanup that gain context from B's downstream rewrites.

Open Issues track separately and are eligible for picking up after the OSS+BYOK three-session sequence completes. Backlog summary (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 #66 + Pairing B (#68 + #69) + #67 Dependabot; Tier 2 #70 (bundled as Pairing A with #66) + #71 pytest-cov + #72-#74 + #75 priority:urgent skill; Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping.

## SWE-hardening rollout

> Authored at session-pre-S-0124 (date 2026-05-11) from the audit plan at `~/.claude/plans/not-a-working-session-sequential-twilight.md`. Comparing Paideia's posture against [`affaan-m/everything-claude-code`](https://github.com/affaan-m/everything-claude-code) and [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) produced 22 GitHub Issues (#65–#86) across three tiers + analysis-outcomes. **Each adoption is ADR-tracked per its discipline; sessions default to single-Issue scope BUT may bundle declared pairings (see "Combined-session pairings" below — three pairings declared at S-0125).** Cross-cutting mechanisms additionally require a first-exercise readiness note per [ADR 0053](adr/0053-mechanism-first-exercise-gate.md).

**Pickup rule.** A future session reads this section and picks the next *eligible unit* (single Issue OR a declared combined-session pairing — see "Combined-session pairings" below) with no remaining blockers. The boot surface (per [`issue-discipline.md`](operations/issue-discipline.md)) counts the underlying Issues in the standard backlog totals; this section adds the dependency + trigger + pairing structure the count cannot encode.

### Tier 1 — foundations (adopt before any non-trivial code lands)

| Issue | Title | Blocked by | Pairing |
|---|---|---|---|
| ~~[#65](https://github.com/StarshipSuperjam/paideia/issues/65)~~ | ~~`uv lock` lockfile for reproducible builds~~ — **closed at S-0127 per ADR 0064** | — | — |
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
