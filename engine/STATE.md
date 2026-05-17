# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/changelog/<YYYY>/S-NNNN-*.md` (per-session entries per ADR 0092; the pre-S-0198 monolithic ENGINE_LOG.md is byte-preserved at `engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + changelog content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + changelog entry.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 533 edges (was 536 pre-S-0123; -4 from 0063 prunes, +1 from S-0155 migration 0065); 516 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan **unblocked at S-0152** via OQ-DEC1-A/B/C/D tension-set settlement (product ADRs 0085–0088); the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 CLOSED, Tier 2 CLOSED entirely, Tier 3 #76 CLOSED.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks + #70 bandit (S-0132 / ADR 0067 + ADR 0068); #67 Dependabot (S-0133 / ADR 0069). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66); Pairing C #73 `/review` + #74 `/security-review` (S-0134 / ADR 0070 + ADR 0071); #75 frontend-ui-engineering modular split via `/frontend-discipline` + `/paideia-frontend-overlays` (S-0135 / ADR 0072 + ADR 0073); #71 pytest-cov coverage floor (S-0136 / ADR 0074; measured baseline 80%, floor 78%); #72 GitHub issue templates (S-0137 / ADR 0075). Tier 3 first-closure: #76 `/ship` multi-model orchestration (S-0148 / ADR 0081 — composes Tier-2 #73 + #74 + #71). **S-0138 closed the S-0137 in-context harness-allowlist over-reach** via `engine/tools/build_lifecycle_push.py` (sibling to `routine_lifecycle_push.py` per ADR 0054) + new engine ADR 0076. **S-0139 closed analysis-outcome [Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81)** (narrowed at boot — lifecycle-state half already in place) via engine ADR 0077: "Alternatives Considered" template section + Deprecated ADRs join `validate_adr_back_reference_orphan`. ADR collection: **92 (85 Accepted + 7 Superseded; 51 engine + 41 product)** — engine ADR 0092 landed at S-0198 (per-session changelog directory replaces monolithic ENGINE_LOG.md; supersedes the ENGINE_LOG-naming/structure clauses of ADR 0037; engine/product wall partition + CHANGELOG.md filename reservation remain Accepted; ADR 0037 flips to Superseded in part; `engine-v0.1.0` tag cuts the foundation close). — engine ADR 0091 landed at S-0188 (engine-memory substrate SQLite + FTS5; supersedes ADR 0090 because Issue #134 falsified its commitment 2a; ADRs 0090, 0056, 0079 flip to Superseded; ADR 0057 amended in-body for the substrate-coupled cluster-detection paragraph; 5-session implementation S-0189 → S-0193 tracked at [Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138)); engine ADR 0079 amended at S-0187 (new "Amendment (S-0187): in-rebuild threshold override" subsection; superseded the next session by ADR 0091); engine ADR 0090 landed at S-0185 (Phase-6 recall-substrate decision; A1-PROPER comprehensive in-project fix campaign with scheduled maintenance + upstream coordination + empirical investigation; substrate preserved; closed Issue #131 — both superseded at S-0188); engine ADR 0089 landed at S-0163 (Skill ↔ Layer-1 procedure-parity validator check; closes Issue #129); engine ADR 0084 landed at S-0151 (pushback-rule extraction-step extension; closes Issue #77); product ADRs 0085–0088 landed at S-0152 (OQ-DEC1-A/B/C/D tension-set settlement; Phase 6 unblocked). The OQ-DEC1 settlements draw from the 0085–0088 range because engine ADRs 0066–0084 occupy that part of the shared sequence per ADR 0037. Full session-by-session history in [`engine/changelog/`](changelog/) (per ADR 0092; historical archive at [`engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`](changelog/_history/ENGINE_LOG-pre-0.1.0.md)). |
| **Last session** | **S-0198 (2026-05-17, interactive build) — Issue #132 closeout via per-session changelog directory cutover (ADR 0092; engine-v0.1.0 foundation-close tag).** Replaced the monolithic 2,799-line `engine/ENGINE_LOG.md` with the Engine reference template's per-session changelog directory pattern at `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md` (the user pointed at `~/Documents/Claude_Files/Engine` mid-plan as "I've already solved this", reshaping Issue #132's literal three-part prescription into a structural cutover). Seven parts in 8 commits + 1 tag: (A) engine ADR 0092 [Supersedes ADR 0037's ENGINE_LOG-naming/structure clauses; engine/product wall partition + CHANGELOG.md reservation remain Accepted] with full ADR 0084 extraction step (empirical duplication-audit sample on S-0030/S-0070/S-0110/S-0150/S-0190 showed 75-90% overlap mean ~83% between ENGINE_LOG entries and archive `outcome_summary` — validated the "duplication audit becomes structural at the 50-line cap" premise) + first-exercise readiness note at [`engine/build_readiness/per_session_changelog_first_exercise.md`](build_readiness/per_session_changelog_first_exercise.md); (B) `engine/changelog/` directory + `engine/schemas/changelog-entry.schema.json` ported byte-for-byte from Engine ref + governed README (`line_cap_soft: 50 / line_cap_hard: 70`); (C) full Engine-ref Session-4-scope aggregator [`engine/tools/changelog_aggregate.py`](tools/changelog_aggregate.py) (`--since <git-tag>` + `--module` + `--format markdown\|json` + `--validate-only`) + 21 pytests all green; (D) `validate.py` rewiring — removed `engine_log_format` check; added `check_changelog_entries` (line-cap soft/hard + jsonschema-validated frontmatter + filename↔session_id consistency; 5 categories) + `check_changelog_readme_governance`; updated `validate_adr_back_reference_orphan` exclusion + STATE.md size-guard pointer; `jsonschema>=4.25.0` dep added; `uv.lock` regenerated; `synthetic_repo` fixture swapped `ENGINE_LOG.md` required-file for `engine/changelog/README.md`; 14 new pytests all green; (E) 0.1.0 release synthesis at [`engine/changelog/2026/S-0198-0.1.0-foundation-close.md`](changelog/2026/S-0198-0.1.0-foundation-close.md) (56 lines; soft-cap slack on release synthesis as designed) + `git mv engine/ENGINE_LOG.md engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md` byte-for-byte (sha256 `b5671df38561dc383b06545af30432995fcf964cb32f76ad8859fcdbd801d014`) + transitional stub authored at Part E and deleted at Part G; (F) shutdown step 7 rewired in lockstep across Layer-1 doc + SKILL.md (step number 7 preserved per ADR 0089 parity); (G) cascade across 22 inbound references in one commit (5 root: `CLAUDE.md` + `engine/STATE.md` + `ROADMAP.md` + `README.md` + `HANDOFF.md`; 8 ops docs: `adr-authoring` + `document-voice` + `engine-memory-conventions` + `cross-references` + `tools-validate-interpretation` + `cascade-discipline` + `routine-mode-operations` + `revert-and-rollback-discipline`; 5 ADRs: 0036/0037/0041/0042/0048 + ADR 0037 Status flip + Supersession Amendment subsection) + follow-up sweep on 5 active-surface refs missed in the first pass (`.claude/commands/start-engine.md` + `.claude/skills/{routine-mode-lifecycle,ship}/SKILL.md` + `CONTRIBUTING.md` + ADR 0041 cascade-description). `engine-v0.1.0` annotated tag created at the cutover state (commit `117aa83`) + pushed to origin. Historical ENGINE_LOG references in pre-S-0198 ADRs + `build_readiness/` + `docs/health-checks/` + `build_plan/` preserved per ADR 0036 cleanup-exemption. T1-A of the readiness note closes in-session (the 0.1.0 entry IS the first per-session entry); T1-B closes at the next material-change session close. Approved plan: [`~/.claude/plans/foamy-plotting-hummingbird.md`](~/.claude/plans/foamy-plotting-hummingbird.md). Detail in [`engine/session/archive/S-0198.json`](session/archive/S-0198.json). |
| **Last build session** | **S-0198 (2026-05-17) — see Last session row.** |


