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

## Audit categories

### Fit

Does the machinery match what the project is actually producing? Look at the last N sessions and ask:

- Does the validate.py soft-warn distribution surface useful signal, or are we ignoring most warnings?
- Do ENGINE_LOG entries match what was actually material, or is the project producing material changes that aren't being logged?
- Do ADR statuses reflect reality, or are some `Accepted` ADRs effectively-superseded with no record?
- Are MemPalace queries surfacing useful prior context, or is recall thin?

### Gaps

What's missing that should be there? Look at:

- Tensions in `docs/tensions.md` that have been open for >10 sessions — are any actionable now?
- ADRs referenced in design docs that don't exist yet.
- Files in `docs/operations/` that have been added but never read (search MemPalace for references).
- Open questions in `STATE.md` that haven't progressed.

### Dead weight

What's in the repo that no longer earns its keep?

- ADRs marked `Deprecated` for >20 sessions with no successor — should they be archived?
- Operations docs that haven't been linked-to or referenced in N sessions.
- `docs/ideation.md` entries that have been sitting unconsumed for many sessions — promote, retire, or accept they're long-tail.
- Stale worktrees per `git worktree list`.

### Bloat

What's grown past its purpose?

- Operations docs > ~300 lines — split if multiple concerns.
- ADRs that should have been one decision but became three.
- Validation categories that fire constantly but never get acted on.
- Session shutdown sequences taking longer than the productive work.

## Telemetry inputs

The audit consumes:

- `tools/validate-history.jsonl` (gitignored, per-clone) — soft-warn category trends, validator runtime drift, hard-fail incidence.
- `session/archive/S-NNNN.json` per session — `started_at`, `closed_at`, `status`, `outcome_summary`, branch.
- ADR collection — counts of Accepted / Deprecated / Superseded over time.
- ENGINE_LOG entries — categorized engine changes by date.
- MemPalace stats (`mempalace_status`, `mempalace_kg_stats`) — drawer growth, room balance, last-write activity.

## Report template

Author at `docs/health-checks/S-NNNN.md`:

```markdown
# Health Check S-NNNN — YYYY-MM-DD

**Cadence:** every <N> sessions. Last check: S-NNNN (<delta>).

## Fit

<observations + corrective actions or "no action">

## Gaps

<observations + corrective actions or "no action">

## Dead weight

<observations + corrective actions or "no action">

## Bloat

<observations + corrective actions or "no action">

## Cadence calibration

<is the cadence right? If consistently no-action, raise. If consistently large action lists, lower.>

## Summary

<one paragraph: what the project's discipline looks like now vs. last check, and what's queued for next session>
```

Each corrective action either:

- Lands in this session as a follow-on commit (small, scope-bounded fixes).
- Becomes the next session's work item in STATE.md (large items).
- Becomes a new tension in `docs/tensions.md` if it's not yet actionable.

## Cadence policy

Defaults work for most phases. Re-evaluate the cadence:

- If health checks consistently produce no actionable findings — raise the cadence (e.g., 10 → 20 → 30).
- If health checks consistently produce large finding lists — lower the cadence (e.g., 10 → 5).
- During transitions between phases — consider a one-off audit at the boundary, independent of the regular cadence.
- The cadence was tightened from 30 → 10 at S-0033 because the S-0032 MemPalace audit surfaced enough accumulated silent failures that the 30-session window was too sparse. Raise back when the project demonstrates more consistent execution (multiple consecutive cadence audits with minimal corrective action).

## See also

- ADR 0022 (lands S-0003) — periodic project health checks.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — telemetry sources fed by shutdown.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn categories the audit consumes.
