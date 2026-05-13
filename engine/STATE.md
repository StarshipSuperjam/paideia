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
| **Last build session** | **S-0145 (2026-05-13) — Issue #113 closed: HNSW sync_threshold prevention wrapper + mempalace 3.3.4 → 3.3.5 upgrade.** Hybrid threshold posture per [ADR 0079](adr/0079-hnsw-sync-threshold-tuning.md): 50_000 inherited during bulk rebuilds (mempalace `_HNSW_BLOAT_GUARD` anti-bloat preserved per upstream PR #344), 100 steady-state on live palace (sealed never-flushed-metadata recurrence vector). **Phase 1.5a empirical discovery** corrected Issue #113's wrong-of-mechanism premise: chromadb default isn't 1000-reached-rarely — mempalace deliberately overrides to 50_000 via `backends/chroma.py:52` (3.3.5; `:54` at 3.3.4). At 1–3-drawers-per-session, 50_000 is never reached; metadata dropped on process exit drives the recurring rebuilds. New tool `engine/tools/mempalace_set_sync_threshold.py` overrides via chromadb's `configuration.hnsw.sync_threshold` channel (the metadata channel is rejected on payloads including `hnsw:space` as a distance-function change — verified empirically; `configuration` is the chromadb 1.5.x retrofit path). Mandatory `--backup-dir` for apply; pre-switch state capture; post-switch verification via fresh-client re-read; palace health probe via probe_palace.py subprocess. Boot probe (`session-start.sh`) verify-only; never auto-applies. Rebuild tool emits post-success forward-pointer naming the threshold-set command. **27 pytests green; live palace at threshold=100 on both collections (16,792 drawers + 51 closets); backup retained at `~/.mempalace/palace.S-0145-pre-threshold-switch`.** **Upgrade**: closed stale Dependabot PR #104 (19 commits behind main; CI `uv lock --check` failure on transitive drift); did pyproject + uv.lock change in-session; `uv sync` brought venv to mempalace 3.3.5 + chromadb 1.5.9 (transitive). 3.3.5 complementary fixes: #1342 quarantine_stale_hnsw + #1396 tool_search retry + #1322 client-side quarantine wiring — recovery-side improvements that compound with ADR 0079's prevention. **S-0144 row inline correction** (this row): the S-0144 row claimed "mempalace v3.3.5's default" but the S-0144 venv was 3.3.4 (verified empirically at S-0145); technical claim about embedding-function defaults holds across both versions. **Issue #113 correction comment** posted before close: four-section framing covering mechanism premise + version premise + line-number premise + disposition. New upstream Issue filed on MemPalace/mempalace proposing `--hnsw-sync-threshold N` flag on `init`/`repair`. Validator: 0 hard-fails; baseline soft-warns only. ADR 0079 dogfoods Alternatives Considered per ADR 0077; ADR 0053 first-exercise readiness: 0/4 criteria satisfied (10th consecutive negative finding). 3+ commits: eager-claim be4574c + dep-bump 394fc52 + deliverable (pending) + close (pending). |


## Next session work item

**S-0146 — pick next eligible unit.** Phase 6 entry remains blocked behind OQ-DEC1-A/B/C/D tension settlement (4 tensions decide-before Phase 6, 17+ sessions stale; see [`product/docs/tensions.md`](../product/docs/tensions.md)). Either tackle the OQ-DEC1 deliberation set OR pick one of the ready-to-execute alternatives below.

**Immediate Phase-6 blocker — OQ-DEC1-A/B/C/D** (Server-side mastery / two-hop neighborhood retrieval / embedding strategy for entity resolution / chunk-resolver vs SEP URL pointers). All four are decide-before Phase 6. Settlement converts each to an ADR. Filing options per the S-0141 audit's Gaps section: single coordinated tension-resolution session OR four separate ADR sessions. **Phase 6 cannot open until these settle.**

**Ready-to-execute alternatives (zero-blocker):**

