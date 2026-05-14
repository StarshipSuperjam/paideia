# Project health check

> Periodic audit of the project's own machinery: does our discipline match what we're producing? Per ADR 0022 (lands in S-0003). Cadence trigger fires automatically at session boot when `(next_id - last_audit_session) >= health_check_cadence` (overdue-catchup logic introduced at S-0041; default cadence: 10 as of S-0033, was 30 from S-0001 to S-0032 — tightened by user direction at S-0032 because the audit there surfaced enough silent failures that the 30-session window was too sparse; see ADR 0022 Consequences amendments). The trigger fires both at the natural-cadence slot and at every later slot until the audit fires (no silent slide).

The first check landed at S-0030 (manual fire at the project-setup-to-project-build phase boundary; see [`docs/health-checks/S-0030.md`](../../docs/health-checks/S-0030.md)). [`engine/tools/health_check.py`](../tools/health_check.py) was authored at S-0029 per [ADR 0022](../adr/0022-periodic-project-health-checks.md). The second check landed at S-0041 ([`docs/health-checks/S-0041.md`](../../docs/health-checks/S-0041.md)) as a catch-up audit after the original cadence-aligned slot (S-0040) was consumed by user-directed work and the strict-modulo trigger silently slid forward to S-0050. Under the cadence-10 default the next natural fires are at every cadence interval beyond `last_audit_session`.

## When the trigger fires

At session boot, the SessionStart hook (`engine/tools/hooks/session-start.sh` per [ADR 0043](../adr/0043-hook-architecture.md)) parses the trailing 4-digit counter from `next_id` (the slot about to be claimed; e.g., `next_id: "0040"` → `40`), reads `last_audit_session` from `register_state.json`, and computes `slots_since = next_id - last_audit_session`. The trigger fires when `slots_since >= cadence`:

- `slots_since == cadence` — "due" surface; the cadence-aligned natural fire:
  > "Next slot is S-NNNN. Cadence trigger fires for a project health check. Run the audit now or defer?"
- `slots_since > cadence` — "overdue" surface; the cadence-aligned slot was consumed by other work and the audit slid:
  > "Cadence trigger fires; audit is OVERDUE by N session(s). Run the audit now or document explicit deferral."

