# ADR 0090 — Phase-6 recall-substrate decision: MemPalace preserved with active maintenance + upstream coordination

- **Status:** Accepted
- **Date:** 2026-05-15
- **Deciders:** S-0185

## Context

The S-0184 health-check audit's adversarial freshness probe per [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) element 3 found MemPalace retrieval broken in **three reinforcing ways** ([`docs/health-checks/S-0184.md`](../../docs/health-checks/S-0184.md) finding A):

1. **HNSW UNKNOWN.** `mempalace repair-status` reports `status: UNKNOWN` ("metadata has not been flushed yet"). The S-0163 `mempalace_hnsw_status_suspect` telemetry catches it but doesn't fix it. [ADR 0079](0079-hnsw-sync-threshold-tuning.md)'s S-0145 `sync_threshold=100` retrofit expected "≥150-session recurrence interval"; S-0184 found UNKNOWN at 39 sessions post-rebuild — **under the expected window**.
2. **Wing-filtered search throws upstream.** `mempalace search --wing paideia --room pushback` returns `Internal error: Error finding id` — upstream [MemPalace/mempalace#1082](https://github.com/MemPalace/mempalace/issues/1082) (project-side [Issue #1](https://github.com/StarshipSuperjam/paideia/issues/1)). ADR 0057 element 4's prescribed `pushback`/`lesson` cluster-reading workflow is structurally un-runnable in this code path.
3. **BM25 fallback returns mining pollution.** With vector search degraded and 98 wings of per-worktree auto-capture scatter (Issue #2), BM25 matches against captured terminal output rather than curated decision/lesson drawers. S-0184's three representative queries returned validator soft-warn dumps as top hits.

User adjudicated Finding-MEMPALACE option (c) — settle the substrate decision NOW — and filed [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) with three named alternatives: (A1) durable fix campaign; (A2) git-grep-against-tracked-ADR-files; (A3) Postgres + pgvector. This ADR settles which path.

### Investigation history

Four rounds of plan-mode pushback (user adjudication via AskUserQuestion + free-text pushback) drove the deliberation. The pushback rule per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) was active across all four:

- **Round 1.** Initial recommendation was a hybrid (A2 immediately + A3 as Phase-6+ trajectory). User: *"This feels like you are trying to ungate forward progress at the expense of durable solutions."* Hybrid surfaced as patch-and-run with hand-wavy deferral.
- **Round 2.** Pivoted to A3-now. User: *"This removes MemPalace from this project's tool stack. That's a huge change. Why wouldn't we have done this instead of choosing MemPalace in the first place? Are we sure this mitigation doesn't introduce new constraints that are being glossed over here?"* Triggered reading [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Project usage scope" and [`engine/docs/audits/mempalace-adversarial-review-S-0086.md`](../docs/audits/mempalace-adversarial-review-S-0086.md). Found:
  - MemPalace was chosen for capture-surface affordances (Stop/PreCompact hooks ship with it; ~19 MCP tools the AI invokes by name; verbatim conversation drawers; local-only no-API-cost; AAAK summarization for diary).
  - Project established a **scale-back precedent at S-0086** — KG, tunnels, AAAK-for-project-drawers retired via [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) Consequences amendment. The discipline is *narrow rather than replace*.
  - A3-now coupling costs glossed over: embedding-API recurring cost + network failure mode + vendor lock-in; hook rewrites; ~500+ drawer re-embedding migration; replacement of substantial S-0093 tooling (`mempalace_boot_search.py` + `scan_mempalace_citations.py`); ADR 0056 mechanical-adoption-check layer rewrite; multi-session ops-doc + skill + CLAUDE.md rewrites.
  - **Citation-telemetry signal:** `mempalace_zero_citations_after_search` fires 25/30 sessions per S-0184. Even when search runs, retrieved drawers aren't cited in `outcome_summary` / commits / diary. The project is *already* operating with near-zero retrieval signal.
- **Round 3.** Pivoted to A1-PROPER (comprehensive in-project fix campaign with scheduled maintenance + contract refinement + empirical investigation). User: *"Yes — A1-PROPER (Recommended)."*
- **Round 4.** User: *"And we're sure we aren't blindly throwing our hands in the air over breaks that could be fixed? Seems like people are tackling similar issues. See https://github.com/MemPalace/mempalace/pull/625 as an example..."* Triggered upstream investigation via `gh pr list` / `gh issue list` / `gh pr view`. Found:
  - PR #625 (the reference) — CLOSED with "superseded by recently merged PRs to develop." Upstream is responsive; ~5 PRs/month merged in the relevant window.
  - **Mode 1 upstream status:** [Issue #1489](https://github.com/MemPalace/mempalace/issues/1489) OPEN (the project's own filing per ADR 0079). Corroborating datapoint from @sarahnovotny on bulk-rebuild recurrence. Proposes `--hnsw-sync-threshold N` flag on `init` + `repair`. PR #1452 (avoid quarantining recoverable HNSW metadata) OPEN.
  - **Mode 2 upstream status:** Issue #1082 OPEN. **@meretrout correction comment TODAY (2026-05-15):** the failure is **scale/accumulation-bound**, not version-bound — reproducible at 328K drawers; **fresh small palaces work fine** at the same mempalace 3.3.5 + chromadb 1.5.9 versions. **Our palace is 22K drawers — well below the failure threshold @meretrout reproduced.** Mode 2 may not be load-bearing at our scale; needs empirical re-verification. PR #1463 OPEN: SQLite BM25 fallback on Chroma ID lookup divergence. PR #1396 MERGED (search retry; partial fix per upstream's own framing).
  - **Mode 3 upstream status:** **PR #1424 ALREADY MERGED** improves `_wing_from_transcript_path` to read `cwd` from the JSONL transcript (the canonical answer rather than path-suffix slicing). **PR #1511 filed today (2026-05-15)** adds `MEMPALACE_WING` env var explicit override layering on top of #1424. Our `mempalace-operations.md` description of the wing-derivation behavior is pre-#1424 — likely outdated; recent sessions may already be landing in `paideia` properly.

**Strategic shift.** The substrate question changes shape from *"MemPalace is broken; settle replacement"* to **"MemPalace is being actively fixed upstream; settle our coordination posture."** The project's role is **bridge-and-coordinate**, not abandon.

### Were prior fixes fantasy? No.

S-0078 rebuild tool ([ADR 0045](0045-shared-state-integrity-discipline.md) amendment), S-0088/S-0092 prune campaigns (Issues #40/#41 closed), S-0093 boot-search orchestrator + citation telemetry ([ADR 0056](0056-mempalace-mechanical-adoption-checks.md) S-0093 amendment), S-0145 ADR 0079 sync_threshold retrofit, S-0153 upstream Issue #1489 filing, S-0163 telemetry + SQLite-direct reads (Issues #127, #128) — all shipped working. ADR 0079's "≥150-session recurrence expected" was honest expectation, falsified at 39 sessions by S-0184. That is a **falsified premise to investigate**, not evidence the fix was fantasy.

What was missing across the prior fixes wasn't quality — it was **ongoing maintenance cadence**. Each fix was one-shot remediation. The recurrence is a scheduling gap layered on top of substrate behavior.

### Load-bearing premises

The four rounds of pushback exercised the [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step in practice. The premises this ADR's Decision rests on:

1. **The three modes are confirmed-broken at our scale and version.** *Falsifier:* empirical re-verification (Decision commitment 1) shows one or more modes don't reproduce against mempalace 3.3.5 + our 22K-drawer palace. *Test status:* not runnable in plan mode; the first commitment of the Decision IS the test. **Held loosely** — verification is part of the deliverable.
2. **Upstream timelines are reasonable enough to coordinate rather than fork.** *Falsifier:* months pass without any of #1489 / #1463 / #1511 merging. *Test status:* upstream merged 5+ relevant PRs in the April-May 2026 window (#1000, #1191, #1227, #1287, #1396, #1424) per `gh pr list`. **Accepted with the named risk.**
3. **The `mempalace_zero_citations_after_search` 25/30 telemetry signal indicates retrieval is currently low-utility.** *Falsifier:* AI invocation discipline is the cause (not retrieval quality), and improving discipline would restore citation rate. *Test status:* not runnable in plan mode; the ADR 0079 recurrence investigation (commitment 4) may surface adjacent evidence. **Accepted; sunset criterion in Consequences.**
4. **The S-0086 scale-back precedent is the right shape for this decision (narrow rather than replace).** *Falsifier:* upstream activity collapses and the substrate becomes durably broken; or migration cost becomes lower than expected. *Test status:* unverifiable in-context. **Accepted with named conditions for A3-now reconsideration (commitment 6).**
5. **The maintenance cadence is operationally affordable.** *Falsifier:* first-exercise shows shutdown overhead is material session-friction; rebuild fails in some session shape. *Test status:* unverifiable until first exercise. **Accepted; first-exercise readiness note covers verification.**

## Decision

The project preserves **MemPalace** as the durable semantic-memory substrate for Phase 6 and beyond. The substrate decision settles around six specific commitments:

1. **Empirical re-verification first.** Before wiring specific mitigations, probe current mempalace 3.3.5 behavior against the project's actual palace (S-0186 deliverable):
   - **Mode 1:** re-run `mempalace repair-status`; check `configuration.hnsw.sync_threshold` on both `mempalace_drawers` and `mempalace_closets` collections; verify whether HNSW UNKNOWN persists, and whether the threshold value drifted.
   - **Mode 2:** re-run `mempalace_search --wing paideia --room pushback` (the load-bearing wing-filter shape per ADR 0057 element 4). If it succeeds at our 22K-drawer scale, Mode 2 is not load-bearing for us and the contract refinement in commitment 2c is unnecessary.
   - **Mode 3:** run `mempalace_list_wings`; verify whether sessions post-PR-#1424 land in `paideia` (proper wing) or per-worktree hashes. If recent sessions land properly, the wing scatter is historical-only and the prune is one-shot.
2. **Maintenance for confirmed-broken gaps** (post-verification, S-0187+):
   - (a) **Mode 1 scheduled rebuild:** schedule [`mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) on a cadence informed by the ADR 0079 recurrence investigation (commitment 4). Per-shutdown if affordable; per-N-sessions if not. Bridge until Issue #1489 lands the upstream `--hnsw-sync-threshold N` flag (or until the project's existing [`mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) approach is shown sufficient).
   - (b) **Mode 3 prune:** one-time bulk [`prune_mempalace.py --audit-orphan-wings --apply`](../tools/prune_mempalace.py) if historical accumulation exists. Recurring schedule **only if** PR #1424 + #1511 don't suffice going forward (verified by step 1 Mode 3 probe).
   - (c) **Mode 2 contract refinement:** ADR 0057 element 4 in-body amendment to use unfiltered `mempalace_search` + caller-side wing/room filtering OR direct chromadb-SQLite reads (the path [`audit_mempalace()`](../tools/health_check.py) already takes per S-0163 #128 fix) — **only if** step 1 Mode 2 probe shows wing-filter still broken at our scale. Otherwise no contract change; the bug is upstream-tracked at Issue #1082 and out-of-scope at our palace size.
3. **Upstream coordination.** Active posture, not passive waiting:
   - Monitor MemPalace/mempalace issues #1082 / #1398 / #1489 and PRs #1463 / #1511 / #1452 / #1428.
   - When upstream fixes land that obsolete project workarounds, retire the workarounds per the existing disposition pattern: [`mempalace_set_sync_threshold.py`](../tools/mempalace_set_sync_threshold.py) retires when #1489 lands; ADR 0057 contract refinement (if authored under commitment 2c) retires when #1463 lands; per-worktree wing pollution prune (if scheduled under commitment 2b) retires when #1511 lands.
   - Comment on relevant upstream Issues with our use-case data (helps prioritization).
   - Consider contributing patches (e.g., our `mempalace_set_sync_threshold.py` pattern → upstream #1489's "option 1" as a PR).
4. **Empirical investigation of ADR 0079's falsified recurrence interval** (S-0186 deliverable): probe persist behavior, verify threshold setting (configuration channel vs metadata channel), check write-path distribution between `drawers` and `closets` collections, instrument the `_apply_batch` persist condition if necessary. Find out why HNSW UNKNOWN recurred at 39 sessions vs ≥150 expected. Findings inform the rebuild-cadence decision in commitment 2a and may produce an ADR 0079 amendment or its own follow-up ADR.
5. **Substrate preserved.** MemPalace remains the project's semantic-memory substrate. The capture surface (Stop/PreCompact hooks, `mempalace_add_drawer`, `mempalace_diary_write`) — *which is healthy per S-0184* — continues unchanged. ADR 0056 mechanical adoption checks continue. ADR 0057's adversarial-stance contract continues (element 4 contract refinement is conditional per commitment 2c, not posture change). The S-0086 scale-back precedent is the through-line: narrow when warranted, do not abandon.
6. **Open future option.** The A3 path (Postgres + pgvector as substrate) stays open for a future ADR if:
   - Phase 6 pgvector partition machinery (per ADRs [0086](../../product/adr/0086-model-agnostic-embedding-storage-architecture.md), [0087](../../product/adr/0087-two-hop-neighborhood-retrieval-shape.md), [0088](../../product/adr/0088-sep-chunk-resolver-index.md)) lands at scale AND the marginal cost of adding `decision_embeddings_<dim>` becomes small; OR
   - Upstream MemPalace fixes do not converge over the next 60 sessions and project workarounds become an unaffordable maintenance burden.
   
   This ADR does not preclude that future; it commits to MemPalace for the present and names the conditions under which A3 might be reconsidered.

## Alternatives Considered

Per [ADR 0077](0077-adr-template-alternatives-considered-section.md). The deliberation spanned four named alternatives plus the chosen path.

### A1-INITIAL — One-shot fix campaign (without scheduling discipline)

- **What:** Treat each of the three S-0184 modes as a discrete one-shot remediation (e.g., re-run ADR 0079 sync_threshold retrofit; re-run S-0088 prune batch; etc.). No ongoing maintenance cadence; no upstream coordination commitment.
- **Pros:** Cheapest path; the project already has the tooling for each remediation (`mempalace_rebuild_hnsw.py`, `prune_mempalace.py`, `mempalace_set_sync_threshold.py`); session-sized.
- **Cons:** This is essentially the path the project has been on across S-0078, S-0088, S-0145, and S-0163. The S-0184 recurrence at 39 sessions falsifies its sufficiency. Each prior fix shipped working but lacked maintenance cadence, and degradation recurred. Without scheduling discipline, the next audit will surface the same modes.
- **Rejected because:** the empirical record (S-0184 finding A) is the affirmative evidence against this path.

### A2 — git-grep-against-tracked-ADR-files as the recall substrate

- **What:** Retire `mempalace_search` from the load-bearing critical path. ADR contract recall moves to `git grep` against `engine/adr/*.md` + `product/adr/*.md`. Decision-drawer / pushback / lesson content reads move to direct chromadb-SQLite reads (the path `audit_mempalace()` already takes). MemPalace narrows to capture-only + diary read/write.
- **Pros:** Operationally minimal; zero ongoing maintenance overhead; durable (git is the project's source-of-truth); aligns with the project's S-0086 scale-back trajectory; preserves capture surface and diary which work today.
- **Cons:** Surrenders semantic similarity for decision-drawer recall preemptively. The 25/30 `mempalace_zero_citations_after_search` telemetry suggests we're already paying this cost — but the cost is paid because the *current* search is degraded, not because semantic similarity itself is unneeded. The Round 4 upstream investigation showed Mode 2 may not even be broken at our scale (@meretrout's 328K-drawer reproduction vs our 22K palace). Surrendering before verifying is premature.
- **Rejected because:** the empirical re-verification commitment in A1-PROPER (commitment 1) supersedes the need for preemptive surrender; we'll find out whether semantic similarity is actually working before retiring it. A2 also abandons the upstream coordination posture — gives up rather than waits-and-coordinates.

### A3-now — Postgres + pgvector substrate replacement

- **What:** Author migration `0068_drawer_recall_substrate.sql` with `decision_embeddings_<dim>` / `lesson_embeddings_<dim>` / `pushback_embeddings_<dim>` partition tables extending the [ADR 0086](../../product/adr/0086-model-agnostic-embedding-storage-architecture.md) per-dim pattern. Migrate ~500+ curated drawers via re-embedding. Author capture + retrieval tools replacing `mempalace_add_drawer` / `mempalace_search`. Replace `mempalace_diary_*` with either a Postgres table or JSONL in git. Rewrite ADR 0056 mechanical-adoption-check layer. Multi-session migration.
- **Pros:** Architecturally cleanest end-state; single substrate the project fully controls; no upstream dependency; semantic similarity preserved at scale. Aligns with Phase 6 partition pattern.
- **Cons:** Substantial migration cost (hook rewrites; ~500+ drawer re-embedding; replacement of S-0093 `mempalace_boot_search.py` + `scan_mempalace_citations.py`; ADR 0056 layer rewrite; ops-doc + skill + CLAUDE.md rewrites). Adds ongoing embedding-API dependency (recurring cost + network failure mode + vendor lock-in) that the project currently does NOT have. The S-0086 audit explicitly preferred narrowing over replacement. **Upstream activity (Round 4 finding) substantially obsoletes this path** — if PR #1424 already merged + PR #1511 / PR #1463 land, the substrate self-heals at upstream pace.
- **Rejected because:** pays substantial migration cost without addressing root cause (scheduling discipline). The Round 4 upstream finding showed the substrate is being actively fixed; the project's role is coordinate-and-bridge, not throw away.

### Hybrid — A2 immediately + A3 as Phase-6+ trajectory

- **What:** Restructure retrieval to git-grep + direct-SQLite immediately (A2 shape); defer A3 as a Phase-6+ trajectory when partition machinery lands.
- **Pros:** Operationally minimal now; nominally points at A3 as future durable answer.
- **Cons:** Patch-and-run by composition. The "Phase 6+ trajectory" has no decide-by trigger — it's "we'll do the durable thing later" with no commitment. Retains MemPalace in critical path for diary despite same chromadb open-path issues (HNSW UNKNOWN affects every chromadb open, not just vector search). Splits substrate ownership across three sub-substrates (git-grep + direct-SQLite + MemPalace-for-diary) — three things to maintain, not fewer.
- **Rejected because:** Round 1 user pushback: *"This feels like you are trying to ungate forward progress at the expense of durable solutions."* The framing was accurate.

### A1-PROPER — Comprehensive in-project fix campaign with scheduled maintenance + upstream coordination + empirical investigation (chosen)

- **What:** Six commitments per Decision section above.
- **Pros:** Preserves the substrate the project has built around. Trades modest ongoing cost (~30s rebuild per shutdown if needed + periodic pruning + 1 ADR amendment if needed + investigation work) for keeping all current affordances (capture surface; MCP affordance; diary; semantic similarity; ADR 0056 mechanical adoption checks; S-0093 boot-search orchestrator + citation telemetry). Empirical verification first means we don't commit to mitigations we may not need (post-PR-#1424, the wing-derivation may be working; post-22K-vs-328K, the wing-filter may not be broken at our scale). Upstream coordination posture means the project's workarounds retire as upstream fixes land, instead of compounding indefinitely.
- **Cons:** Posture-not-machinery for the upstream-coordination commitment (drift risk: a session may forget to check upstream status; same risk as the pushback rule itself). The maintenance cadence (commitment 2a) is operationally non-trivial. If empirical verification (commitment 1) shows all three modes broken at our scale AND upstream timelines collapse, the commitment 6 reconsideration trigger fires sooner than hoped.
- **Rejected because:** not rejected — chosen.

## Consequences

### In this session (S-0185)

- This ADR (`engine/adr/0090-phase-6-recall-substrate-decision.md`) lands at Accepted.
- See-also back-pointers added to ADRs [0056](0056-mempalace-mechanical-adoption-checks.md), [0057](0057-adversarial-stance-for-health-check-audits.md), [0079](0079-hnsw-sync-threshold-tuning.md) (cascade per [ADR 0041](0041-cascade-analysis-discipline.md)).
- First-exercise readiness note at [`../build_readiness/recall_substrate_fix_campaign_first_exercise.md`](../build_readiness/recall_substrate_fix_campaign_first_exercise.md) per [ADR 0053](0053-mechanism-first-exercise-gate.md). Trigger criterion #4 fires (Consequences span ≥3 ops docs OR ≥5 tooling files — ADR 0090 + ADR 0056 + ADR 0057 + ADR 0079 + mempalace-operations.md + first-exercise note = 6 surfaces).
- ENGINE_LOG `[Unreleased]` Added entry naming this ADR + the readiness note.
- STATE.md updated: ADR count 89 → 90; next-session-work rotation (Issue #131 closes; S-0186 work item is the empirical verification + ADR 0079 recurrence investigation; PDG papers Session α remains carried — substrate question is settled, even if execution is in progress).
- MemPalace `decision`-tagged drawer captures the four-round deliberation (capture surface works; `mempalace_add_drawer` is unaffected by the retrieval breakages).
- [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) closed with comment naming this ADR + A1-PROPER + the empirical-verification-first commitment + S-0186+ sequence.

### S-0186 deliverable (next session)

Empirical re-verification report at `engine/docs/audits/mempalace_state_S-0186.md` (or equivalent structured probe report). Covers commitments 1 + 4:

- Per-mode probes documented with command + output + finding.
- ADR 0079 recurrence investigation: persist behavior, threshold setting, write-path distribution.
- Findings inform whether commitment 2c (Mode 2 contract refinement) fires.
- Findings inform commitment 2a cadence decision (per-shutdown vs per-N-sessions).

### S-0187+ deliverables

- (a) Scheduled rebuild wiring (commitment 2a) into session-shutdown-sequence (or the cadence the investigation recommends).
- (b) One-time prune OR recurring prune cadence (commitment 2b) based on Mode 3 verification.
- (c) ADR 0057 element 4 in-body amendment (commitment 2c) ONLY IF Mode 2 verification warrants.
- (d) Operations doc updates documenting the new maintenance cadence in [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Maintenance probes" subsection.
- (e) Upstream coordination process documented in `mempalace-operations.md` (the watch-and-retire-workarounds pattern).
- Tests for any wiring changes.

### Cross-session consequences

- **Issues #1, #2 stay OPEN** (correctly tagged `upstream`) tracking the upstream MemPalace/mempalace Issues. Project-side Issues track *our impact*; they close when upstream resolves AND the project's workaround retires.
- **`mempalace_zero_citations_after_search` soft-warn** stays in the validator catalog. It may move from "persistent baseline" toward "informational" if the empirical verification + investigation produce evidence that the 25/30 ratio is retrieval-quality-driven (and the mitigations restore it) vs invocation-discipline-driven (where AI behavior change is the load-bearing fix).
- **A3 reconsideration triggers** (per commitment 6):
  - Phase 6 partition machinery lands at scale + decision_embeddings marginal cost is small;
  - OR 60 sessions pass without upstream convergence AND project workaround cost is unaffordable.
  
  Either trigger fires → new ADR supersedes or amends this one. Until then, this ADR is the contract.

### Sunset criterion

If three consecutive health-check audits (S-0205, S-0225, S-0245 at cadence-20) report no MemPalace-substrate findings AND the upstream coordination posture has retired ≥1 project workaround successfully, the ADR's "A1-PROPER posture" can transition from active maintenance to *steady-state observation*. The next health-check audit considers retiring or amending this ADR's commitments at that point.

## See also

- [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) — the mechanical adoption-check layer this ADR preserves; the `mempalace_zero_citations_after_search` soft-warn is the load-bearing telemetry input.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — element 4's cluster-reading workflow is conditionally refined per commitment 2c; the freshness-probe inventory's `pushback`/`lesson` cluster reading shape is contingent on the empirical verification.
- [ADR 0079](0079-hnsw-sync-threshold-tuning.md) — the prior fix campaign whose recurrence-interval premise was falsified by S-0184; commitment 4 commits to investigating why.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — the extraction-step rule this ADR dogfoods; four rounds of plan-mode pushback are the procedure-in-action.
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — the Alternatives Considered template this ADR dogfoods.
- [ADR 0086](../../product/adr/0086-model-agnostic-embedding-storage-architecture.md) — the per-dim partition pattern the A3 future option would extend.
- [ADR 0045](0045-shared-state-integrity-discipline.md) — the detection-side spine for HNSW divergence; `mempalace_rebuild_hnsw.py` was its consequence-deliverable.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the soft-warn lifecycle the persistent-warn surface participates in.
- [ADR 0041](0041-cascade-analysis-discipline.md) — the cascade discipline driving the See-also back-pointers in ADRs 0056 / 0057 / 0079.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — the first-exercise readiness gate; this ADR's first-exercise note covers it.
- [ADR 0022](0022-periodic-project-health-checks.md) — the periodic-audit cadence whose adversarial-stance refinement at ADR 0057 surfaced finding A.
- [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) — the operational surface; gains maintenance-cadence documentation in S-0187+ per Consequences.
- [`engine/operations/mempalace-tagging-conventions.md`](../operations/mempalace-tagging-conventions.md) — tag conventions the cluster-reading consumes.
- [`engine/docs/audits/mempalace-adversarial-review-S-0086.md`](../docs/audits/mempalace-adversarial-review-S-0086.md) — the S-0086 adversarial review whose narrow-rather-than-replace verdict this ADR continues.
- [`docs/health-checks/S-0184.md`](../../docs/health-checks/S-0184.md) — the audit that surfaced finding A.
- [`engine/build_readiness/recall_substrate_fix_campaign_first_exercise.md`](../build_readiness/recall_substrate_fix_campaign_first_exercise.md) — the first-exercise readiness note.
- [Issue #1](https://github.com/StarshipSuperjam/paideia/issues/1) — project-side tracking of upstream MemPalace/mempalace#1082.
- [Issue #2](https://github.com/StarshipSuperjam/paideia/issues/2) — project-side tracking of upstream wing-naming bug (now narrowed by upstream PR #1424).
- [Issue #131](https://github.com/StarshipSuperjam/paideia/issues/131) — closes; the S-0184 audit-spawned filing this ADR resolves.
- Upstream [MemPalace/mempalace#1082](https://github.com/MemPalace/mempalace/issues/1082) — Mode 2 wing-filter throws; scale-bound per @meretrout 2026-05-15 correction.
- Upstream [MemPalace/mempalace#1398](https://github.com/MemPalace/mempalace/issues/1398) — adjacent post-bulk-add transient case (partial fix merged via PR #1396).
- Upstream [MemPalace/mempalace#1489](https://github.com/MemPalace/mempalace/issues/1489) — the project's own filing per ADR 0079; proposes `--hnsw-sync-threshold N` flag on init + repair.
- Upstream [MemPalace/mempalace#1463](https://github.com/MemPalace/mempalace/issues/1463) — PR: SQLite BM25 fallback on Chroma ID lookup divergence (Mode 2 recovery).
- Upstream [MemPalace/mempalace#1511](https://github.com/MemPalace/mempalace/issues/1511) — PR (filed 2026-05-15): `MEMPALACE_WING` env var explicit override; Mode 3 source-fix.
- Upstream [MemPalace/mempalace#1424](https://github.com/MemPalace/mempalace/issues/1424) — PR (MERGED): `_wing_from_transcript_path` reads cwd from JSONL; Mode 3 partial fix already in 3.3.5.
- Upstream [MemPalace/mempalace#1452](https://github.com/MemPalace/mempalace/issues/1452) — PR: avoid quarantining recoverable HNSW metadata (Mode 1 adjacent).