- **[Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)** — `/ship` multi-model orchestration skill (composes #73 `/review` + #74 `/security-review` + #71 pytest-cov). All blockers closed. First-exercise of the layered review stack. Medium density (skill body + synthesis template + ADR + first-exercise readiness note).
- **[Issue #62](https://github.com/StarshipSuperjam/paideia/issues/62)** — 4 validator soft-warns from S-0122 audit (still OPEN since S-0122). The S-0141 audit's "leaky audit-to-fix cycle" worked example. Modest validator-extension work.

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

**S-0143 verification (closed in-session)**: All deliverables landed end-to-end. (1) ADR 0076 Amendment v2: skip-caller pre-flight in `routine_worktree_sweep.py` (8 dedicated pytests) + enriched preserve-report in both `routine_worktree_sweep.py` and `sweep_worktrees.sh` + boot-time bulk sweep wired into `session-start.sh`; verified via the live dry-run output naming the 3 preserved stale worktrees with full state + guidance. (2) ADR 0057 revised Decision 1: inline adjudication when interactive; routine-fired audits keep user-buffered shape; health-check.md + TEMPLATE.md updated. (3) Issue #109 closed — `mempalace_hnsw_divergence` + `mempalace_wing_count_growth` now in `checks_run` unconditionally. (4) Issue #110 closed — `scan_issue_collisions.py` filters upstream-labeled + `[TRIGGER:`-titled Issues (6 new pytests); empirical effect issue_collision 17 → 11 in-session. (5) Issue #111 closed — `is_marker_line_back_pinned()` classifier in `scan_orphans.py` with forward-pin trigger vocabulary (11 new pytests); verified `expression-contract-instantiation.md` no longer false-flags (only `prep-paideia-prompt-pack.md` flagged from the stale-marker axis, correctly). (6) 3 stale worktrees removed in-session under per-worktree user confirmation: S-0103 crazy-ritchie-db0791 + S-0121 admiring-faraday-020026 + S-0128 vibrant-antonelli-850599. **Dogfood (Tier 1):** S-0143's own worktree (`friendly-diffie-c57b62`) is preserved at close per the new Amendment v2 wiring — closes when next session's boot-time bulk sweep collects it. Validator: 0 hard-fails; soft-warns baseline carryover (`issue_collision` 11 — down 17 → 11 from the new filter; `missing_rigor_score` 360; `orphan_leaf` 1). MemPalace `decision` drawer authored capturing the worktree-preservation-vs-cleanup tradeoff + the audit-buffering-vs-inline tradeoff.

**S-0142 verification (closed in-session)**: All deliverables landed end-to-end. (1) S-0141 User-adjudication subsection populated with full disposition table per ADR 0057; (2) 71 stale worktrees removed via `engine/tools/sweep_worktrees.sh --apply` (76 → 5 post-sweep); (3) 4 `health-check-finding` Issues filed ([#109](https://github.com/StarshipSuperjam/paideia/issues/109) / [#110](https://github.com/StarshipSuperjam/paideia/issues/110) / [#111](https://github.com/StarshipSuperjam/paideia/issues/111) / [#112](https://github.com/StarshipSuperjam/paideia/issues/112)) with bodies citing S-0141 audit; (4) ADR 0076 Amendment landed in present-truth declarative form (no `### Amendment` header per ADR 0062 governed-doc soft-warn); (5) `engine/tools/sweep_worktrees.sh` skip-caller's-worktree safety check landed and verified — pre-edit dry-run flagged S-0142's own worktree for removal; post-edit dry-run skipped it correctly. **Dogfood (Tier 1):** post-close `routine_worktree_sweep.py` invocation at S-0142 close — closes when the worktree + branch are gone post-session. **Reversed at S-0143**: the post-close sweep wiring destroyed S-0142's own working folder before the user could follow up; ADR 0076 Amendment v2 at S-0143 reverses the close-side invocation and shifts cleanup to next-session boot. Validator: 0 hard-fails; soft-warns baseline carryover (issue_collision 26 reflecting +4 new Issues; missing_rigor_score 360; orphan_leaf 1); no `adr_consequences_amendment_header` (cleared by present-truth reshape). MemPalace `decision` drawer authored capturing the structural-gap diagnosis + user-pushback-driven scope expansion + the sweep_worktrees.sh safety-check fix-in-context.

Open Issues backlog (per [`engine/ENGINE_LOG.md`](ENGINE_LOG.md) `[Unreleased]` and the GitHub Issue list): SWE-hardening Tier 1 CLOSED (#65/#66/#67/#68/#69/#70); Tier 2 CLOSED entirely (#71 + #72 + #73 + #74 + #75); Analysis-outcome additions partially closed (#81 closed at S-0139; #86 closed at S-0140; #85 trigger-gated); Phase 6 prep work behind OQ-DEC1 settlement; Issue #62 validator soft-warns; Issue #64 CB-E-63 re-scoping; #91 duplicate ADR 0052; #92 cohort_id lingering migration; **#113 CLOSED at S-0145 per ADR 0079**. Issue #2 (mempalace wing-name derivation) stays OPEN with S-0132 recurrence comment; upstream-blocked.

**S-0145 verification (closed in-session).** All Phase 1–4 empirical exercises succeeded: mempalace 3.3.5 smoke checks green (version + status + probe_palace + MCP vector search); 27 pytests for the new tool green; live palace converged to threshold=100 via apply path (backup at `~/.mempalace/palace.S-0145-pre-threshold-switch`); idempotency confirmed; boot probe surfaces consistency correctly. Forward-pointer (post-deploy verification, no in-session work): next 5–10 session boots should not see `mempalace_hnsw_divergence` re-fire; first natural bulk rebuild post-deploy measures the threshold=100 overhead empirically.

Plan file (S-0145 approved + revised mid-session at Phase 1.5a per user pushback on the threshold-value mechanism): [`~/.claude/plans/twinkling-finding-kitten.md`](~/.claude/plans/twinkling-finding-kitten.md).

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
