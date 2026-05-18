# Project State

> The single file every session reads first. Names what's current and what's next. Updated at every build-session close.
>
> **Scope discipline.** This file describes present state only. Session-by-session history lives in `engine/session/archive/S-NNNN.json` (canonical structured archive per ADR 0042) and `engine/changelog/<YYYY>/S-NNNN-*.md` (per-session entries per ADR 0092; the pre-S-0198 monolithic ENGINE_LOG.md is byte-preserved at `engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`). Cross-reference into those surfaces; do not duplicate their content here. The 37 prior-session prose rows S-0081–S-0119 retired at S-0121 per audit-session inline cleanup — they were duplicating archive + changelog content. Any addition to this file must answer: *would a session reading only STATE.md need this to know what's current?* If the content is "what happened last session," it belongs in the archive + changelog entry.

## Current

| Field | Value |
|---|---|
| **Project** | Paideia — knowledge mastery app on a pedagogical dependency graph |
| **GitHub** | https://github.com/StarshipSuperjam/paideia (OSS, Apache 2.0; public-flip landed at S-0130 with tag [`oss-flip-v1.0.0`](https://github.com/StarshipSuperjam/paideia/releases/tag/oss-flip-v1.0.0)) |
| **Current phase** | **Phase 5 — Philosophy subdomain seeding (closed; S-0045 → S-0076; production-audit closeout at S-0122; production-audit follow-up migrations at S-0123).** 380 nodes + 533 edges (was 536 pre-S-0123; -4 from 0063 prunes, +1 from S-0155 migration 0065); 516 `pedagogical_prerequisite` + 17 `historical_influence` (predicate first-use at S-0123 per ADR 0061 product). Phase 5 build closeout report at [`engine/build_readiness/phase_5_closeout.md`](build_readiness/phase_5_closeout.md); production-audit findings at [`engine/build_readiness/phase_5_production_audit_findings.md`](build_readiness/phase_5_production_audit_findings.md); audit-system-input at [`engine/build_readiness/phase_5_audit_system_input.md`](build_readiness/phase_5_audit_system_input.md); follow-up migrations at [`product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql`](../product/seed-graph/migrations/0061_seed_historical_influence_retyping_part1.sql) / [`0062_seed_direction_flips_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_part1.sql) / [`0062_seed_direction_flips_revert_part1.sql`](../product/seed-graph/migrations/0062_seed_direction_flips_revert_part1.sql) / [`0063_seed_weak_edge_cleanup_part1.sql`](../product/seed-graph/migrations/0063_seed_weak_edge_cleanup_part1.sql) / [`0064_seed_evidence_annotations_part1.sql`](../product/seed-graph/migrations/0064_seed_evidence_annotations_part1.sql). T1-A through T1-D closed for [`engine/tools/fetch_structural_reference.py`](tools/fetch_structural_reference.py) at S-0122 closeout. **Phase 6 self-correction master plan** unblocked at S-0152 via OQ-DEC1-A/B/C/D tension-set settlement (product ADRs 0085–0088); audit-side closeout + follow-up execution complete. **Phase 6 scope expanded at S-0202** via [ADR 0094 product](../product/adr/0094-phase-6-scope.md) to include Tier-A substrate redesign (Clusters 1-5) BEFORE the SEP/embedding self-correction work commits node-table-dependent migrations — dependency order 1 → 2 → 4 → 3 → 5 per synthesis.md; per-cluster product ADRs + migrations land in Session δ₂+ and subsequent build sessions; SEP backfill + embedding work per [ADR 0086](../product/adr/0086-model-agnostic-embedding-storage-architecture.md) sequences AFTER Tier-A migrations so the five semantically-rich fields (`node_type` / `disciplinary_domain` / `granularity` / `canonical_sources` / `misconceptions`) are present at backfill time. **The OSS+BYOK three-session refactor completed: Session A at S-0128 ([ADR 0065](../product/adr/0065-oss-pivot-and-byok-disposition.md) supersedes 0029 + 0035); Session B at S-0129 (downstream doc rewrites); Session C at S-0130 (LICENSE Apache 2.0 + NOTICE/CONTRIBUTING/CODE_OF_CONDUCT authoring + SECURITY.md/README.md OSS rewrites + 141-file PII path sweep + `.claude/settings.json` cleanup; public-visibility flip held at halt-and-confirm gate at session close).** **SWE-hardening rollout — Tier 1 CLOSED, Tier 2 CLOSED entirely, Tier 3 #76 CLOSED.** Tier 1 closed: #65 lockfile (S-0127 / ADR 0064); Pairing B #68 CI mirror + #69 branch protection (S-0131 / ADR 0065 engine + ADR 0066); Pairing A #66 gitleaks + #70 bandit (S-0132 / ADR 0067 + ADR 0068); #67 Dependabot (S-0133 / ADR 0069). Tier 2 closed: Pairing A #70 bandit SAST (S-0132 / ADR 0068, paired with #66); Pairing C #73 `/review` + #74 `/security-review` (S-0134 / ADR 0070 + ADR 0071); #75 frontend-ui-engineering modular split via `/frontend-discipline` + `/paideia-frontend-overlays` (S-0135 / ADR 0072 + ADR 0073); #71 pytest-cov coverage floor (S-0136 / ADR 0074; measured baseline 80%, floor 78%); #72 GitHub issue templates (S-0137 / ADR 0075). Tier 3 first-closure: #76 `/ship` multi-model orchestration (S-0148 / ADR 0081 — composes Tier-2 #73 + #74 + #71). **S-0138 closed the S-0137 in-context harness-allowlist over-reach** via `engine/tools/build_lifecycle_push.py` (sibling to `routine_lifecycle_push.py` per ADR 0054) + new engine ADR 0076. **S-0139 closed analysis-outcome [Issue #81](https://github.com/StarshipSuperjam/paideia/issues/81)** (narrowed at boot — lifecycle-state half already in place) via engine ADR 0077: "Alternatives Considered" template section + Deprecated ADRs join `validate_adr_back_reference_orphan`. ADR collection: **94 (87 Accepted + 7 Superseded; 51 engine + 43 product)** — product ADRs 0093 + 0094 landed at S-0202 (PDG papers extraction pre-phase Session δ₁ — [`Phase 6 product-trajectory formalization`](../product/adr/0093-phase-6-product-trajectory-formalization.md) + [`Phase 6 scope expansion to include Tier-A substrate redesign`](../product/adr/0094-phase-6-scope.md); first two of Session δ's four foundational ADRs; tool-stack ADR + learning-outcome taxonomy ADR + 3 Session-α coordination questions + 8 `kant_walkthrough.md` §6.7 D1-D8 schema items defer to Session δ₂+); engine ADR 0092 landed at S-0198 (per-session changelog directory replaces monolithic ENGINE_LOG.md; supersedes the ENGINE_LOG-naming/structure clauses of ADR 0037; engine/product wall partition + CHANGELOG.md filename reservation remain Accepted; ADR 0037 flips to Superseded in part; `engine-v0.1.0` tag cuts the foundation close); engine ADR 0091 landed at S-0188 (engine-memory substrate SQLite + FTS5; supersedes ADR 0090 because Issue #134 falsified its commitment 2a; ADRs 0090, 0056, 0079 flip to Superseded; ADR 0057 amended in-body for the substrate-coupled cluster-detection paragraph; 5-session implementation S-0189 → S-0193 tracked at [Issue #138](https://github.com/StarshipSuperjam/paideia/issues/138)); engine ADR 0079 amended at S-0187 (new "Amendment (S-0187): in-rebuild threshold override" subsection; superseded the next session by ADR 0091); engine ADR 0090 landed at S-0185 (Phase-6 recall-substrate decision; A1-PROPER comprehensive in-project fix campaign with scheduled maintenance + upstream coordination + empirical investigation; substrate preserved; closed Issue #131 — both superseded at S-0188); engine ADR 0089 landed at S-0163 (Skill ↔ Layer-1 procedure-parity validator check; closes Issue #129); engine ADR 0084 landed at S-0151 (pushback-rule extraction-step extension; closes Issue #77); product ADRs 0085–0088 landed at S-0152 (OQ-DEC1-A/B/C/D tension-set settlement; Phase 6 unblocked). The OQ-DEC1 settlements draw from the 0085–0088 range because engine ADRs 0066–0084 occupy that part of the shared sequence per ADR 0037; product ADRs 0093 + 0094 draw from 0093–0094 because engine ADRs 0089–0092 occupy 0089–0092 in the shared sequence. Full session-by-session history in [`engine/changelog/`](changelog/) (per ADR 0092; historical archive at [`engine/changelog/_history/ENGINE_LOG-pre-0.1.0.md`](changelog/_history/ENGINE_LOG-pre-0.1.0.md)). |
| **Last session** | **S-0202 (2026-05-18, interactive build) — PDG papers extraction pre-phase Session δ₁: first two of Session δ's four foundational ADRs landed.** Drafted [`product/adr/0093-phase-6-product-trajectory-formalization.md`](../product/adr/0093-phase-6-product-trajectory-formalization.md) (formalizes the 2026-05-14 user-settled trajectory bullet from HANDOFF.md as a binding ADR — four commitments specialized from ADR 0065 for Phase 6 substrate work: NO LMS-integrated tooling in Paideia's own releases [third-party OSS forks not foreclosed]; individual-only product scope re-affirmed; BYOK execution surface = iOS Keychain client-side, web visualizer BYOK shape EXPLICITLY deferred to Phase 8/9 implementation session; retention-mechanic exclusion holds per ADR 0065 commitment 6 threat-shape test) + [`product/adr/0094-phase-6-scope.md`](../product/adr/0094-phase-6-scope.md) (Phase 6 expands to include Tier-A substrate redesign Clusters 1-5 BEFORE SEP/embedding self-correction work commits node-table-dependent migrations; dependency order 1→2→4→3→5 per synthesis.md; SEP backfill operates on Tier-A-redesigned schema; Tier B/C/D/E defer to Phase 7+ or out-of-scope per ADR 0093 commitments 1+2). **Key in-session reframing for ADR 0094:** HANDOFF.md's four-option framing (A expand-all-17 / B narrow-to-Tier-A / C halt / D rescope) reduced after foreclosing C (per ADR 0093 commitment b) and dropping D (underspecified); synthesis.md §"Phase 6 master-plan-input subsection" supplied the empirically-grounded binary (Option α expand-Phase-6-to-include-Tier-A-before-SEP-backfill vs Option β proceed-narrow-accept-re-backfill); Option α chosen on embedding semantic-quality argument (per adversarial_review.md E.12.2 the five Tier-A fields most affect embedding quality) + quality-first posture per pushback drawer 1dc03200. **ADR 0084 extraction step triggered for ADR 0094** (contract-shape-change class): seven load-bearing premises authored with falsifiers + dispositions; premises 2, 3, 6 surfaced as unverifiable-in-context with named T1-A / T1-B / T2-A readiness criteria. Two engine_memory `decisions` drawers paired (e8d5de6b for 0093, 6d04110d for 0094) per two-layer recording. product/adr/README.md index updated (count 41→43). Approved plan: [`~/.claude/plans/breezy-percolating-wilkinson.md`](~/.claude/plans/breezy-percolating-wilkinson.md). Detail in [`engine/session/archive/S-0202.json`](session/archive/S-0202.json). |
| **Pre-S-0202** | **S-0201 (2026-05-17/18, interactive build) — PDG papers extraction Session γ: foundational reading against the four kant_walkthrough.md §6.6 reading items (F1-F4) + inline release of the S-0193 mempalace backup tarball.** Authored [`engine/build_readiness/pdg_papers_extraction/foundations.md`](build_readiness/pdg_papers_extraction/foundations.md) (473 lines) answering F1 (Meyer & Land threshold concepts), F2 (Spiro CFT + `bridge_concept` literature grounding — coinage finding), F3 (Middendorf & Pace bottleneck-vs-threshold distinction — subset relationship), F4 (Husserl primary-source verification — majority-reading-plus-refining-minority). §7.2 per-D-item bearing table maps F1-F4 onto §6.7 D1-D8. §7.3 two recommendations for Session δ (multi-valued `node_type`; D8 procedure operational on migration day 1). Quality-first posture. Inline housekeeping: released S-0193 mempalace backup tarball (167MB); pruned resolved HANDOFF section. Saved engine_memory lesson drawer on per-enum-value literature checks. Detail in [`engine/session/archive/S-0201.json`](session/archive/S-0201.json). |
| **Pre-S-0201** | **S-0200 (2026-05-17, interactive build) — PDG papers extraction Session β: Kant/phenomenology walkthrough against actual Paideia data + inline housekeeping (#146 main repo `.venv` iCloud corruption rebuild + #147 `engine/changelog/**/*.md` to `OPERATIONAL_ALLOWLIST` after ADR 0092 cutover).** Authored [`engine/build_readiness/pdg_papers_extraction/kant_walkthrough.md`](build_readiness/pdg_papers_extraction/kant_walkthrough.md) (601 lines) walking 8 data-points through the proposed schema from `synthesis.md` Clusters 2/4/5/8. Findings: 5 schema accommodations + 5 schema conflicts + 5 schema gaps + 8 Session δ adjudication items + 4 Session γ reading items (F1-F4 answered at S-0201). Detail in [`engine/session/archive/S-0200.json`](session/archive/S-0200.json). |
| **Pre-S-0200** | **S-0199 (2026-05-17, interactive build) — PDG papers extraction Session α: cross-reference audit of 17 synthesis clusters against the 92 ADRs.** Authored [`engine/build_readiness/pdg_papers_extraction/adr_cross_reference_map.md`](build_readiness/pdg_papers_extraction/adr_cross_reference_map.md) (605 lines). Surfaced three coordination questions Session δ must adjudicate (node_type enum ↔ ADR 0008; institutional-vs-individual scope under ADR 0065; BYOK execution-surface per cluster). Inline housekeeping. Detail in [`engine/session/archive/S-0199.json`](session/archive/S-0199.json). |
| **Last build session** | **S-0202 (2026-05-18) — see Last session row.** |


## Next session work item

**S-0202 closed at S-0202.** PDG papers extraction pre-phase Session δ₁ complete — [`product/adr/0093`](../product/adr/0093-phase-6-product-trajectory-formalization.md) (Product Trajectory formalization) + [`product/adr/0094`](../product/adr/0094-phase-6-scope.md) (Phase 6 Scope expansion to include Tier-A substrate redesign Clusters 1-5) landed; ADR collection 92→94. Two `decisions`-room engine_memory drawers paired. Session δ's remaining two foundational ADRs (tool-stack + learning-outcome taxonomy) + 3 Session-α coordination questions + 8 `kant_walkthrough.md` §6.7 D1-D8 schema items defer to Session δ₂+.

**S-0203 — Next session work item: user picks.** Open natural-next items:

- **PDG papers extraction — Session δ₂** per HANDOFF.md PDG entry. Substantive deliberation session — drafts the remaining two foundational ADRs (tool-stack [Postgres+JSONB vs Neo4j vs RDF/Jena — adversarial E.10.3 MUST settle before any Tier-A migration]; learning-outcome taxonomy [Bloom vs SOLO vs Decoding-the-Disciplines vs Fink vs synthesis default]) AND adjudicates as many of the three Session-α coordination questions + eight `kant_walkthrough.md` §6.7 D1-D8 items as fit within one session. Per the S-0202 plan-mode design, Cluster 4 cluster-implementation ADR (Session δ₃+) depends on coordination question #1 + D1-D5 + D7-D8; Cluster 5 depends on D6 + D7; Cluster 3 depends on the learning-outcome taxonomy ADR. The natural δ₂ ordering: tool-stack ADR first (gates Cluster 1+ migration schema shape per premise P5 in ADR 0094); coordination question #1 second (gates Cluster 4 ADR shape); learning-outcome taxonomy ADR third (gates Cluster 3 ADR shape).
- **PDG Session ε prep** — adversarial residue adjudication (19 deferred findings from Session α). Still not the natural next step — Session δ₂ should run first.
- **Inline-fix possibilities:** Pre-existing `adr_back_reference_orphan` soft-warns on ADRs 0093 + 0094 will resolve naturally when downstream cluster-implementation ADRs cite them. No bounded housekeeping items currently named.

**Carry-forward open questions from S-0201's `foundations.md` (not session-sized work — input substrate):**

- **Q1-F2 (Boundary-objects literature consult).** If Session δ₂'s Cluster 4 prep chooses to rename `bridge_concept` → `boundary_concept`, the Star & Griesemer (1989) / Akkerman & Bakker (2011) literature carries the definitional precision Session δ₂ would inherit. Brief WebFetch pass at Session δ₂ boot suffices.
- **Q1-F4 (Tewes 2018 to canonical_sources).** The Frontiers paper's refining-introspection thesis is part of the scholarly conversation; add to `phenomenology` node's `canonical_sources` field at the next canonical-source-authoring pass (Cluster 4 migration backfill or later).

**T1-A and T1-B closure tracking from ADR 0094 load-bearing premises subsection:**

- **T1-A** (premise 2 — Tier-A implementability without re-decomposition) closes at the first Tier-A cluster-implementation ADR landing — likely Cluster 1 (Contestability substrate) in Session δ₂+ or later.
- **T1-B** (premise 3 — D-item adjudication doesn't force Tier-D inclusion) closes at Session δ₂+'s D6 adjudication.
- **T2-A** (premise 6 — five-field embedding semantic-quality claim) closes at the Phase 6 self-correction master plan's embedding evaluation step per ADR 0086.

Tier-B trigger-gated issues (#22, #24, #79, #82, #83, #84, #85, #115, #117) remain in the backlog as load-bearing activation reminders per the S-0195 plan's triage; do NOT mass-close.

**T1-C of the per-session changelog first-exercise note** closes when the aggregator runs against ≥2 entries (natural exercise at the next release-prep session OR explicit invocation). S-0198 + S-0200 + S-0202 entries now exist; aggregator will run cleanly against either ≥2-count.

**Carried open items:**

- **Worktree-local `engine/.memory/engine_memory.sqlite3` stale files** in pre-S-0193 worktrees — the resolver fix means new sessions read the canonical main-repo file, but worktrees that initialized before S-0193 may carry a local file (harmless, gitignored, can be deleted manually).
- **Eloquent-taussig worktree's stuck validate.py process** (PID 95852 at S-0200 close; 18h+ runtime, 0.0% CPU, connected to Supabase via TCP socket awaiting response). Defunct process from a prior session that held the postgres connection open; killing it isn't urgent (no shared-state corruption risk) but worth a clean-up sweep when convenient.


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