## Next session work item

**S-0198 closed at S-0198.** Issue #132 closed via adoption of the Engine reference template's per-session changelog directory pattern (ADR 0092 supersedes ADR 0037's ENGINE_LOG-naming/structure clauses; `engine-v0.1.0` foundation-close tag cut). T1-A of the first-exercise readiness note closes in-session (this session's 0.1.0 entry IS the first per-session entry).

**S-0199 — Next session work item: user picks.** With Issue #132 now closed and `engine-v0.1.0` tagged, the immediate engine-side cleanup backlog is empty. The user-named product pivot is the default. Tier-A session-sized items still open:

- **PDG papers extraction — Session α (cross-reference audit)** per HANDOFF.md "PDG papers extraction" entry. 6-session pre-phase plan ready for interactive pickup (Sessions α-ζ). Posture is quality-first — no Issues fire before Session ζ.
- **Phase 6 self-correction infrastructure entry**. Unblocked at S-0152 per product ADRs 0085–0088.

Tier-B trigger-gated issues (#22, #24, #79, #82, #83, #84, #85, #115, #117) remain in the backlog as load-bearing activation reminders per the S-0195 plan's triage; do NOT mass-close.

**T1-B of the per-session changelog first-exercise note** closes at the next interactive build session that produces material engine-change content (the session writes its own changelog entry at close; validator's `check_changelog_entries` confirms the entry validates). **T1-C** closes when the aggregator runs against ≥2 entries (natural exercise at the next release-prep session OR explicit invocation).

**Carried open items:**

- **Backup retention** — `~/.mempalace-backup-S-0193-20260517T012057Z.tar.gz` (167MB) preserved per HANDOFF.md; release decision after 5 sessions confirm engine_memory recall is satisfactory and the user signals OK. The S-0194 independent verification audit (verdict PASS) is one of those 5; 3 more to go (S-0195 was the second post-cutover normal-operation session; S-0196 was the third — engine_memory boot search + diary read both fired cleanly and the boot orchestrator produced relevant hits including the S-0184 audit decision drawer + ADR 0042 decision drawer).
- **Worktree-local `engine/.memory/engine_memory.sqlite3` stale files** in pre-S-0193 worktrees — the resolver fix means new sessions read the canonical main-repo file, but worktrees that initialized before S-0193 may carry a local file (harmless, gitignored, can be deleted manually).


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
| ~~[#76](https://github.com/StarshipSuperjam/paideia/issues/76)~~ | ~~`/ship` multi-model orchestration~~ — **closed at S-0148 per ADR 0081** | — closed |
| ~~[#77](https://github.com/StarshipSuperjam/paideia/issues/77)~~ | ~~Evaluate `doubt-driven-development` workflow~~ — **closed at S-0151 per ADR 0084 (Option 2 — CLAUDE.md pushback-rule extension with explicit extraction step for high-stakes decision classes)** | — closed |
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
