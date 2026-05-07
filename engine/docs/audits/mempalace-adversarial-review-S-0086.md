# MemPalace adversarial review — S-0086

> Authored at S-0086 (interactive `/start-engine`) per [Issue #35](https://github.com/StarshipSuperjam/paideia/issues/35). Campaign session S-D of 7 per [`~/.claude/plans/i-need-a-plan-prancy-ripple.md`](https://github.com/StarshipSuperjam/paideia). First concrete application of [ADR 0057](../../adr/0057-adversarial-stance-for-health-check-audits.md)'s adversarial-stance posture (the formal first-exercise of ADR 0057 is the cadence-fired audit at S-0087). Verdict reasoning weighs both **fit-historically** and **fit-to-CONTINUE**.

## Verdict

**Scale back.** MemPalace earns its weight on a narrow set of engine-side authoring uses (decision drawers; pushback / lesson capture; diary; well-formed boot search) and ADR 0057 just committed those same uses as substrate for forward cadence audits. Retiring the system would retire posture this campaign is constructing, with no offsetting forward gain — none of Phase 6 self-correction, Phase 7 teaching layer, Phase DEC.1 retrieval architecture, OQ-CONTEXT-COMPRESSION, or OQ-PEDAGOGY-INFERENCE-LOCUS specifies MemPalace as a substrate; product runtime is Postgres-shaped end-to-end. Forward opportunity cost of retirement = lost engine-side discipline; forward opportunity cost of preservation = continued burden cost.

The burden cost is real but **partitioned**: a small load-bearing core (decision room, lessons room, problems-room pushbacks, diary wing, well-targeted search) earns its weight; a large dead-weight perimeter (50+ orphaned per-worktree wings, ~40K+ inaccessible drawers in 8 historical full-encoded-path wings, 88 mined ops-doc drawers, KG and tunnels, AAAK spec mostly unused) does not. Scale back to the load-bearing core; recommend retire the perimeter; recommend implement Issues #38 / #39 / #40 with audit-specified shape adjustments.

The verdict is **not** retire. The verdict is **not** preserve-as-is. The verdict is **scale back**, and the scale-back program is the audit's recommendations below — user-adjudicated; downstream-executed per [ADR 0048](../../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) issue discipline; this session does not execute the recommendations.

## Methodology

The audit applies ADR 0057's framework to MemPalace itself. Five contract elements held in:

- **Posture inversion** (ADR 0057 element 2): each use category framed adversarially — "argue for retirement; preserve only with affirmative case keyed to a forward-load-bearing function."
- **Stats-as-proxy anti-pattern** (ADR 0057 element 3): every claim about MemPalace's adoption rests on **content probes run during this audit** — `mempalace_search` against representative recent terms, `mempalace_list_drawers` direct samples of decisions / lessons / problems / general rooms, archive sampling of `mempalace_activity` rollups across 20 sessions S-0066–S-0085. Stats are reported but tagged as inputs to probes, not as conclusions.
- **User-buffered execution** (ADR 0057 element 1): findings + recommendations only. The User adjudication subsection arrives blank. ADR amendments and child Issues land downstream.
- **Required output ≥1 retire-candidate** (ADR 0057 element 4): the perimeter retirement candidates are named with reasoning weighing forward opportunity cost.
- **Cold-context probe** (ADR 0057 element 5): `engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md` randomly selected; reported below.

**Temporal frame:** the audit explicitly asks both "did MemPalace earn its burdens up to now?" AND "does MemPalace fit going forward?". The 12-of-16 Phase 5 routine adoption gap from [Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27) is one data point about *one phase's* work shape; forward phases (Phase 6 self-correction, Phase 7 teaching layer, Phase DEC.1) have fundamentally different work shapes, and ADR 0057's audit-substrate commitment lands force at S-0087. Historical evidence underdetermines forward fit.

**What was excluded.** No retroactive recovery of pre-S-0078 lost diary entries (out of scope per S-0080's correction note; a separate concern from the audit's value question). No upstream-MemPalace bug investigation beyond what's already filed at [#1](https://github.com/StarshipSuperjam/paideia/issues/1), [#2](https://github.com/StarshipSuperjam/paideia/issues/2), [MemPalace/mempalace#1394](https://github.com/MemPalace/mempalace/issues/1394). No design-of-replacement-substrate (the audit produces verdicts and recommendations, not redesign).

## Empirical evidence — historical

### Adoption rate per session, S-0066 through S-0085

Pre-S-0078 (12 sessions, S-0066 → S-0077): every archive shows `search_calls=0`, `diary_read_calls=0`, `diary_write_calls=0`, `add_drawer_calls=0`. **Adoption was 0%, not 25%.** Issue #27's 12-of-16 figure was specific to Phase 5 routines; the broader pattern across both interactive and routine sessions in this window is universal zero. ADR 0056's mechanical adoption checks (S-0078 force) corrected this to ≥1 search and ≥1 diary_write per session in every archive S-0078 → S-0085 (8 sessions).

This is *call frequency* evidence; ADR 0056 worked. The remainder of the audit asks whether the forced calls produce value.

### Decisions room (paideia/decisions): 72 drawers vs 58 ADRs

Direct sample of all 72 drawers via `mempalace_list_drawers wing=paideia room=decisions`. Each drawer is substantive: ADR-companion narrative covering "what prompted this," verbatim conversational context, supersession rationales, amendment-block authoring at the moment the amendment landed. Recent ADRs all carry decision drawers: ADR 0050, 0051, 0052, 0054, 0055, 0056, 0057. ADR 0048 / 0049 missing from `decisions` room (filed under `general` per the wing-naming history); the legacy general-room decision drawers are tagged `decision` correctly.

The 1.24:1 ratio (drawers:ADRs) reflects amendment drawers + light-revision drawers + a handful of pushback drawers misfiled to the decisions room. **Two-layer recording is producing real, usable substrate** — recovered verbatim by `mempalace_search "ADR 0055 apply_migration wrapper production reads gate"` returning ADR 0055's decision drawer with its full deliberation cascade.

### Lessons room (paideia/lessons): 117 drawers

Direct sample of 10 drawers. All 10 carry concrete, recoverable failure-mode content:

- "validate.py can hang transiently (~24min observed at S-0060) on the live graph audit query" — recovery context for a mid-session hang.
- "From a worktree, `git checkout main` fails with 'main is already used by worktree'" — workflow lesson recoverable on subsequent occurrences.
- "Edit tool mismatch on multi-line markdown blocks — fall back to smaller anchor" — tool-recovery lesson.
- "Post-close exploration-mode lockout: every archive value must be correct BEFORE the close commit lands" — operational lesson.
- "STATE.md 'Last build session' rows can drift to 4-cell shape over many edits" — drift-detection lesson.
- "S-0061 ADR 0054 lifecycle-push wrapper subprocess-bypass hypothesis confirmed for two of three modes" — first-exercise verification.

Every sampled lesson is the kind a future session would benefit from retrieving before re-attempting the same approach. Match the `lesson` tag's stated purpose: "we tried X, it failed because non-obvious Y, the fix that worked was Z."

### Problems room (paideia/problems): 291 drawers

Direct sample of 10. All 10 carry verbatim pushback moments — including:

- "S-0075 cross-bridges edge curation against bloat — pushed back against authoring 150 cross-domain edges; recommended threshold."
- "S-0010 — STATE.md-judgment-call on whether ADR 0030 was warranted: pushed toward YES against the easier 'document in CHANGELOG and skip'."
- "S-0061 — Pushed back against the temptation to amend the close commit cd33979 to undo the current_plan.md deletion after the lifecycle-push wrapper REFUSED."
- "S-0026 — Self-critique on proposed two-session split for budget reasons — 'My session-budget claim was a hedge, not a measurement'."
- "S-0010 — caught my own architecture.md footer claim being misleading; corrected mid-session."

Match the `pushback` tag's stated purpose. Verbatim user framing + verbatim AI pushback + verbatim user acceptance + summary, recoverable by semantic search before re-attempting the same mistake.

### General room of paideia wing: 88 mined ops-doc drawers (Issue #40)

Direct sample of 10 from `paideia/general` confirms: chunks of `pedagogy.md`, `learner-model.md`, `MISSION.md`, `architecture.md`. Source files already in version control; reading them via `Read` is more efficient than retrieval via search. These are the noise floor [Issue #40](https://github.com/StarshipSuperjam/paideia/issues/40) names.

### Wing chaos: 50+ per-worktree wings + 8 historical full-path wings

`mempalace_list_wings` confirms 50+ wings of 1-7 drawers each (orphans of the wing-naming bug from Issue [#2](https://github.com/StarshipSuperjam/paideia/issues/2)) and 8 historical full-encoded-path wings totaling ~40K drawers. Direct attempt to list one of the latter (`mempalace_list_drawers wing=-Users-shanekidd-...-cd2efd`) fails with the upstream "wing contains invalid characters" error. The 40K drawers are functionally inaccessible via wing-filtered queries; they still surface in unfiltered `mempalace_search` results, contributing to noise without being addressable for cleanup.

### `sessions` wing (8,814 drawers): organized by topic-room

The `sessions` wing partitions across `architecture` (1,925), `planning` (2,495), `technical` (4,189), `problems` (subset of 291 total), `lessons` (subset of 117 total), `diary` (160). The `general` room is empty. This is auto-capture working — Stop / PreCompact hook chunks topic-bucketed at write time.

### Counterfactual probe — did MemPalace recall change recent sessions?

For S-0083 / S-0084 / S-0085, the diary entries name specific moments. S-0084: the boot read found upstream `mempalace repair-status` already exists, redirected the plan from "build a probe from scratch" to "shell to the existing read-only command" (50-line vs 5-line implementation). S-0085: user-buffered-execution principle was added contract-grade after a one-sentence pushback in plan-mode review (the pushback drawer of that moment is now in `paideia/problems`). S-0083: settings.json desync between intermediate commits caught after first surfacing — the lesson is captured.

For this session (S-0086): the boot `mempalace_search` returned the "what high utility looks like" drawer with concrete A/B/C/D scenarios (re-litigation prevention; pushback retrieval; cross-session capture; convergence detection) which informed the seven-category methodology. It also returned an Issue #38 Skill mechanism description that I evaluated and excluded from execution scope per the audit's posture. **Both recalls altered this session's path.**

This is consistent recall-drives-decision evidence across 4 of 4 sampled sessions.

### Adoption-rate evidence is **about whether the system is queried**, not whether the queries return usable content

The audit ran 6 substantive boot-style searches against representative current and recent topics (ADR 0057, ADR 0056, ADR 0055, cross-domain bridges, rigor score Phase 6 calibration, eager-claim push-gate). All 6 returned usable content — verbatim ADR decision drawers, pushback drawers, lesson drawers, S-0085 outcome summary text. Search recall on substantive queries is producing content quality, not noise.

Two searches against drift-suspect content surfaced exactly the issues ADR 0057 names: a stats-as-proxy claim from S-0040 / S-0041 era ("decisions-room compliance gain is real (1.17 ratio vs. ~0.4)") that the current audit's content probe revises with current numbers (1.24 ratio with substantive content quality, not just count). The system surfaces the older count and the current count side-by-side; the audit reads both and chooses the live evidence per ADR 0057 element 3.

## Empirical evidence — forward-fit map

For each forward state-need named in the project, identify whether MemPalace plays a load-bearing role, is a candidate-among-substrates, or has no role:

| Forward need | Load-bearing substrate | MemPalace role |
|---|---|---|
| **Phase 6 self-correction pipeline** (Sonnet emits tension records; Opus reviewer batches) | `tension_log` Postgres table; Sonnet emission contract in `AGENT_INSTRUCTIONS.md`; Opus reviewer reads from `tension_log`; provisional ADR pipeline writes to filesystem | **None.** No MemPalace mention in `build_plan/P_6_self_correction.md` or `product/docs/self-correction.md` runtime sections. |
| **Phase 7 teaching layer** (Sonnet teaches; multi-turn engagement state) | `AGENT_INSTRUCTIONS.md` system prompt + structured learner state (Postgres `learner_events` + `mastery_snapshots`) + prompt caching | **None.** No MemPalace mention in `build_plan/P_7_teaching_layer.md` runtime. |
| **Phase DEC.1 OQ-DEC1-A** (server-side mastery computation) | Postgres + service-layer | **None.** |
| **Phase DEC.1 OQ-DEC1-B** (two-hop neighborhood retrieval) | Postgres recursive CTEs per ADR 0017 | **None.** |
| **Phase DEC.1 OQ-DEC1-C** (embedding strategy) | pgvector + chosen embedding model | **None.** Note: pgvector is the product-runtime embedding stack; MemPalace's chromadb is a separate engine-side stack. |
| **Phase DEC.1 OQ-DEC1-D** (chunk resolver) | Either Postgres index or direct URL pointers | **None.** |
| **OQ-CONTEXT-COMPRESSION** (Phase 7 prerequisite) | Structured-state replacement (Postgres) + ephemeral per-turn summarization + prompt caching | **None.** Per OQ-CONTEXT-COMPRESSION's leaning: "needs to be ephemeral (in-session-scoped) or explicitly structured to honor the structural-not-substantive discipline" — explicitly rules out durable substrate for compressed conversation, which is what MemPalace would be. |
| **OQ-PEDAGOGY-INFERENCE-LOCUS** | Distributed code + `product/docs/pedagogy/inferences.md` registry | **None.** |
| **Cadence-fired audits going forward** (per ADR 0057, S-0087+) | MemPalace `pushback` / `lesson` drawer content reading; `mempalace_search` against representative recent terms; `audit_mempalace()` adoption-count probes | **Load-bearing.** ADR 0057 commits this substrate in the `health-check.md` "MemPalace freshness probe" section: *"the audit AI runs additional `mempalace_search` MCP calls during prose authoring against current-session-relevant terms; results are read for content quality."* Retirement here requires a successor substrate or contract amendment. |
| **Routine-mode boot procedure** (per ADR 0051) | `mempalace_diary_read` at boot for cross-session continuity | **Load-bearing for routine-mode**, ADR 0051 Skill-driven. Retirement here requires contract amendment. |
| **Two-layer decision recording** (CLAUDE.md standing rule) | ADR + MemPalace `decision`-tagged drawer | **Load-bearing**, with mechanical reminder via `post-adr-write.sh` per ADR 0043. |
| **Engine-side cross-session pattern detection** (e.g., recurring pushbacks against the same risk-class) | `mempalace_search` clustering per ADR 0057 element 3 | **Load-bearing.** AI-judgment work at audit time per the Cluster-detection-not-script principle in ADR 0057. |
| **Phase 5 production audit's freshness probes** | MemPalace freshness probe (per ADR 0057 + S-0085 health-check.md rewrite) | **Load-bearing.** Probes surface in `health-check.md` "Mechanical inputs and freshness probes" section. Inherits ADR 0057 posture once routine T-PHASE-5-AUDIT fires. |

**The forward-fit pattern is decisive.** Product runtime (Phase 6 / 7 / DEC.1) has zero MemPalace dependency. Engine-side discipline (cadence audits, routine-mode boot, two-layer decision recording, pattern detection) has load-bearing dependency. The forward role of MemPalace is identical to its current role; neither expansion nor contraction is mandated by upcoming phases.

## Burden ledger

What the project pays for MemPalace, mapped against retire / scale-back / preserve dispositions:

| Burden | Retire-now | Scale-back-perimeter | Preserve-as-is |
|---|---|---|---|
| ~30 MCP tools surface | Drops to 0 (MCP server unloaded). | Drops to ~10 (search, list_drawers, list_rooms, list_wings, status, diary_read, diary_write, add_drawer, get_drawer; KG / tunnels / AAAK retired). | Stays. |
| Hook complexity (mempalace-hook-wrapper.sh + post-mempalace-tool-use.sh + probe_palace.py + mempalace_rebuild_hnsw.py per ADR 0045 + S-0084) | Drops entirely. Plus the boot-time `validate.py --health-probe-only` MemPalace branch retires. | Stays — load-bearing for store integrity once any uses remain. The recovery story (S-0084's non-destructive rebuild) survives. | Stays. |
| Mechanical adoption checks (ADR 0056) | Drops entirely with the substrate. | **Question opens:** if the surface scales back to a smaller well-defined set, do the three soft-warns / hard-fail still apply 1:1, or do they re-shape? | Stays. |
| Boot ceremony token cost (search + diary_read) | Drops to 0. | Stays for the load-bearing uses. Could be reduced if Issue #38 retargets only well-formed boot searches. | Stays. |
| Two-layer decision recording authoring step | Drops; ADRs alone become canon. | Stays for the engine-side discipline. | Stays. |
| Recovery uncertainty (S-0079 → S-0080 misdirection; S-0084 destructive-repair recovery) | Drops with the substrate. | Stays. The post-S-0084 recovery shape (`mempalace_rebuild_hnsw.py` + `palace.last-good`) is the working answer; no further uncertainty since S-0084. | Stays. |
| Cognitive load (taxonomy, tagging conventions, AAAK) | Drops. | Drops materially: KG / tunnels / AAAK retire; remaining surface is wings + rooms + drawers + 4-tag set (`decision`, `pushback`, `lesson`, `work`). | Stays. |
| Disk + memory footprint of 47,249 drawers | Drops. | Drops materially: pruning the 88 mined ops-doc drawers + 50+ orphaned per-worktree wings (~150 drawers) recovers little disk. The 40K+ historical full-path wings are the fat target — but inaccessible to in-project tooling due to upstream wing-naming bug. | Stays. |

**The headline burden cost lives in the perimeter** (KG / tunnels / AAAK / 88 ops-doc drawers / 50+ orphaned wings / 40K+ inaccessible drawers / wing-naming chaos). The load-bearing core (decisions / lessons / problems / diary / well-targeted search / recovery story / hook integrity) carries forward at modest cost. Scale-back retires the perimeter and preserves the core.

## Counterfactual

### Retroactive (what would have been worse?)

- **S-0084** would have built an HNSW divergence probe from scratch (~50 lines) instead of shelling to upstream's existing `mempalace repair-status` (5 lines) — without the boot search that found the existing tool. Direct value: hours saved + simpler implementation.
- **S-0085** would not have had the user-buffered-execution principle threaded through 5 contract surfaces in one session — without the captured pushback drawer that future sessions can recover.
- **S-0086 (this session)** would have approached the seven-category framing without the "what high utility looks like" drawer's concrete A/B/C/D scenarios — risking a less-disciplined adversarial frame.
- **The accumulated lessons room** (117 drawers) would simply not exist. Many are recovery contexts a future session would re-derive at hours-per-occurrence cost. Specific examples already cited above.

The retroactive counterfactual is positive on the load-bearing core. It's neutral or weakly negative on the perimeter — the noise from per-worktree wings and ops-doc drawers makes search recall harder when the query phrasing doesn't naturally cluster around the load-bearing rooms.

### Prospective (what would Phase 6+ need to build/replace?)

The forward-fit map says: nothing in product runtime needs replacement, because product runtime never used MemPalace. Engine-side discipline would need replacement *if* MemPalace retires entirely. Candidate substrates if engine-side were to be rebuilt cold:

- **Decision drawers → ADR-only canon, plus more aggressive ENGINE_LOG narrative.** Cost: ENGINE_LOG must absorb verbatim conversational context without rotting; today it's typically third-person structured narrative, not deliberation. Loss: the verbatim conversational moment is harder to recover; ADR cross-references give the contract but not the story.
- **Lessons → an `engine/operations/lessons.md` register file.** Cost: register-fatigue (Issue #29's `ideation.md` retirement is exactly the failure mode of register files that stop being maintained). Mempalace's semantic search + room-by-tag retrieval is precisely what makes lessons recoverable; a flat file requires grep + reading.
- **Pushbacks → captured in commit messages or session archive `outcome_summary` only.** Cost: pushback moments are diffuse and conversational; they don't compress into structured archive fields well. The `paideia/problems` room captures the verbatim moment; a structured field would lose the verbatim context.
- **Cadence-audit substrate → contract amendment of ADR 0057.** Cost: the freshness-probe inventory loses one substrate (the `pushback`/`lesson` drawer reading); the audit's content-probe surface narrows to the validator-acted-on-rate, Supabase migration empirical, hook-log success-exit, and registry capture-rate probes. Workable but loses a load-bearing input.
- **Routine-mode diary continuity → ADR 0051 amendment removing the diary read.** Cost: routine-mode loses cross-session reflection continuity; STATE.md's last-session row is the only continuity layer. Workable but reduces context for the next routine session.

The forward replacement work is real but not catastrophic. It's *worse than* preserving the load-bearing core, however — every substitute is a step down in fidelity from what MemPalace delivers today.

## Posture sections (per ADR 0057 element 2)

### Fit — argue for retirement; preserve only with affirmative case

**Adversarial prompt:** What about MemPalace is *doing the work it was created to do*? What about it is plumbing waiting for a function that never arrived?

Doing the work:
- Decision drawers (72) — verbatim ADR-companion reasoning. Affirmative case: future sessions recover decision context via search; the Aug-2025 ADR 0050 decision drawer surfaced this session for the apply-migration-wrapper context. **Preserve.**
- Lessons room (117) — concrete failure-mode recoveries. Affirmative case: validator-hangs, edit-tool-mismatches, worktree git-checkout failures, lifecycle-push verifications all recoverable on similar attempts. **Preserve.**
- Problems room pushback drawers — verbatim moments that prevented re-attempting flagged approaches. Affirmative case: the system-prompt pushback rule has no log; pushback drawers ARE the log per the tag's documented purpose. **Preserve.**
- Diary wing (160 drawers across `wing_claude` + `paideia/diary`) — first-person AI reflection across sessions. Affirmative case: ADR 0051 routine-mode boot procedure depends on this for cross-session continuity. **Preserve.**
- Well-targeted boot search — the audit's own ad-hoc probes returned 6/6 substantive content. Affirmative case: the system surfaces context that STATE.md doesn't carry. **Preserve.**

Plumbing waiting for a function that never arrived:
- KG (`mempalace_kg_*`) — never used. The project encodes structural facts in ADRs + STATE.md + cross-references; KG would duplicate without query-power gain. **Recommend retire.**
- Tunnels — never used. Single-project install; cross-wing linking has no use case. **Recommend retire.**
- AAAK spec for project drawers — diary wing uses AAAK; project drawers don't. The cognitive load of the spec is paid even though the format is selectively used. **Recommend retire from project use** (preserve for diary if upstream insists).
- 88 mined ops-doc drawers in `paideia/general` — duplicate of in-git content. **Recommend retire** (Issue #40A).
- 50+ orphaned per-worktree wings — accident of the upstream wing-naming bug. **Recommend retire** (Issue #40B).
- 40K+ drawers in 8 historical full-encoded-path wings — inaccessible via wing-filtered queries due to upstream "wing contains invalid characters." Contribute to total drawer count but not to retrieval; surface as noise in unfiltered search. **Recommend retire** if a workaround exists for accessing the wings; **defer** if not (dependency on upstream resolution; pair with Issues #1 / #2 / #1394).

### Gaps — argue what would be missing if removed

**Adversarial prompt:** What would a cold-context consumer trip over if MemPalace went dark tomorrow?

The cold-context consumer would lose:
- The verbatim-moment recovery layer for decisions, lessons, and pushbacks. ADRs preserve contracts; ENGINE_LOG preserves third-person narrative. Neither preserves the conversational moment that produced the contract or the failure-mode recovery.
- The cross-session reflection continuity for the AI itself. STATE.md's last-session row carries outcome-focused third-person summary; the AI-side first-person reflection doesn't fit there.
- The cadence-audit `pushback`/`lesson` cluster-detection substrate ADR 0057 just committed. Replacement requires contract amendment.

The cold-context consumer would NOT lose:
- Any product runtime functionality. Phases 6 / 7 / DEC.1 / 8 / 9 don't depend on MemPalace.
- ADR-recorded decisions or contracts. Those live in `engine/adr/` and `product/adr/`.
- Validator soft-warn lifecycle (per ADR 0042's archive-as-canon).

### Infrastructure-without-function — argue retire / convert / preserve-with-affirmative-case

**Adversarial prompt:** Which MemPalace infrastructure exists but produces no observable function?

| Surface | Disposition | Reasoning |
|---|---|---|
| Hook complexity (mempalace-hook-wrapper, ADR 0045 snapshot/probe/rollback, post-mempalace-tool-use) | **Recommend preserve-with-affirmative-case.** Store integrity is load-bearing for the load-bearing core. The S-0084 99.7%-destructive-repair recovery proves the hook's integrity guarantees matter when upstream tooling misbehaves. | Affirmative case keyed to ADR 0045's S-0033/S-0034 vector closure. |
| `probe_palace.py` + `mempalace_hnsw_divergence` soft-warn (S-0084 amendment) | **Recommend preserve-with-affirmative-case.** Detection probe shells to upstream read-only command; cost is one extra `mempalace repair-status` invocation per boot. Load-bearing for surfacing divergence before recall degrades. | Affirmative case keyed to S-0084's empirical demonstration of value. |
| ADR 0056 mechanical adoption checks (3 categories) | **Recommend preserve-with-narrowing.** Forced call frequency is the cheapest surface that prevents the pre-S-0078 zero-adoption recurrence. **Issue #39** (drawer-citation telemetry) closes the value-vs-frequency gap. The hard-fail on diary write retains its severity rationale. | Pair with #39 implementation. |
| `audit_mempalace()` in `health_check.py` (pushback/lesson adoption-count probes) | **Recommend preserve-with-affirmative-case.** ADR 0057 documents these as canonical contract for cadence audits. | Load-bearing for cadence-fired audits going forward. |
| KG (`kg_*` tools, knowledge graph storage, closet hierarchy) | **Recommend retire.** Never used; project's structural facts live in ADRs + cross-references. | Issue against MCP tool surface to scope down. |
| Tunnels | **Recommend retire.** Never used; single-project install. | Issue against MCP tool surface to scope down. |
| AAAK spec for project drawers | **Recommend retire from project use.** Diary wing uses AAAK; project drawers do not. The cognitive cost of the spec is paid for one use; that's not justified. | Doc clarification + tagging-conventions update. |
| `mempalace_status` boot protocol message (the verbose "MemPalace Memory Protocol" prose returned every status call) | **Recommend convert.** The protocol prose belongs in an opt-in spec, not in every status response that surfaces in the AI's context. Currently consuming ~600 tokens per call for prose the project deliberately ignores per `mempalace-operations.md` "Project usage scope". | Upstream issue / project-side filter. |

### Bloat — argue what should be cut

**Adversarial prompt:** What is verbose, repetitive, or redundant?

- **The `general` room of `paideia` wing (88 mined ops-doc drawers).** Cut. Ops docs live in version control; reading via Read is more efficient than retrieval via search. Mining duplicates content and dilutes search ranking.
- **The 50+ per-worktree wings of 1-7 drawers each.** Cut. Orphans of the wing-naming bug; semantic search across them is noise.
- **The 40K+ drawers in 8 full-encoded-path wings.** Cut if accessible via workaround; otherwise defer pending upstream resolution. These contribute search-result noise without contributing recallable signal.
- **The protocol message in `mempalace_status` responses.** Cut from project-side (filter at the MCP layer) or upstream (PR to `mempalace`). ~600 tokens per call across every health-probe + audit invocation is real cost for prose the project ignores.
- **AAAK spec for project drawers.** Cut from project-side. Diary uses AAAK (`wing_claude`); project drawers in `paideia` wing don't and shouldn't (verbatim conversational format is the value).

## Issues #38 / #39 / #40 evaluation

### Issue #38 — Mechanize MemPalace boot search with reformulations into current_plan.md

**Audit verdict:** **Implement, with audit-specified scope adjustments.**

Issue #38 names the right value lever (search effectiveness, not just call frequency) and proposes the right structural mechanism (Skill-driven reformulation + write into `current_plan.md`). Audit caveats:

- The current single-formulation boot search is producing usable content for substantive queries (this audit's empirical evidence). The problem #38 names is real but partial — search recall is *workable* with one well-formed query, *better* with three.
- Recommend implement #38 as proposed.
- Recommend the post-implementation Issue #39 telemetry to provide closed-loop measurement: did the three-formulation search return drawers that subsequent authoring cited? If yes, the mechanism earns its weight; if no, scale back.

### Issue #39 — Instrument MemPalace drawer-citation telemetry at shutdown

**Audit verdict:** **Implement.**

The audit's own counterfactual probe is exactly what #39 asks future sessions to mechanize. Today, the audit reads diary entries + outcome_summary + commit messages to infer "did MemPalace recall change anything?". Mechanizing this surfaces the same signal continuously without per-audit AI judgment.

The proposed `mempalace_zero_citations_after_search` soft-warn is well-shaped — fires precisely when retrieval happens but produces no observable behavior change. Pairs naturally with #38's post-implementation evaluation.

Recommend implement as proposed. Add a row to `audit_archive_structured_fields.py`'s `REQUIRED_ARCHIVE_FIELDS` per ADR 0056 Layer 4 — no audit code change needed.

### Issue #40 — Prune MemPalace noise floor

**Audit verdict:** **Implement, with audit-specified expansion.**

Issue #40 names two prune targets (88 mined ops-doc drawers + per-worktree wings). The audit's findings widen the scope:

- **#40A — 88 mined ops-doc drawers:** implement as proposed. Direct delete; small batch; reversible from version-control source if needed.
- **#40B — 50+ orphaned per-worktree wings (1-7 drawers each):** implement as proposed. Audit per the issue's procedure: if the wing carries any high-signal drawers (`decision`/`pushback`/`lesson` content), preserve those by manual re-capture into bare `paideia` wing; delete the rest.
- **#40C — NEW SCOPE: 40K+ drawers in 8 historical full-encoded-path wings.** If a workaround exists for accessing wings whose names contain invalid characters (upstream Issues [#1](https://github.com/StarshipSuperjam/paideia/issues/1) / [#2](https://github.com/StarshipSuperjam/paideia/issues/2) / [#1394](https://github.com/MemPalace/mempalace/issues/1394) territory), prune. If not, defer with explicit dependency on upstream resolution. The 40K count is the fat target; pruning 88 + 150 leaves the bulk untouched. Recommend Issue #40 explicitly takes a position on #40C.
- **#40D — NEW SCOPE: KG and tunnels retirement.** Consistent with the audit's verdict on infrastructure-without-function. The MCP tool surface for KG (`kg_query`, `kg_add`, `kg_invalidate`, `kg_stats`, `kg_timeline`) and tunnels (`find_tunnels`, `list_tunnels`, `create_tunnel`, `delete_tunnel`, `traverse`) is project-side dead weight. Document the retirement; consider whether MCP filtering is possible to reduce the surface the AI's context loads.
- **#40E — NEW SCOPE: AAAK spec retirement from project usage.** The diary wing keeps AAAK; project drawers in `paideia` wing use verbatim conversational format. Document explicitly so future drawers are authored consistently.

Recommend the audit's scope-expansion lands as comments on Issue #40 (or as #40A/B/C/D/E child Issues if the user prefers granularity). The retirement program lands as a single cleanup-batch session post-user-adjudication.

## Affirmative retire candidates (per ADR 0057 element 4)

The audit recommends the following retire candidates with reasoning weighing both historical evidence and forward opportunity cost:

1. **88 mined ops-doc drawers in `paideia/general`** (per Issue #40A). *Historical:* duplicate of in-git content; dilutes search ranking. *Forward:* no Phase 6+ use case. *Forward opportunity cost of retire:* zero. **Strong retire.**
2. **50+ per-worktree wings (1-7 drawers each)** (per Issue #40B). *Historical:* orphans of upstream wing-naming bug; never queried; never produced retrieval value. *Forward:* no use case. *Forward opportunity cost of retire:* zero. **Strong retire.**
3. **KG (`kg_*` tool family)** (per #40D). *Historical:* documented as not-used in `mempalace-operations.md` "Project usage scope" since S-0032. *Forward:* no Phase 6+ use case (Postgres + ADRs + STATE.md cover structural facts). *Forward opportunity cost of retire:* zero. **Strong retire.**
4. **Tunnels (`*_tunnels` tool family)** (per #40D). *Historical:* documented as not-used. *Forward:* no use case (single-project install). *Forward opportunity cost of retire:* zero. **Strong retire.**
5. **AAAK spec for project drawers** (per #40E). *Historical:* selectively applied (diary wing only); the cognitive cost of the spec is paid for one use site. *Forward:* no Phase 6+ use case for project drawers. *Forward opportunity cost of retire:* near-zero (preserve AAAK for diary if convenient). **Recommend retire from project drawer authoring** (preserve-for-diary).
6. **40K+ drawers in 8 historical full-encoded-path wings** (per #40C). *Historical:* inaccessible to in-project tooling; contribute search-result noise without retrievable signal. *Forward:* no use case. *Forward opportunity cost of retire:* zero. **Recommend retire conditional on upstream-bug workaround** (Issues [#1](https://github.com/StarshipSuperjam/paideia/issues/1) / [#2](https://github.com/StarshipSuperjam/paideia/issues/2) / [#1394](https://github.com/MemPalace/mempalace/issues/1394) dependency).

## Cold-context probe

**Random-pick procedure:** `find engine/operations engine/adr docs/health-checks engine/build_readiness -name '*.md' -type f` then `RANDOM`-indexed selection (the host's `shuf` was unavailable; equivalent randomization via shell `RANDOM`).

**Selected artifact:** [`engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md`](../../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

**Cold read findings:**

- Self-contained: a cold reader can understand the problem (HANDOFF cleanup-treadmill), the decision (narrow HANDOFF; route deferrals to Issues with label taxonomy + boot visibility + scope-collision detection), and the rationale (S-0027–S-0041 telemetry of 2.25:1 cleanup-to-substantive ratio) without consulting other artifacts. Concrete numbers anchor the empirical case.
- Cross-references resolve: ADR 0043 (hook architecture), ADR 0045 (shared-state integrity), ADR 0049 (sibling — scope-lock + descope-reorder audit), CLAUDE.md sections, file paths to the four new tools and modified hook scripts. All resolve to currently-correct content.
- Sibling coupling: "Per ADR 0049, sibling to this one" — cold reader needs ADR 0049 to fully understand the `declared_scope` field that ADR 0048's collision detector consumes. Coupling is named explicitly so the cold reader knows where to look. Acceptable.
- Amendment block at S-0051: "FYI line corrected; taxonomy extended; community labels dropped." Three concrete defects named, three corrections named, distinction between amendment and supersession explicit. The amendment shape is honest and well-formed.
- No drift: the ADR's claims about deliverables (issue-discipline.md, scan_issue_backlog.py, scan_issue_collisions.py) match current files; the post-S-0051 label taxonomy claims (12 labels: 8 type + 1 priority + 3 reactive-only) match the current `gh label list` reality.

**Verdict on the cold-read:** healthy. No hidden drift. No orphan claims. The ADR is exactly the artifact a future cold consumer needs.

## Concrete recommendations

The audit recommends the following actions, **all subject to user adjudication** per ADR 0057 element 1:

### Recommendations: implement (the load-bearing core)

- **R1.** Implement [Issue #38](https://github.com/StarshipSuperjam/paideia/issues/38) (mechanize boot-search reformulations into `current_plan.md`) as proposed. Pair with R2's telemetry for closed-loop evaluation.
- **R2.** Implement [Issue #39](https://github.com/StarshipSuperjam/paideia/issues/39) (drawer-citation telemetry at shutdown) as proposed. Adds `mempalace_citations` field per ADR 0056 Layer 4 + `mempalace_zero_citations_after_search` soft-warn.
- **R3.** Implement [Issue #40](https://github.com/StarshipSuperjam/paideia/issues/40) with audit's scope expansion: #40A (88 ops-doc drawers) + #40B (50+ orphaned wings) + #40C (40K+ historical full-path wings, conditional on upstream workaround) + #40D (KG + tunnels MCP-tool retirement) + #40E (AAAK spec retirement from project drawers).

### Recommendations: contract update (codify the audit's verdict)

- **R4.** Author a small-scope ADR amending [ADR 0056](../../adr/0056-mempalace-mechanical-adoption-checks.md) to record the audit's scale-back verdict: explicitly declare KG / tunnels / AAAK-for-project-drawers / mined-ops-doc-drawers / orphaned-per-worktree-wings as out-of-project-scope, paired with the Issue #40 retirement program. Pattern: in-place Consequences amendment block (no supersession) per the project's amendment discipline.
- **R5.** Update [`engine/operations/mempalace-operations.md`](../../operations/mempalace-operations.md) "Project usage scope" section to reflect the post-audit scoped surface (drop KG / tunnels / AAAK-for-project; add `wing_claude` AAAK carve-out). Doc work; no ADR needed.
- **R6.** No changes to ADR 0057's freshness-probe contract. The audit's verdict (scale back, preserve load-bearing core) is consistent with ADR 0057's `pushback`/`lesson` substrate commitment. The S-0087 first-exercise audit can apply the same posture cleanly.

### Recommendations: docs

- **R7.** Update [`docs/health-checks/TEMPLATE.md`](../../../docs/health-checks/TEMPLATE.md) "Forward-fit map" subsection (or sibling) to bake in the temporal-frame discipline this audit applied: any future audit of an internal subsystem weighs both fit-historically AND fit-to-CONTINUE. Defer to S-0087's first-exercise audit if it surfaces a cleaner shape.
- **R8.** Note in [`engine/operations/mempalace-tagging-conventions.md`](../../operations/mempalace-tagging-conventions.md) that pushback drawers occasionally land in `paideia/decisions` instead of `paideia/problems` when authored alongside an ADR (sample: `drawer_paideia_decisions_a3d64680e953450f011e582f`). Either: room targeting is intentional and the convention should reflect it, OR: the convention is strict and a one-shot migration moves the misfiles. Recommend the former (tagging carries the meaning; room targeting is best-effort) and document accordingly.

### Recommendations explicitly NOT in scope

- The audit does not recommend retire of MemPalace as a whole. The verdict is scale-back, not retire.
- The audit does not recommend changes to the boot ceremony (steps 3 / 3b in `session-build-lifecycle.md`). Issue #38, if implemented, modifies the ceremony surface; absent #38, the ceremony stays.
- The audit does not recommend retroactive recovery of pre-S-0078 lost diary entries. That work was bounded out at S-0080.
- The audit does not propose new ADR for "MemPalace's overall role." The role is settled by the existing ADRs (0045 + 0056); the scale-back verdict is an amendment to ADR 0056, not a new contract.

## User adjudication

<populated post-audit by the user>

The recommendations above are the audit's findings. Per ADR 0057 element 1 (user-buffered execution), execution work — ADR amendment authoring, child Issue filing, doc updates, retirement-program scheduling — lands in downstream sessions after user adjudication, OR inline in this same session if the user approves during in-session review.

## Notes on framework fit

This is the first concrete application of ADR 0057's adversarial-stance posture. Notes for S-0087's first-exercise refinement:

- **The seven-category Issue #35 framing AND the four-posture ADR 0057 framing both apply, but at different layers.** The seven categories enumerate use-categories (boot search, diary read, diary write, two-layer recording, pushback/lesson capture, KG, tunnels). The four postures (Fit / Gaps / Infrastructure-without-function / Bloat) frame *how* to ask about each category. The audit threaded both: each use category was evaluated through each posture's adversarial prompt-question. This worked; documenting that two-layer interplay in `health-check.md` may help S-0087.
- **The forward-fit map is the audit's most decisive output.** The seven-category evidence table is good; the burden ledger is good; but the forward-fit-map's "MemPalace plays no role in Phase 6 / 7 / DEC.1; load-bearing in cadence audits + routine-mode boot + two-layer decision recording" was the verdict-shaping output. Recommend `health-check.md` Forward-fit-map subsection (sibling to Mechanical-inputs-and-freshness-probes).
- **The dual counterfactual (retroactive + prospective) is more decisive than either alone.** Retroactive answered "did the system pull weight"; prospective answered "will it continue to." Together they answered the load-bearing question.
- **Recommendation-only execution worked.** The audit produces actions for user adjudication, not actions executed in-session. The Issue #38 / #39 / #40 evaluation subsection is the natural fit-point for already-filed Issues whose dispositions the audit informs.
- **Cold-context probe was small but useful.** ADR 0048 cold-read healthy. The probe is a proportionate defense against the warm-context bias; one randomly-selected artifact is sufficient at audit cadence.

If S-0087's first-exercise audit applies the same posture and surfaces friction, the surface should be ENGINE_LOG-tracked refinement to `health-check.md` and `TEMPLATE.md`, not contract supersession.

## See also

- [Issue #35](https://github.com/StarshipSuperjam/paideia/issues/35) — the original framing and seven-category methodology this audit answers.
- [Issue #38](https://github.com/StarshipSuperjam/paideia/issues/38), [#39](https://github.com/StarshipSuperjam/paideia/issues/39), [#40](https://github.com/StarshipSuperjam/paideia/issues/40) — the three already-proposed solutions evaluated above.
- [ADR 0057](../../adr/0057-adversarial-stance-for-health-check-audits.md) — the framework this audit applies.
- [ADR 0056](../../adr/0056-mempalace-mechanical-adoption-checks.md) — the call-frequency mechanism whose value the audit interrogates.
- [ADR 0045](../../adr/0045-shared-state-integrity-discipline.md) — the store-integrity discipline the audit affirms (load-bearing for the load-bearing core).
- [`engine/operations/mempalace-operations.md`](../../operations/mempalace-operations.md) — the operational surface; the audit recommends targeted updates per R5.
- [`engine/operations/health-check.md`](../../operations/health-check.md) — adversarial-stance ops surface; the audit's notes on framework fit feed S-0087's refinement.
- [`engine/build_readiness/adversarial_stance_first_exercise.md`](../../build_readiness/adversarial_stance_first_exercise.md) — first-exercise readiness note (T1-A through T1-E pending S-0087, not S-0086).
- [Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27) — closed at S-0078; the historical-adoption gap the audit interrogates.
- [Issue #31](https://github.com/StarshipSuperjam/paideia/issues/31) — closed at S-0084; the destructive-repair recovery whose detection probe the audit affirms.
