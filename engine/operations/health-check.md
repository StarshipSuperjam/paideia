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

## Mechanical inputs (the audit consumes; the audit is not consumed by them)

### Dead-weight scanner

[`engine/tools/scan_orphans.py`](../tools/scan_orphans.py) — multi-axis scanner that surfaces candidate files for the dead-weight conversation. Five axes, each independent:

- **reference-count** — files with fewer than 3 inbound references.
- **last-mod-age** — files unchanged across 20+ sessions of project history AND with low inbound references (the dual filter prevents foundation reference docs from surfacing).
- **register-empty** — register/queue files (currently `ideation.md`, `tensions.md`) with no captured entries.
- **ops-doc-uncited** — operations docs not cited in any of the last 20 session archives.
- **stale-marker** — files carrying decide-trigger / decide-before / open decide-by markers whose pinned phase or session has passed.

Run at audit-session boot:

```bash
python3 engine/tools/scan_orphans.py --output engine/health_check/dead_weight_candidates_S-NNNN.md
```

Each candidate is annotated with axis, signal, last substantive change, and inbound reference count. The audit walks the file top-to-bottom and triages each candidate against the operative diagnostic question. **Surfacing in multiple axes is a stronger signal.** A file that flags both `ops-doc-uncited` AND `last-mod-age` AND `reference-count` is almost certainly dead weight; the audit confirms by reading the file.

### Validator telemetry

`tools/validate-history.jsonl` (gitignored, per-clone) — soft-warn category trends, validator runtime drift, hard-fail incidence.

`engine/session/archive/S-NNNN.json` — per-session `outcome_summary_soft_warns` (the canonical structured field per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)), `started_at`, `closed_at`, `status`, `outcome_summary`, branch, and (post-ADR-0049) `scope_delivery`. (Pre-S-0083 archives also carry `transcript_token_pct` / `transcript_token_estimate` / `tokenizer_used` from the retired ADR 0049 decision 3 telemetry; new archives do not.)

### Project state

ADR collection (counts by status across time), ENGINE_LOG entries (categorized engine changes by date), MemPalace stats (`mempalace_status`, `mempalace_kg_stats` — drawer growth, room balance, last-write activity).

## Audit posture (not categories — postures)

The four traditional category buckets (Fit / Gaps / Dead-Weight / Bloat) are *organizing prompts for the audit's prose*, not a checklist to complete. Each is a posture to take while reading the project, not a slot to fill.

### Fit posture

Walk through the project asking: **does the machinery match what the project is actually producing?**

