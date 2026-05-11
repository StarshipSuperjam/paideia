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
| **Last build session** | **S-0129 (2026-05-11) — Session B of three-session OSS+BYOK refactor.** Downstream doc rewrites per [ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) Consequences land in five files. [`product/docs/business.md`](../product/docs/business.md) Personal Project Disposition list grows six → eight commitments matching ADR 0065 Decision; Pricing and Distribution table rewritten (subscription rows out; free-download + one-time IAP unlock + BYOK rows in; dollar amount TBD); Operating Cost Model retitled "Infrastructure Operating Cost" with single-part ~$200–300/yr floor; Annual Operating Subsidy Budget section retired; Cost Amplification with Session Length reframed user-side. [`product/docs/infrastructure.md`](../product/docs/infrastructure.md) Deployment Target rewritten Apple-only-with-client-direct-API; new BYOK key handling subsection names Keychain storage with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, no iCloud sync, force-crash pre-submission test, and the architectural clarification that *graph build and graph analysis remain back-end maintainer work* — user conversations surface signals the back-end review pipeline consumes as candidate inputs (like bug reports vs. code patches), but no graph-mining work runs on the user's device. [`ROADMAP.md`](../ROADMAP.md) Phase 8 + Phase 9 success criteria rewritten (cost-cap-mechanism criterion removed; BYOK onboarding flow + force-crash test + milestone-bound repo-migration trigger as Phase-9-entry gate added; Phase 9 pedagogical-degradation discipline per ADR 0014 replaces the prior cost-cap-mechanism Phase 9 criterion; static-polish foreclosure extended to bind against user-funnel-mechanic). Strong working commitments item 2 updated to ADR 0065. [`product/docs/MISSION.md`](../product/docs/MISSION.md) Disposition paragraph + commitment 2 rewritten. [`product/adr/0014-sonnet-teaches-opus-reviews.md`](../product/adr/0014-sonnet-teaches-opus-reviews.md) Consequences extended (optional editorial pass folded in per the approved plan) to absorb the pedagogical-degradation principle from retired ADR 0029 — "degrade rather than terminate mid-concept-engagement" survives as a teaching discipline scoped to Sonnet's per-turn context preparation. **S-0128 leftover cleanup picked up in this session** (single commit before substantive rewrites): ENGINE_LOG invented `### Known unfixed` subsection removed (Keep-a-Changelog discipline); STATE.md side-discoveries free prose replaced with Issue-link references to [#91](https://github.com/StarshipSuperjam/paideia/issues/91) and [#92](https://github.com/StarshipSuperjam/paideia/issues/92). Seven commits total (eager-claim + cleanup + 5 substantive + closeout). Soft-warns: persistent only (issue_collision / missing_rigor_score / orphan_leaf; no new categories; issue_collision count rose to 28 from S-0128's 21 because Issues #91 + #92 now exist and surface as scope-collision candidates against this session's working title). Prior sessions: see [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` for S-0128 (OSS+BYOK Session A, ADR 0065 supersession), S-0127 (Issues #65 + #90), and S-0126 (audit follow-ups #87/#88/#89). |

## Next session work item

**S-0130 — Session C of three-session OSS+BYOK refactor: LICENSE / PII cleanup / OSS hygiene / public-flip cycle per [ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) Consequences.** Mechanical-but-broad sweep; ends with the repo materially ready for the public visibility flip.

- **License + top-level OSS hygiene.** Replace `LICENSE` with full Apache 2.0 text; copyright line `Copyright (c) 2026 The Paideia Project Contributors`. Author `NOTICE` at repo root. Author `CONTRIBUTING.md` (minimal — points to CLAUDE.md, ADR/ENGINE_LOG/MemPalace conventions, engine session protocol; "this is a personal project; contributions accepted at maintainer's discretion; if you fork for App Store distribution, please rebrand"). Author `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1). Rewrite `SECURITY.md` for OSS+BYOK posture. Rewrite `README.md` (drop `(private)`; drop personal-name reference; add Status/OSS section).
- **PII cleanup.** ~137 tracked files contain `/Users/shanekidd/` and ~3 files contain "Shane Kidd". Batch substitution `s|/Users/shanekidd/|~/|g` across tracked set; explicit handling for `LICENSE`, `README.md`, `engine/ENGINE_LOG.md`, `engine/adr/0050-project-venv-and-hook-path-wiring.md`. `.claude/settings.json` lines 4–10 cleaned (move main-repo-path-dependent permissions to `.claude/settings.local.json` gitignored, OR rewrite as portable patterns if Claude Code syntax supports). `engine/build_readiness/*.md` and `HANDOFF.md` and `docs/health-checks/S-*.md` swept with the same `~/`-substitution.
- **`.env.example`** verified / updated to note BYOK posture (iOS app does not consume `.env`).
- **Verification before public flip.** `git ls-files | xargs grep -l 'Shane Kidd'` returns empty. `git ls-files | xargs grep -l '/Users/shanekidd'` returns empty. `git ls-files | xargs grep -lE 'sk-ant-|sk-proj-|pat_'` returns empty (defense-in-depth on credential-shaped strings). `LICENSE` parses as recognized Apache 2.0.
- **Public flip moment.** `gh repo edit StarshipSuperjam/paideia --visibility public`; tag `oss-flip-v1.0.0`; verify via `gh repo view --json visibility,licenseInfo`. After the flip, `engine/STATE.md` GitHub row updates from `(private)` to OSS-status.

Plan file (Session A authored): [`~/.claude/plans/i-want-to-shift-hidden-hedgehog.md`](https://github.com/StarshipSuperjam/paideia) Session C section.

The user may choose to interleave SWE-hardening Issues (#66 gitleaks; Pairing B #68+#69 CI mirror + PR template / branch protection; #67 Dependabot) before Session C if desired — the dependency chain (A → B → C) is sequence-rigid only between adjacent sessions; SWE-hardening Issues are independent of the OSS+BYOK content disposition.

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 #66 + Pairing B (#68 + #69) + #67 Dependabot; Tier 2 #70 (bundled as Pairing A with #66) + #71 pytest-cov + #72-#74 + #75 priority:urgent skill; Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration.

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
