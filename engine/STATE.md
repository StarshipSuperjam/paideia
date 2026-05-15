# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/ENGINE_LOG.md` (Keep-a-Changelog-style material-change entries). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + ENGINE_LOG content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + ENGINE_LOG.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 533 edges (was 536 pre-S-0123; -4 from 0063 prunes, +1 from S-0155 migration 0065); 516 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. Phase 6 self-correction master plan **unblocked at S-0152** via OQ-DEC1-A/B/C/D tension-set settlement (product ADRs 0085–0088); the audit-side closeout + follow-up execution is complete. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 CLOSED, Tier 2 CLOSED entirely, Tier 3 #76 CLOSED.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks + #70 bandit (S-0132 / ADR 0067 + ADR 0068); #67 Dependabot (S-0133 / ADR 0069). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66); Pairing C #73 `/review` + #74 `/security-review` (S-0134 / ADR 0070 + ADR 0071); #75 frontend-ui-engineering modular split via `/frontend-discipline` + `/paideia-frontend-overlays` (S-0135 / ADR 0072 + ADR 0073); #71 pytest-cov coverage floor (S-0136 / ADR 0074; measured baseline 80%, floor 78%); #72 GitHub issue templates (S-0137 / ADR 0075). Tier 3 first-closure: #76 `/ship` multi-model orchestration (S-0148 / ADR 0081 — composes Tier-2 #73 + #74 + #71). **S-0138 closed the S-0137 in-context harness-allowlist over-reach** via `engine/tools/build_lifecycle_push.py` (sibling to `routine_lifecycle_push.py` per ADR 0054) + new engine ADR 0076. **S-0139 closed analysis-outcome [Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81)** (narrowed at boot — lifecycle-state half already in place) via engine ADR 0077: "Alternatives Considered" template section + Deprecated ADRs join `validate_adr_back_reference_orphan`. ADR collection: **89 (85 Accepted + 4 Superseded; 48 engine + 41 product)** — engine ADR 0089 landed at S-0163 (Skill ↔ Layer-1 procedure-parity validator check; closes Issue #129); engine ADR 0084 landed at S-0151 (pushback-rule extraction-step extension; closes Issue #77); product ADRs 0085–0088 landed at S-0152 (OQ-DEC1-A/B/C/D tension-set settlement; Phase 6 unblocked). The OQ-DEC1 settlements draw from the 0085–0088 range because engine ADRs 0066–0084 occupy that part of the shared sequence per ADR 0037. Full session-by-session history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md). |
| **Last session** | **S-0184 (2026-05-15, interactive build) — health-check audit at the cadence trigger (overdue-catchup; `slots_since=22 > cadence=20`).** Audit window S-0163 → S-0183 (21 sessions, 5 interactive + 16 routine). Two non-obvious findings: (A) **MemPalace retrieval is broken in three reinforcing ways** — HNSW UNKNOWN, upstream wing-filter throws Issue #1, BM25 fallback returns mining pollution (the prescribed `pushback`/`lesson` cluster reading per ADR 0057 element 4 is structurally un-runnable in current substrate); (B) **persistent-warn surface saturated** — 7 categories at ≥10 persistence, all annotated baselines, alarm-too-noisy-to-alert pattern. Two user-pre-named findings adjudicated inline: Finding-MEMPALACE → option (c) settle Phase-6 recall-substrate decision NOW → [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131); Finding-ENGINE-LOG → option (d) cut 0.1.0 + structural split + duplication audit → [Issue #132](https://github.com/StarshipSuperjam/paideia/issues/132); Finding B → option B1 separate annotated-baselines bucket → [Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133). Inline cleanups: STATE.md prune of accreted verification rows (this session). All five S-0162 findings (#127, #128, #129, plus folded fit-warn, plus inline) closed at S-0163 — the audit-to-fix pipeline worked end-to-end. Cadence stays at 20. Report at [`docs/health-checks/S-0184.md`](../docs/health-checks/S-0184.md); detail in [`engine/session/archive/S-0184.json`](session/archive/S-0184.json). |
| **Previous interactive build session** | **S-0183 (2026-05-15, interactive build) — T-SEED-QA disposition.** Migration [`0066`](../product/seed-graph/migrations/0066_seed_qa_disposition_reversed_part1.sql) (7 C1 reversals via DELETE+INSERT, clean-provenance posture) + [`0067`](../product/seed-graph/migrations/0067_seed_qa_disposition_rewrites_part1.sql) (13 C3 summary rewrites per topic-handle-first pattern); [ADR 0059](adr/0059-audit-time-structural-reference-fetching.md) Consequences amended with the inline-`evidence` gold-signal lesson; [Issue #130](https://github.com/StarshipSuperjam/paideia/issues/130) filed for the 9 "target is more general" Defensible-sub-shape rubric calibration. Graph state: 380 nodes + 516 prereq + 17 historical_influence (totals unchanged); `graph_version` stays at 16. The T-SEED-QA target is fully complete (20/20). Detail in [`engine/session/archive/S-0183.json`](session/archive/S-0183.json). |
| **Previous interactive deliberation session** | **S-0171 (2026-05-14, interactive build) — PDG papers deep extraction + 6-session pre-phase deliberation plan.** Two academic papers processed through a 5-lens × 66-sub-concern pipeline. Top finding (user-confirmed): the current Paideia graph (380 / 533 / 2) is materially under-modeled at the substrate level. 5 decisions settled (Paideia product trajectory; two-bias-surface partition; contestability is atomic; mass-retyping default reversed; quality-first deliberation posture). 17 integrated clusters across 5 tiers; 22 adversarial findings. Pre-phase plan (Sessions α-ζ) authored — see HANDOFF.md. Detail in [`engine/session/archive/S-0171.json`](session/archive/S-0171.json). |
| **Previous routine session** | **S-0182 (2026-05-15, routine — `T-SEED-QA` SQA-20 closeout, FINAL).** Census closeout aggregation: [`engine/build_readiness/seed_qa_findings.md`](build_readiness/seed_qa_findings.md). **Headline rates: C1 = 7/516 = 1.36% (all Reversed); C2 = 0/380; C3 = 13/380 = 3.4%.** C1 drift vs the 13% production-audit baseline: ~9.5× below; cross-bridge fortification per 0061–0065 durably held. The T-SEED-QA target is fully complete (20/20 tasks). Detail in [`engine/session/archive/S-0182.json`](session/archive/S-0182.json). |
| **Last build session** | **S-0184 (2026-05-15) — see Last session row.** |


## Next session work item

**Three S-0184-audit-spawned work items, plus the carried-over PDG papers Session α.** All four are session-sized; user adjudication picks order.

**[Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) — Phase-6 recall-substrate decision ADR (Finding-MEMPALACE option c).** The S-0184 audit's freshness probe found MemPalace retrieval broken in three reinforcing ways (HNSW UNKNOWN; upstream wing-filter throws Issue #1; BM25 fallback returns mining pollution); user adjudicated against a recurring-fix routine (which would only address mode 1) in favor of settling the substrate decision. Author an ADR deliberating: durable fix campaign vs. git-grep-against-tracked-ADR-files as the substrate vs. Postgres+pgvector. **Trigger:** ideally lands BEFORE PDG papers Session α (which depends on decision-drawer recall) OR Session α dogfoods git-grep-only retrieval. Session-sized.

**[Issue #132](https://github.com/StarshipSuperjam/paideia/issues/132) — ENGINE_LOG cut 0.1.0 + structural split + duplication audit (Finding-ENGINE-LOG option d).** ENGINE_LOG.md is 2,548 lines, zero prior cuts; foundation closed per the file's own preamble convention (`0.1.0 at foundation close`). Three-part work: (1) duplication-audit current `[Unreleased]` against archive content; (2) cut `[0.1.0] - <date>`; (3) structural split — historical sections move to `engine/ENGINE_LOG_HISTORY.md` not loaded by default. Session-sized.

**[Issue #133](https://github.com/StarshipSuperjam/paideia/issues/133) — Persistent-warn-surface annotated-baselines bucket (Finding B option B1).** 7 categories at ≥10 persistence saturate the boot persistent-warn surface; the alarm-too-noisy-to-alert pattern means open Issues like #125 (firing 21/30) get ignored. Three-part work: (1) `validate.py` change to filter annotated baselines from boot surface (per-commit firing unchanged); (2) annotation inventory — confirm/tighten reasons in `tools-validate-interpretation.md`; (3) `engine/operations/soft-warn-lifecycle.md` + ADR 0042 amendment naming the new bucket as a formal disposition. Session-sized; structurally upstream of acting on the 7 saturating categories themselves.

**PDG papers Session α — Cross-reference audit against 89 ADRs** (carried from S-0171 / HANDOFF.md). Map each proposed cluster against intersecting/conflicting/extending ADRs. Output: `engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md`. **Coupling:** depends on decision-drawer recall; if Issue #131 settles on git-grep substrate, Session α runs against that; if it settles on a fix campaign, Session α may follow the fix.

**Routine work.** The T-SEED-QA target is fully complete (20/20). No routine target authored. Routine boots will exit cleanly until a new target is authored (likely as part of the Phase 6 master-plan work that follows the OQ-DEC1 settlement and the recall-substrate decision).

**PDG papers pre-phase plan (carried from S-0171; full detail in HANDOFF.md).** Sessions α through ζ run the deliberation-first sequence before any substrate code lands: α (cross-reference audit; the next session item above) → β (Kant/phenomenology walk-through against actual Paideia data) → γ (foundational reading: Meyer & Land / Middendorf & Pace / Spiro / Falmagne) → δ (four foundational product ADRs: Phase 6 scope, tool-stack, learning-outcome taxonomy, product-trajectory commitment) → ε (adversarial-residue adjudication of the 19 deferred findings) → ζ (synthesis + Issue-draft revision; only then are the 17 Issues filed). Decisions settled in S-0171 (record in product ADRs in Session δ): (1) Paideia product trajectory — learner-facing + OSS-forkable, no LMS-integrated tooling on user-direct projects; (2) two-bias-surface partition — graph-topology vs LLM-mediated bias; (3) contestability is atomic — confidence + provenance + counterexamples + version history land as a unit; (4) mass-retyping default reversed — existing 516 prereq edges retype to `soft_prerequisite` not `hard_prerequisite`; (5) quality-first deliberation posture.

**Phase 6 master plan authoring (now unblocked per OQ-DEC1 settlement at S-0152 — ADRs 0085–0088).** The master plan should sequence: (1) `users.embedding_model` + `embedding_dims` metadata schema (depends on ADR 0086); (2) first `vector` partition migration + `node_embeddings_<dim>` table; (3) `sep_chunks` junction-table migration; (4) the 380-node SEP backfill batch (~19 hours); (5) entity-resolution-service application-code surface; (6) tension-log emission scaffolding. **Coupled to Issue #131 outcome** — if the recall-substrate decision settles on Postgres+pgvector, this work absorbs decision/lesson drawer storage too.

**Ready-to-execute alternatives (zero-blocker, can fire before Phase 6 master plan if user prefers):**

- **[Issue #115](https://github.com/StarshipSuperjam/paideia/issues/115)** — `node_class` schema extension (Phase 5 audit Proposal 4 follow-up). Trigger-gated on Phase 6 self-correction's node-quality-tagging master plan landing; now eligible since OQ-DEC1 settled.
- **[Issue #22](https://github.com/StarshipSuperjam/paideia/issues/22)** — Metabase (or alternative BI) evaluation. Trigger-gated on Phase 6 telemetry volume; still trigger-gated.
- **[Issue #24](https://github.com/StarshipSuperjam/paideia/issues/24)** — Graph renderer for the seed graph (local CLI MVP, hostable-for-feedback aspiration). Session-sized; zero-blocker; post-P5-closeout trigger met.
- **[Issue #64](https://github.com/StarshipSuperjam/paideia/issues/64)** — Re-scope CB-E-63 direction flip alongside the 4-node intentionality/meaning/proposition/propositional_attitude cluster. The Issue body recommends deferring to Phase 6 audit infrastructure; that infrastructure can now be built.
- **First natural `/ship` invocation** (Tier-2 closeout for [`engine/build_readiness/ship_skill_first_exercise.md`](build_readiness/ship_skill_first_exercise.md)). Not a session in itself — fires when any S-0153+ session pre-merges a substantive change. Record in `outcome_summary`.

Tier 3 items remain trigger-gated (#79 performance-optimization; #80 CODEOWNERS ADR-promotion-gated; #82 release tagging; #83 SBOM; #84 repo-health metrics; #85 API documentation discipline trigger-gated on Phase 6+).

**Open Issues backlog after S-0184: 18.** Three new at S-0184 (audit-spawned): [#131](https://github.com/StarshipSuperjam/paideia/issues/131) Phase-6 recall-substrate decision ADR, [#132](https://github.com/StarshipSuperjam/paideia/issues/132) ENGINE_LOG cut+split+audit, [#133](https://github.com/StarshipSuperjam/paideia/issues/133) persistent-warn-surface annotated-baselines bucket — all session-sized and `health-check-finding`-labeled. Pre-existing 15: 2 upstream-blocked (#1, #2 — MemPalace); 6 trigger-gated (#79, #80, #82, #83, #84, #85); 3 session-sized ready-to-execute (#22, #24, #64); #115 (node_class schema, now eligible); #117 (migration-discipline GRANTs, trigger-gated); #125 (`/start-engine.md` thin-pointer conversion + SKILL parity gap — surfaced by S-0163 `skill_layer1_parity_drift`); [#130](https://github.com/StarshipSuperjam/paideia/issues/130) (T-SEED-QA rubric calibration question). Full session-by-session Issue-close history in [`engine/ENGINE_LOG.md`](ENGINE_LOG.md).

**Tier 1 verification closed at S-0147**: Dependabot's first PR batch arrived 2026-05-12 (5 days ahead of the expected Monday cadence). 11 PRs (#94–#105), all major-version bumps; the `pip-minor-and-patch` grouping correctly did NOT bundle them per ADR 0069 decision 3 — major bumps open individually by design. S-0147 processed all 11 end-to-end as the first natural exercise of the new ADR 0080 boot-time visibility mechanism (rebase onto current main + `uv lock` regen + force-push + CI green + squash-merge per PR). Empirical record updated declaratively in ADR 0069 per ADR 0062.

**Pairing C verification still pending**: first real invocation of `/review` and `/security-review` against substantive changes. Captured in ADR 0070's + ADR 0071's "Empirical record (pending)" subsections, or in the invoking session's `outcome_summary`. AI may surface invocation as a suggestion on substantive code changes (the user adjudicates).

**S-0135 verification still pending**: first real invocation of `/frontend-discipline` + `/paideia-frontend-overlays` against substantive frontend code (marketing-site authoring, knowledge-graph visualizer authoring, or Phase 6 SwiftUI entry — whichever opens first). Captured in ADR 0072 + 0073 "Empirical record (pending)" subsections.

**S-0136 verification closed in-session**: T1-A (CI green on deliverable push) verified via run [25753339781](https://github.com/StarshipSuperjam/paideia/actions/runs/25753339781) on SHA `9f8ea63` — both jobs `validate.py` + `pytest engine/tools` exit 0; `Run pytest engine/tools with coverage` step green against the post-S-0136 corpus (coverage 80% ≥ floor 78%). T1-B (gate fires red above floor) verified empirically in-session via direct `uv run coverage report --fail-under=99` → exit 2. Both Tier 1 readiness criteria closed; Tier 2 + Tier 3 forward-pointers per `pytest_cov_first_exercise.md`.

**Visual-identity ADR (future product session)**: needed before `/paideia-frontend-overlays` overlay 5 tightens from `FYI` to `Required`. Triggered when the user is ready to commit palette/type/motif specs to ADR contract; until then, overlay 5 references the working prototype as load-bearing context. Cascade per ADR 0041 will update the overlay skill in the same session the ADR lands.

**ADR 0035 ambiguity (resolved at S-0154).** [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106) closed — the user adjudicated Option A (inline clarification). ADR 0065 commitment 1 now carries an explicit scope clarification: "no web app" applies to the consumer learner-facing product distribution channel only; marketing/landing site + knowledge-graph visualizer + OSS community demo web surfaces are operational not product and are not foreclosed (the funnel-mechanic discipline per commitment 6 still binds them). The edit target was ADR 0065, not ADR 0035 — ADR 0035 was already `Superseded by ADR 0065` at S-0128, and commitment 1's platform language is preserved verbatim in ADR 0065. ADRs 0072 + 0073 + the `paideia-frontend-overlays` skill updated to cite the resolved ADR 0065 commitment 1.

**S-0137 verification (pending — first natural Issue filing)**: first real authoring through the new templates exercises the template chooser, required-field UI block, and auto-label behavior. Captured in ADR 0075's "Empirical record (pending)" subsection or the invoking session's `outcome_summary`.

**S-0138 verification (Tier 1 closed in-session at S-0138; Tier 2 partial after S-0139)**: `build_lifecycle_push.py` Tier 1 closed at S-0138 close via the session's own deliverable + close push exercises (dogfood). **Eager-claim mode first exercise closed at S-0139 boot** (commit `a739106` pushed via `python3 engine/tools/build_lifecycle_push.py eager-claim` → exit 0 + parent main FF'd cleanly; S-0139 deliverable + close pushes are the second + third natural deliverable-mode exercises). Tier 2 remaining forward-pointers per [`engine/build_readiness/build_lifecycle_push_first_exercise.md`](build_readiness/build_lifecycle_push_first_exercise.md): first refusal exercise (malformed lifecycle commit); first push-rejection exit-3 exercise.

**S-0139 verification (closed in-session)**: ADR 0077's deliverables verified end-to-end. Template change visible in `adr-authoring.md` between Decision and Consequences. ADR 0077 dogfoods the new section with four full Pros/Cons/Rejected-because alternatives. Validator extension: all 169 validate-tests green; 6 orphan-check tests green including the 2 new Deprecated coverage tests; full `validate.py` pass exits 0 with no new soft-warns (baseline carryover only: 23 issue_collision / 360 missing_rigor_score / 1 orphan_leaf). Issue #81 closed at session shutdown with comment naming ADR 0077 and the narrowed-scope discovery. MemPalace decision drawer `drawer_paideia_decisions_14689598e4bbbac248e785db` captures the four-alternative deliberation + the narrowed-scope discovery as load-bearing pattern.

**S-0148 verification (Tier 2 forward-pointers open).** Tier 1 closed at S-0148 (dogfood). Tier 2 forward-pointers per [`engine/build_readiness/ship_skill_first_exercise.md`](build_readiness/ship_skill_first_exercise.md): first non-dogfood `/ship` invocation; first NO-GO verdict with non-trivial finding; first override-attempt with anti-rationalization rebuttal; first sub-agent error path; first CI-fallback path; first invocation against a routine-mode session.

Plan file (S-0162 approved): [`~/.claude/plans/i-would-like-to-ethereal-puppy.md`](~/.claude/plans/i-would-like-to-ethereal-puppy.md).

Plan file (S-0152 approved): [`~/.claude/plans/fuzzy-seeking-flute.md`](~/.claude/plans/fuzzy-seeking-flute.md).

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