`last_audit_session` is bumped by `engine/tools/health_check.py` at report-emit time (per the same S-0041 amendment); the field is the canonical "audit happened" anchor. If `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041), the hook falls back to the strict-modulo logic with a stderr log line so the regression surfaces at boot.

The `/start-engine` slash command's documented procedure mirrors this logic at step 2; the hook surfaces the prompt regardless of how the session is launched.

The validator's `health_check_overdue` soft-warn ([`tools-validate-interpretation.md`](tools-validate-interpretation.md)) provides defense-in-depth: if the SessionStart hook silently fails (the S-0033/S-0034 vector pattern), the soft-warn fires on every commit until the audit catches up.

### History of the cadence-trigger logic

- **S-0001 → S-0030.** Original logic: `last_claimed mod cadence == 0`. Off-by-one against ADR 0022 prose intent — fired the trigger one slot AFTER the cadence-numbered session.
- **S-0031 → S-0041.** Corrected to `next_id mod cadence == 0` (strict-modulo) per [ADR 0043](../adr/0043-hook-architecture.md). The fix landed at the right slot but introduced a silent-slide failure mode: when the cadence-aligned slot was consumed by user-directed work, the trigger silently slid forward by a full cadence (S-0040 missed → next fire at S-0050, a 19-session gap).
- **S-0041 onward.** Replaced strict-modulo with overdue-catchup: `(next_id - last_audit_session) >= cadence`. The trigger now fires at the natural cadence slot AND at every later slot until the audit fires. ADR 0022 Decision + Consequences amended; ADR 0043 Consequences amended; carriers updated across `engine/tools/hooks/session-start.sh`, this doc, `engine/operations/session-build-lifecycle.md`, the corresponding skill, and `.claude/commands/start-engine.md`.

The user's response routes:

- **Accept** — the session's work *is* the audit. Author a report (template below) and commit it under `docs/health-checks/S-NNNN.md`.
- **Defer** — proceed with planned work; the trigger fires again next session, and again the session after, until accepted or the user explicitly disables the cadence in `register_state.json` for some bounded window.

The cadence is configurable per-project in `register_state.json` via the `health_check_cadence` field. **10 is the default as of S-0033** (was 30 from S-0001 to S-0032). The change is recorded in `register_state.json`'s `health_check_cadence_history` field with reasoning. Lower for fast-moving phases or when telemetry shows fast drift; higher when phases are long and structurally settled. Re-evaluate as part of any cadence-numbered audit.

## How the audit *behaves* — operative discipline

The deliverable of a health-check is **not the report.** The deliverable is the *behavior of looking honestly* at the project's machinery and surfacing what isn't doing its work. The report is a byproduct.

This distinction matters because the prior framing — Fit/Gaps/Dead-Weight/Bloat as four categorical buckets to fill — biases the audit toward report-completion rather than judgment. A categorical list can be produced quickly without auditing anything beyond what mechanical scans emit. **If you find yourself producing a categorized list quickly, you are reporting, not auditing.** Stop and re-engage.

Before triaging anything, internalize the **operative diagnostic question** the audit applies to every artifact, every category, every rule:

> *Is this thing doing the work it was created to do, or is it plumbing waiting for a function that never arrived?*

A file with 17 inbound references but zero captured entries is plumbing. A validator soft-warn that fires 40 times across 5 sessions and is never acted on is plumbing. An ops doc that exists but no session has cited following is plumbing. A pending decide-trigger pinned to a phase that passed two sub-phases ago is plumbing. The diagnostic is uniform; the surfaces vary.

**Required output:** every health-check must surface at least one **non-obvious finding** that is not on any mechanical scanner's output. Mechanical surfaces (the scanners below) feed the audit; they do not replace it. If the audit's report contains only what the scanners produced, the audit did not happen.

## Adversarial stance (per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md))

The four posture sections below default to *confirming* that things still work, with **preserve** as the safe disposition. Across cumulative audit windows the preserve-disposition reinforces itself — S-0052 said preserve; S-0065 cited S-0052; S-0077 cited both — and accumulated dead-weight no audit retires. The fix is structural: the audit takes an **adversarial stance** at every section. Argue the candidate should be retired or replaced; only preserve with affirmative case.

[ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) is the citable contract; this section is the operational surface. The adversarial-stance posture is the audit-side counterpart to [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s gate-side adversarial-reconnaissance discipline. ADR 0040 asks *"what could break our session?"* prospectively at the gate; this contract asks *"what is broken or stale or superseded that we've been carrying as if it were fine?"* retrospectively at the audit.

### Stats-as-proxy-for-function (named anti-pattern)

The lazy-analysis pattern: an audit cites a count, a status field, or an existence check and treats it as evidence the system is doing its job. The diagnostic question is whether it is *doing the work*, which counts and existence don't answer. Every system reference in the audit must specify what *content probe* runs against it.

The S-0065 audit looked at MemPalace and wrote *"Wing `paideia` carries 485 drawers across 5 rooms as of S-0032 close (from STATE.md infrastructure row); this audit did not run a fresh `mempalace_status`. Treat as a known number. **No action.**"* — citing a cached count from a prior audit and treating its existence as a healthy signal. Meanwhile, the routine-mode-skips-diary-write gap ([Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27)) was actively dropping `pushback`/`lesson` capture across every Phase 5 routine session — invisible to drawer-count-as-stat but obvious to anyone who tried to *use* MemPalace recall during routine work.

The class is broader than MemPalace. Validator soft-warn count → "working," even when soft-warns aren't producing acted-on signal. Supabase migrations table populated → "DB is fine," without checking whether the migration's empirical postconditions hold against live data. Hook scripts exist on disk → "hooks are running," even if a PATH problem makes them silently no-op (the S-0032 audit caught exactly this for the mempalace capture hook *only because* a probe-style fresh check ran). The Mechanical inputs section below names a per-system freshness-probe inventory; the audit's prose claim about a system's health must rest on a probe run *during this audit*, not on a cited number from a prior audit or a cached entry in [`engine/STATE.md`](../STATE.md).

### Posture inversion is load-bearing

Each of the four traditional postures (Fit / Gaps / Infrastructure-without-function / Bloat) gets an adversarial prompt-question rewrite below. The Infrastructure-without-function disposition options shift from `[retire / convert / preserve]` to `[recommend retire / recommend convert / recommend preserve-with-affirmative-case]` — *recommendation*-shape, not action-shape, per the user-buffered execution principle below. The affirmative case for preserve must specify *what work this artifact does that no other artifact does*. "Inbound references" alone is not an affirmative case; the references are themselves candidates for retirement.

**Required output: ≥1 affirmative retire-candidate-recommendation** (or an adversarially-scrutinized explicit "no candidates" subsection). The current ≥1-non-obvious-finding requirement still holds; the new ≥1-retire-candidate requirement is additive. An audit that ends with all preserves and zero retires is structurally suspicious in the same way an audit producing no findings would be — the adversarial posture wasn't exercised. The escape hatch: if the project's current state honestly admits no retire candidates, the audit authors an explicit "no retire candidates this audit" subsection that adversarially scrutinizes its own claim ("I argue no retire candidates because X; if X were false, Y would be a candidate"). The escape is open *and* answerable.

### Cold-context probe per audit

The audit reads ≥1 randomly-selected artifact (operations doc, ADR, register, build-plan chunk, STATE.md row, hook script) *as if* it had no project context, and asks: do cross-references resolve to currently-correct content? does the prose tell a future cold consumer how to *use* this artifact, or only that it exists? does the artifact name a sibling that no longer exists? does it carry a rule whose successor superseded it without a back-reference? The probe is the audit's defense against compound drift in artifacts the warm-context audit can't see — the audit knows too much, and that knowledge is itself the failure mode. A randomly-selected target prevents the audit from converging on artifacts it already trusts.

### User-adjudicated execution — inline when interactive, buffered when unattended

The audit's deliverable is **findings + guidance suggestions, adjudicated by the user before downstream action is taken**. The audit *reports* and *recommends*; the user *adjudicates and authorizes*; downstream actions execute per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) issue-discipline (the `health-check-finding` label is the deferral lane).

This is the structural counterpart to [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s "gate sessions are conversational by default" posture — the cadence audit is conversational by default in the same way. The audit session has no path to executing retire / convert / replace actions autonomously; "auto-resolve" of an audit finding is a misidentification of the session's mode. Inline trivial cleanups that fall under the standard "default to fix-in-context" rule (per [CLAUDE.md](../../CLAUDE.md)) still apply — the buffer is for the audit's *adversarial recommendations* (retirement, replacement, structural change), not for stray typos noticed in passing.

The *adjudication step* runs in one of two shapes by audit mode (per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) revised Decision 1 at S-0143):

**Interactive audit (user present).** The audit MAY adjudicate findings inline:

1. After authoring each section's adversarial findings (Fit / Gaps / Infrastructure-without-function / Bloat / Non-obvious / Affirmative retire candidates / Cold-context), surface the adjudication options to the user via AskUserQuestion (or equivalent conversational prompt). One question per finding with a small number of disposition options: *accept (file Issue / fix inline / surface in STATE.md / add to tensions.md)*, *reject (with reason)*, *modify (then re-surface)*.

2. Record the user's disposition in the report's "User adjudication" subsection. Author the table row in declarative form ("**Finding A** — *accept*; routed to Issue #NNN" or "**Finding B** — *reject*; the inbound reference is structurally load-bearing per ADR XXXX").

3. For accepted findings routed to Issues, file them inline via `gh issue create --label health-check-finding` immediately. The Issue body cites the audit report by path. Other dispositions (fix-inline / STATE.md surface / tensions.md entry) execute via the same session's normal commit cadence.

4. The audit closes with the User adjudication subsection populated and all approved downstream artifacts authored in the same session — no follow-up adjudication session is required.

This pattern mirrors ADR 0040's build-readiness gate "the AI surfaces, the user directs, the AI authors the resolution artifacts in same session." It collapses what was previously a 2-session cost (audit session + adjudication session, the pre-S-0143 default) into one interactive conversation when the user is reachable.

**Routine-fired audit (unattended).** The audit MUST leave the "User adjudication" subsection blank. The audit closes with recommendations *surfaced*, not *executed*. A subsequent interactive session reads the audit report, populates the User adjudication table with dispositions, and routes approved findings to Issues (or other lanes) at that time. This preserves the deliberation buffer for findings whose merit is genuinely contested — the user-time cost of a 2-session split is justified when no user is available to adjudicate inline.

**Mode determination.** If the AI is responding to user input in the same session (interactive `/start-engine` invocation; a session the user attends after a cadence-trigger boot surface), inline adjudication is permitted. If the session is fired by Claude Code Routines per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) (no user input expected), inline adjudication is structurally impossible — leave the table blank.

The audit AI is responsible for the determination. Mis-judgment toward inline adjudication when no user is reachable means findings sit silently in an unanswered AskUserQuestion surface — the same failure mode the user-buffered framing was protecting against, surfaced from a different direction.

## Mechanical inputs and freshness probes (the audit consumes; the audit is not consumed by them)

The mechanical scanners below feed the audit; the freshness probes attached to each external system the audit references answer the operative diagnostic question per the stats-as-proxy-for-function anti-pattern named above. The probe surfaces are required: the audit's prose claim about a system's health must rest on a probe run *during this audit*, not on a cited number from a prior audit.

### Dead-weight scanner

[`engine/tools/scan_orphans.py`](../tools/scan_orphans.py) — multi-axis scanner that surfaces candidate files for the dead-weight conversation. Five axes, each independent:

- **reference-count** — files with fewer than 3 inbound references.
- **last-mod-age** — files unchanged across 20+ sessions of project history AND with low inbound references (the dual filter prevents foundation reference docs from surfacing).
- **register-empty** — register/queue files (currently `tensions.md`) with no captured entries. (Pre-S-0083 the list also included `ideation.md`; that file retired at S-0083 per Issue #29 — its function migrated to GitHub Issues with the `enhancement` label per ADR 0048.)
- **ops-doc-uncited** — operations docs not cited in any of the last 20 session archives.
- **stale-marker** — files carrying decide-trigger / decide-before / open decide-by markers classified as **back-pinned** (overdue OR unannotated). Marker lines explicitly **forward-pinned** to a future phase/session/OQ/external-trigger are deliberately deferred and not stale; the scanner skips them via the classifier in `is_marker_line_back_pinned()` (per S-0143 / [Issue #111](https://github.com/StarshipSuperjam/paideia/issues/111)). Forward-pin trigger vocabulary the classifier recognizes:
    - `decide-before Phase N` — forward-pinned when N > current_phase (Phase N has not yet opened); back-pinned (overdue) otherwise.
    - `decide-by S-NNNN` — forward-pinned when NNNN > current_session_id; back-pinned otherwise.
    - `Phase N+` — forward-pinned when N > current_phase; back-pinned otherwise.
    - `[TRIGGER: <condition>]` — always forward-pinned (gated on external condition).
    - `OQ-XXXXX` reference — always forward-pinned (the open question is unresolved; if it had been settled, the marker would have been removed).
    - No trigger annotation → back-pinned (stale by default, since no deferral justification is given).
    The same classifier is used by [`engine/tools/health_check.py`](../tools/health_check.py)'s TBD/TODO/FIXME marker scan in audit_gaps; both surfaces share the trigger vocabulary so an annotation that satisfies one satisfies the other.

Run at audit-session boot:

```bash
python3 engine/tools/scan_orphans.py --output engine/health_check/dead_weight_candidates_S-NNNN.md
```

Each candidate is annotated with axis, signal, last substantive change, and inbound reference count. The audit walks the file top-to-bottom and triages each candidate against the operative diagnostic question. **Surfacing in multiple axes is a stronger signal.** A file that flags both `ops-doc-uncited` AND `last-mod-age` AND `reference-count` is almost certainly dead weight; the audit confirms by reading the file.

### Validator telemetry

`tools/validate-history.jsonl` (gitignored, per-clone) — soft-warn category trends, validator runtime drift, hard-fail incidence. Per [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md), each record carries four per-phase duration fields against tiered targets:

- **Structural phase** (in-process file/regex checks; no DB, no subprocess) — target **< 500ms**.
- **Health-probe phase** (external-subprocess probes: chromadb open + repo state + GitHub Issues via `gh`) — target **< 5s**.
- **Graph audit phase** (live-DB consultation per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md)) — target **< 5s**.
- **Total runtime** — target **< 11s**.

The `validator_runtime_phase_regression` soft-warn fires when any phase exceeds 1.5× its tiered target across 3 consecutive runs (the current run participates in the rolling window). Pre-S-0126 entries carry the prior single `duration_ms` field; pre-S-0127 entries carry the three-field schema (no `duration_health_probe_ms`); the regression check skips entries that don't carry every per-phase field.

`engine/session/archive/S-NNNN.json` — per-session `outcome_summary_soft_warns` (the canonical structured field per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)), `started_at`, `closed_at`, `status`, `outcome_summary`, branch, and (post-ADR-0049) `scope_delivery`. (Pre-S-0083 archives also carry `transcript_token_pct` / `transcript_token_estimate` / `tokenizer_used` from the retired ADR 0049 decision 3 telemetry; new archives do not.)

### Project state

ADR collection (counts by status across time), ENGINE_LOG entries (categorized engine changes by date), MemPalace stats (`mempalace_status`, `mempalace_kg_stats` — drawer growth, room balance, last-write activity). **These are stats; they feed the audit but do not answer the operative diagnostic question.** The freshness probes below are required content probes, not substitutes for the stats.

### Freshness probes (per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md))

Each external system the audit references gets a fresh content probe at audit-time. The probe answers "is this system *doing the work*?" not "does it exist?". Probes are run during the audit; the report's "Freshness probes run" subsection (per the new TEMPLATE.md shape) records what was probed and what the probe surfaced.

#### MemPalace freshness probe

Run `mempalace search` against ≥3 representative recent terms — derived from the last 1-3 sessions' `working_on` subjects in `engine/session/archive/*.json`, plus named `pushback`/`lesson` keywords. The probe is *"does recall return relevant content?"* not *"does the wing have drawers?"*. [`engine/tools/health_check.py`](../tools/health_check.py)'s `audit_mempalace()` function already runs `pushback`/`lesson` adoption-count probes via a direct wing-agnostic read of the chromadb sqlite store (converted from the wing-scoped `mempalace search --wing paideia` CLI at S-0163 per [Issue #128](https://github.com/StarshipSuperjam/paideia/issues/128) — the prior wing-scoped query returned empty once drawers scattered across ~77 wings) — the audit cannot skip them. Beyond the script's mechanical surface, the audit AI runs additional `mempalace_search` MCP calls during prose authoring against current-session-relevant terms; results are read for *content quality* (do the drawers carry usable context, or are they thin?), not just count.

#### Validator freshness probe

Read the *acted-on rate* of soft-warns across the audit window, not just the count. For each persistent soft-warn category surfaced at boot (3+ of last 5 archives per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)), check whether commits in the audit window addressed the named category — `git log --grep` against the category name, cross-referenced with `outcome_summary_soft_warns` deltas across consecutive archives. The probe is *"are warnings producing acted-on signal?"* not *"what's the count?"*. Persistent warns with zero acted-on commits across the window are candidates for promotion to hard-fail (per [`tools-validate-interpretation.md`](tools-validate-interpretation.md) "Persistent-warn annotation"), category-redefinition, or retirement.

#### Supabase freshness probe

Verify the most-recent migration's empirical effect against the live DB. Sample row counts against the migration's expected scale; spot-check predicate distribution against the migration's `Postcondition-Assertions:` block (once that lands at S-E per [Issue #23](https://github.com/StarshipSuperjam/paideia/issues/23)); confirm the schema shape matches the migration's contract header. The probe is *"does the migration's postcondition hold?"* not *"is the schema_migrations row present?"*. Read-only via `psycopg`; never write through the audit path. Cross-ref [`migration-discipline.md`](migration-discipline.md).

#### Hook freshness probe

Tail `.claude/logs/*-hook.log` for the audit window; verify recent invocations show success exit codes (`OK exit=0`), not just hook script existence on disk. The probe is *"does the hook fire successfully?"* not *"does the script file exist?"*. The S-0032 audit caught the mempalace capture hook silently failing (FAIL exit=127 on every fire since S-0002 due to a PATH problem) only because a probe-style check ran; without that probe the failure would have remained invisible. The hooks the audit checks: SessionStart (`engine/tools/hooks/session-start.sh`), Stop / PreCompact (`engine/tools/hooks/mempalace-hook-wrapper.sh`), PostToolUse (`engine/tools/hooks/post-adr-write.sh`, `engine/tools/hooks/post-state-edit.sh`, `engine/tools/hooks/post-mempalace-tool-use.sh`).

#### Registry freshness probe

For each register file (`product/docs/tensions.md`, the dead-weight scanner output, `engine/session/auto_target.json`, `HANDOFF.md`), the probe asks whether content was *captured* in the audit window, not whether the file exists. Probe surface: `git log --since` against the file (commits that modified it), and an inline read for content shape (does the file carry actionable entries, or has it been static for many sessions?). A register with zero captures across the window is a candidate for retirement (per the dead-weight posture below) or for re-examination of whether sessions are actually using it.

## Maintenance probes

Automated probes surface in the audit's "Maintenance findings" subsection of the report. Each runs at session boot via `validate.py --health-probe-only` invoked by `session-start.sh`. Findings accumulate per the soft-warn lifecycle ([ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)) and are first-class inputs to the audit.

### MemPalace HNSW divergence (added S-0084 per Issue #31)

[`engine/tools/probe_palace.py`](../tools/probe_palace.py) shells out to upstream's `mempalace repair-status` (read-only; never opens chromadb) on every session boot and parses the divergence percentage between the SQLite ground truth and the HNSW vector index. Soft-warn `mempalace_hnsw_divergence` fires at ≥10% divergence; LOUD-attention surface at ≥30%. The probe also promotes its overall exit code from 0 (healthy) to 1 (suspect) at ≥10%, which surfaces in `chromadb_palace_health` as a separate signal.

When the audit fires, it should:

1. Read the `mempalace_hnsw_divergence` count from the relevant archive(s)' `outcome_summary_soft_warns`.
2. If non-zero across recent archives, name the divergence percentage in the audit's "Maintenance findings" subsection.
3. **Do NOT recommend `mempalace repair --mode legacy`.** S-0078 confirmed that command destroys SQLite embedding rows (99.7% loss observed at the time; see [`mempalace-operations.md`](mempalace-operations.md) "Known issues" for forensic detail and the upstream tracker).
4. Recommend [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) — non-destructive direct chromadb rebuild, run against a scratch palace copy first, swap to live only after 0% divergence verified.

## Audit posture (not categories — postures)

The four traditional category buckets (Fit / Gaps / Dead-Weight / Bloat) are *organizing prompts for the audit's prose*, not a checklist to complete. Each is a posture to take while reading the project, not a slot to fill.

The leading prompt-question for each posture is **adversarially framed** per [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) — argue against the status quo, surface what's silently ignored, and only preserve with affirmative case. Each posture's recommendations route through the report's User adjudication subsection (per the user-buffered execution principle); the audit *surfaces*, the user *adjudicates*, downstream sessions execute approved actions per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

### Forward-fit map (dual-temporal-frame discipline; per [Issue #44](https://github.com/StarshipSuperjam/paideia/issues/44) and [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md))

**Sibling to Fit posture, applied alongside it.** The S-0086 MemPalace adversarial review surfaced a load-bearing pattern lesson (captured in `paideia/lessons` at S-0086 close): adversarial audits of internal subsystems must weigh BOTH historical fit AND fit-to-CONTINUE; either alone produces a muddled or too-charitable verdict. Retrospective alone is too easy on inertia ("it's been around, sessions cite it, leave it"); prospective alone is too easy on future-optimism ("we're going to use it more, just wait"). Together they constrain the verdict precisely.

The S-0086 audit's most decisive output was its **forward-fit map** — for each upcoming phase / committed-future-need, the system under audit was named **load-bearing**, **candidate-among-substrates**, or **no-role**. Mapping forward state needs to candidate substrates (Postgres + pgvector, MemPalace, ADR + ENGINE_LOG, STATE.md, new) made the scale-back verdict precise: load-bearing core preserved, dead-weight perimeter retired.

**Apply the forward-fit map to any audit of an internal subsystem** — any artifact whose value depends on continued use. Not just MemPalace; the same shape works against validators, registries, ops docs, build-readiness gates, and ADR contracts.

**Required output:** alongside (not instead of) the historical-evidence reading, the audit names what's load-bearing forward, what's a candidate but not committed, and what has no role. The dual-frame produces the most decisive recommendations when historical and forward signals point opposite directions — exactly the cases where retrospective-only or prospective-only would underdetermine the verdict.

The Fit posture below uses the forward-fit map as one of its inputs.

### Fit posture

**Adversarial prompt:** *what machinery is silently ignored, what telemetry is being treated as load-bearing without anyone acting on it, and what category is firing 30+ times per session that no one reads?*

Answer with acted-on-rate analysis and silent-channel probes, not stats:

- Does the validate.py soft-warn distribution surface useful signal, or are we ignoring most warnings? (Per the persistent-warn surface: any category firing in 3+ of last 5 sessions warrants the audit's attention. The validator freshness probe above feeds this with acted-on-rate data.)
- Do ENGINE_LOG entries match what was actually material, or is the project producing material changes that aren't being logged?
- Do ADR statuses reflect reality, or are some `Accepted` ADRs effectively-superseded with no record? (Cross-check against the cascade-discipline soft-warns.)
- **Argue retirement / replacement:** which validator soft-warn categories should be retired (no acted-on signal across the window)? which ADRs should be moved to `Superseded` (effectively superseded but unrecorded)? which telemetry surfaces are plumbing waiting for a function that never arrived?
- Are MemPalace queries surfacing useful prior context, or is recall thin? (The MemPalace freshness probe answers this with content-quality reads, not drawer counts.)
- Are session archives faithfully recording what happened, or is `outcome_summary` becoming a thin gloss?

### Gaps posture

**Adversarial prompt:** *if a new collaborator joined the project tomorrow and tried to do work, what would they discover is missing only by tripping over it?*

Answer by simulating cold-start consumption of named artifacts (the cold-context probe per audit fits here):

- Tensions in `product/docs/tensions.md` open for >10 sessions — actionable now?
- ADRs referenced in design docs that don't exist yet.
- Authoring patterns in active use without rows in [`expression-contract-instantiation.md`](expression-contract-instantiation.md) per the "no row, no authoring" discipline.
- Open questions in `STATE.md` that haven't progressed.
- **Argue retirement / replacement:** which "missing thing" is actually unneeded (pin a deferral with a decide-trigger to surface this rather than carry the gap as work)? which open question should be closed by ADR rather than carried as a tension?
- Cold-context probe finding: read a randomly-selected operations doc / ADR / register / build-plan chunk as if you have no project context. Do cross-references resolve? Does the prose tell a future cold consumer how to *use* this artifact, or only that it exists?

### Infrastructure-without-function (sharpened dead-weight posture)

**Adversarial prompt:** *argue this candidate's retirement. What's the affirmative case for keeping it? If the case is "inbound references" alone, the references are themselves candidates for retirement.*

This is the posture that catches the failure mode the user named at S-0042: a file referenced by infrastructure but never *used* — plumbing waiting for a function that never arrived. The reference-count axis alone misses this; reference count says "anyone pointing at this?" but the operative question is "is it doing work?"

Use the dead-weight scanner output as a starting point, then ask of each candidate:

- A register file: does it carry entries? If no entries across 20+ sessions of opportunity, the register is plumbing. (The registry freshness probe above feeds this.)
- An ops doc: has any session ever cited following it? If the only references are the README index entry, no session has used it.
- A decide-trigger / decide-before marker: has the pinned phase passed? If yes, the marker is stale and the decision either belongs in an ADR now or should be retired.
- An ADR marked `Deprecated` for >20 sessions with no successor: archive consideration.
- A stale worktree: per `git worktree list`, prune candidates surface here.

Each surfaced candidate ends with an explicit *recommendation*: **recommend retire**, **recommend convert to active use**, or **recommend preserve-with-affirmative-case** (the affirmative case must specify *what work this artifact does that no other artifact does* — not "inbound references" alone). The dispositions are recommendation-shape per the user-buffered execution principle; the user adjudicates per the report's User adjudication subsection. Saying "leave it for now" without naming why is the failure mode this audit exists to catch.

**Required output:** ≥1 affirmative retire-candidate-recommendation. If none, the audit authors an explicit "no retire candidates this audit" subsection that adversarially scrutinizes its own claim ("I argue no retire candidates because X; if X were false, Y would be a candidate").

### Bloat posture

**Adversarial prompt:** *if the project's machinery were forced to halve in size, what would go first?*

The thought experiment surfaces what's load-bearing vs accumulated:

- Operations docs > ~300 lines — split if multiple concerns, retire if grown past purpose.
- ADRs that should have been one decision but became three (consolidation candidates).
- Validator categories that fire constantly but never get acted on (the persistent-warn 10-of-N escalation criterion). The Fit-posture validator freshness probe identifies these; bloat asks whether they should be retired.
- Session shutdown sequences taking longer than the productive work — which steps should be retired or compressed?
- **Argue retirement / replacement:** which doc / ADR / convention should go first? Which validator check is overhead the project no longer needs?

## Accumulated pushbacks and lessons (per [Issue #36](https://github.com/StarshipSuperjam/paideia/issues/36) and [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md))

The `pushback` and `lesson` MemPalace tags (per [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md)) exist precisely to be retrieved later. The `pushback` tag captures verbatim moments where a real risk was named and a course correction happened; the `lesson` tag captures procedural failure modes the project should not re-attempt. They are the project's accumulated complaints and learnings. **The audit is the natural consumer.**

Per CLAUDE.md "Posture vs machinery": the pushback rule has no log and no audit; a session that fails to surface a real risk leaves no trace. The `pushback` tag is the *partial* mechanization. Without the audit consuming it, the partial mechanization is itself plumbing waiting for a function that never arrived — exactly what the audit's operative diagnostic question is built to surface. Same logic for `lesson`: capturing a procedural failure mode only pays off if some downstream pass actually reads the captures. The health-check is that pass.

The audit AI runs the following queries during prose authoring (the `health_check.py` script feeds adoption *counts* per [Issue #28](https://github.com/StarshipSuperjam/paideia/issues/28); the audit AI reads the *content*):

```text
mempalace_search(query="<topic-derived-from-recent-archives>",
                 tags=["pushback"], limit=10)
   — drawers since last_audit_session

mempalace_search(query="<topic-derived-from-recent-archives>",
                 tags=["lesson"], limit=10)
   — drawers since last_audit_session
```

Topic terms derive from recent archives' `working_on` and `outcome_summary` fields (per the MemPalace freshness probe pattern), plus catch-all queries against the audit window's themes. The audit reads each returned drawer's verbatim content — *not* just the title — and surfaces clusters in prose:

- **Cluster of pushbacks against the same risk-class** → posture rule that hasn't been mechanized → recommendation for new ADR, validator soft-warn, or hook gate.
- **Cluster of lessons against the same workflow** → ops-doc gap or missing validator check → recommendation for ops-doc update or validator addition.
- **Zero captures across the window** → meaningful signal too: either the posture wasn't exercised (audit-window had no pushback-worthy moments) OR the capture surface is failing silently again (the S-0078 vector with Issue #27). The audit distinguishes the two by sampling working-on subjects against `mempalace_diary_read` content; if diary entries describe pushback-shaped moments that no `pushback` drawer captures, the surface is failing.

The audit produces *concrete recommendations* in this section — new ADR / ops-doc update / validator check / posture-rule mechanization — not just a finding list. Per the user-buffered execution principle, recommendations route through the User adjudication subsection; the user adjudicates; downstream sessions execute approved recommendations via Issues per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) (label `health-check-finding` for cross-session deferrals).

## Report template

The canonical template lives at [`docs/health-checks/TEMPLATE.md`](../../docs/health-checks/TEMPLATE.md). Author the audit's report at `docs/health-checks/S-NNNN.md` against that template. The report is the byproduct; the audit's value lives in the prose. Avoid template-by-rote completion.

The template carries (top-to-bottom):

- **Freshness probes run** — what was probed and what each probe surfaced (per the freshness-probe inventory above). Required; non-empty.
- **Operative diagnostic applied** — restatement of how "is this thing doing the work it was created to do?" applied to surfaced candidates. The dead-weight scanner output is evidence; the audit's judgment is what makes this section non-trivial.
- **Non-obvious finding(s)** — ≥1, not on any mechanical scanner's output.
- **Fit / Gaps / Infrastructure-without-function / Bloat** — each posture's adversarial prompt-question; observations + recommendations. The Infrastructure-without-function dispositions are recommendation-shape: `recommend retire / recommend convert / recommend preserve-with-affirmative-case`.
- **Accumulated pushbacks and lessons** — populated with `mempalace_search` results, drawer reading, and any cluster-driven recommendations.
- **Affirmative retire candidates** — ≥1 retire-candidate-with-reasoning OR an explicit "no retire candidates this audit" subsection adversarially scrutinizing its own claim.
- **Cold-context probe** — what artifact was randomly selected, what a context-cold consumer would see, what gaps surfaced.
- **User adjudication** — populated inline when the audit is interactive (audit AI surfaces each finding via AskUserQuestion + records the disposition + files approved Issues in the same session per the "User-adjudicated execution" section above); left **blank on arrival** when the audit is routine-fired (unattended) — a subsequent interactive session populates the table and routes approved findings to Issues at that time.
- **Cadence calibration** — is the cadence right? If consistently no-action, raise. If consistently large action lists, lower.
- **Summary** — one paragraph: what the project's discipline looks like now vs. last check.

### Hand-authoring an audit report

The script's default flow renders the bullet-list scaffold and writes it to `docs/health-checks/S-NNNN.md`. When the audit-author writes the report by hand (as at S-0077 and S-0141), invoke the script with `--bump-only` instead:

```sh
python3 engine/tools/health_check.py --session S-NNNN --bump-only
```

`--bump-only` skips the audit pipeline + file render entirely and performs only `bump_last_audit_session(session_id)`. The hand-authored file is preserved verbatim; the `last_audit_session` field is bumped so the SessionStart hook + `validate.py`'s `health_check_overdue` check both clear correctly. Mutually exclusive with `--dry-run` at argparse level. Per [ADR 0022](../adr/0022-periodic-project-health-checks.md) S-0149 Consequences amendment, closes [Issue #108](https://github.com/StarshipSuperjam/paideia/issues/108).

After User adjudication, each accepted recommendation routes through one of four execution lanes:

- **Inline trivial cleanup** — only for cleanups that fit the standard "default to fix-in-context" rule (typos, broken cross-refs noticed in passing). The user-buffered execution principle reserves the audit session itself for findings + recommendations; substantive retire / convert / replace actions route through the lanes below, not inline.
- **Next-session work item in STATE.md** — large items requiring substantial scope.
- **New GitHub Issue per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md)** with label `health-check-finding` (cross-session deferrals; the cleanup-batch workflow picks them up later). This is the default lane for adversarial recommendations.
- **New tension in `product/docs/tensions.md`** if the item isn't yet actionable.

## Cadence policy

Defaults work for most phases. Re-evaluate the cadence:

- If health checks consistently produce no actionable findings — raise the cadence (e.g., 10 → 20 → 30).
- If health checks consistently produce large finding lists — lower the cadence (e.g., 10 → 5).
- During transitions between phases — consider a one-off audit at the boundary, independent of the regular cadence.
- The cadence was tightened from 30 → 10 at S-0033 because the S-0032 MemPalace audit surfaced enough accumulated silent failures that the 30-session window was too sparse.
- The cadence was raised from 10 → 20 at S-0097 (alongside the deferred cadence-fired audit that was the formal first exercise of [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md)) because routine sessions per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) consume slots in 8–12-session batches executing similar tasks against a single target — slot-count under cadence-10 stopped tracking telemetry-variety once routines became a regular session shape. The raise lets each cadence window cover ≥1 routine batch plus several interactive sessions, producing a more diverse audit-input pool. Adjust further if subsequent audits show drift accumulating between checks (lower) or audits consistently producing no actionable findings (raise further). See [ADR 0022](../adr/0022-periodic-project-health-checks.md) S-0097 Consequences amendment for the full rationale; `health_check_cadence_history` in `engine/session/register_state.json` records the timeline with reasoning.

## See also

- [ADR 0022](../adr/0022-periodic-project-health-checks.md) — periodic project health checks (parent contract).
- [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) — adversarial stance for project health-check audits (the contract this operational surface implements).
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — gate-side structural sibling: same adversarial-framing pattern at the build-session boundary; same conversational-by-default posture.
- [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — health-check findings route to GitHub Issues with `health-check-finding` label.
- [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — `scope_delivery` field the audit consumes (decision 2 of the ADR; decision 3's context-telemetry was retired at S-0083 per the ADR's amendment).
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate; the cadence audit at S-0087 is the first exercise of ADR 0057.
- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — `pushback` and `lesson` tag specifics the Accumulated-pushbacks-and-lessons section consumes.
- [`docs/health-checks/TEMPLATE.md`](../../docs/health-checks/TEMPLATE.md) — canonical report template sessions populate.
- [`engine/tools/health_check.py`](../tools/health_check.py) — script-generated mechanical input; `audit_mempalace()` runs wing-agnostic `pushback`/`lesson` adoption-count probes (direct chromadb-sqlite read per Issue #128, S-0163).
- [`engine/tools/scan_orphans.py`](../tools/scan_orphans.py) — multi-axis dead-weight scanner.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — telemetry sources fed by shutdown.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn categories the audit consumes.