- Does the validate.py soft-warn distribution surface useful signal, or are we ignoring most warnings? (Per the persistent-warn surface: any category firing in 3+ of last 5 sessions warrants the audit's attention.)
- Do ENGINE_LOG entries match what was actually material, or is the project producing material changes that aren't being logged?
- Do ADR statuses reflect reality, or are some `Accepted` ADRs effectively-superseded with no record? (Cross-check against the cascade-discipline soft-warns.)
- Are MemPalace queries surfacing useful prior context, or is recall thin?
- Are session archives faithfully recording what happened, or is `outcome_summary` becoming a thin gloss?

### Gaps posture

What's missing that should be there?

- Tensions in `product/docs/tensions.md` open for >10 sessions — actionable now?
- ADRs referenced in design docs that don't exist yet.
- Authoring patterns in active use without rows in [`expression-contract-instantiation.md`](expression-contract-instantiation.md) per the "no row, no authoring" discipline.
- Open questions in `STATE.md` that haven't progressed.

### Infrastructure-without-function (sharpened dead-weight posture)

This is the posture that catches the failure mode the user named at S-0042: a file referenced by infrastructure but never *used* — plumbing waiting for a function that never arrived. The reference-count axis alone misses this; reference count says "anyone pointing at this?" but the operative question is "is it doing work?"

Use the dead-weight scanner output as a starting point, then ask of each candidate:

- A register file: does it carry entries? If no entries across 20+ sessions of opportunity, the register is plumbing.
- An ops doc: has any session ever cited following it? If the only references are the README index entry, no session has used it.
- A decide-trigger / decide-before marker: has the pinned phase passed? If yes, the marker is stale and the decision either belongs in an ADR now or should be retired.
- An ADR marked `Deprecated` for >20 sessions with no successor: archive consideration.
- A stale worktree: per `git worktree list`, prune candidates surface here.

Each surfaced candidate ends with an explicit disposition: **retire**, **convert to active use**, or **preserve with a note explaining why the absence of activity is intentional**. Saying "leave it for now" without naming why is itself the failure mode this audit exists to catch.

### Bloat posture

What's grown past its purpose?

- Operations docs > ~300 lines — split if multiple concerns.
- ADRs that should have been one decision but became three.
- Validator categories that fire constantly but never get acted on (the persistent-warn 10-of-N escalation criterion).
- Session shutdown sequences taking longer than the productive work.

## Report template

Author at `docs/health-checks/S-NNNN.md`. The report is the byproduct; the audit's value lives in the prose. Avoid template-by-rote completion.

```markdown
# Health Check S-NNNN — YYYY-MM-DD

**Cadence:** every <N> sessions. Last check: S-NNNN (<delta>).

## Operative diagnostic applied

Brief restatement: which files / categories / rules surfaced as
candidates against "is this thing doing the work it was created to do?"
The dead-weight scanner output goes here as evidence; the audit's
judgment is what makes this section non-trivial.

## Non-obvious finding(s)

At least one. Not on any mechanical scanner's output. The audit's
own observation — what the AI/user noticed that no rule would catch.

## Fit

<observations + corrective actions or "no action with reasoning">

## Gaps

<observations + corrective actions or "no action with reasoning">

## Infrastructure-without-function (dead weight)

For each scanner-surfaced candidate AND any non-obvious additions,
the explicit disposition: retire, convert to active use, or preserve
with a note explaining why the absence of activity is intentional.

## Bloat

<observations + corrective actions or "no action with reasoning">

## Cadence calibration

Is the cadence right? If consistently no-action, raise. If
consistently large action lists, lower.

## Summary

One paragraph: what the project's discipline looks like now vs. last
check, and what's queued for next session.
```

Each corrective action either:

- Lands in this session as a follow-on commit (small, scope-bounded fixes — the default per CLAUDE.md "Default to fix-in-context").
- Becomes the next session's work item in STATE.md (large items requiring substantial scope).
- Becomes a new GitHub Issue per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) with label `health-check-finding` (cross-session deferrals; the cleanup-batch workflow can pick them up later).
- Becomes a new tension in `product/docs/tensions.md` if it's not yet actionable.

## Cadence policy

Defaults work for most phases. Re-evaluate the cadence:

- If health checks consistently produce no actionable findings — raise the cadence (e.g., 10 → 20 → 30).
- If health checks consistently produce large finding lists — lower the cadence (e.g., 10 → 5).
- During transitions between phases — consider a one-off audit at the boundary, independent of the regular cadence.
- The cadence was tightened from 30 → 10 at S-0033 because the S-0032 MemPalace audit surfaced enough accumulated silent failures that the 30-session window was too sparse. Raise back when the project demonstrates more consistent execution (multiple consecutive cadence audits with minimal corrective action).

## See also

- [ADR 0022](../adr/0022-periodic-project-health-checks.md) — periodic project health checks.
- [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — health-check findings route to GitHub Issues with `health-check-finding` label.
- [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — `scope_delivery` field the audit consumes (decision 2 of the ADR; decision 3's context-telemetry was retired at S-0083 per the ADR's amendment).
- [`engine/tools/scan_orphans.py`](../tools/scan_orphans.py) — multi-axis dead-weight scanner.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — telemetry sources fed by shutdown.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn categories the audit consumes.
