# Project health check

> Periodic audit of the project's own machinery: does our discipline match what we're producing? Per ADR 0022 (lands in S-0003). Cadence trigger fires automatically at session boot when `last_claimed mod health_check_cadence == 0` (default cadence: 30).

The first check is expected around S-0030. `tools/health_check.py` lands in one of the sessions ~S-0025. Until then, the audit is run by the AI manually against the categories below.

## When the trigger fires

At session boot, `/start-engine` parses the trailing 4-digit counter from `last_claimed` (e.g., `S-0030` → `0030` → `30`) and computes `counter % cadence`. If `0`, surface the proposal:

> "Last claimed was S-0030. Cadence trigger fires for a project health check. Run the audit now or defer?"

The user's response routes:

- **Accept** — the session's work *is* the audit. Author a report (template below) and commit it under `docs/health-checks/S-NNNN.md`.
- **Defer** — proceed with planned work; the trigger fires again next session, and again the session after, until accepted or the user explicitly disables the cadence in `register_state.json` for some bounded window.

The cadence is configurable per-project in `register_state.json` (add `health_check_cadence: <integer>`). 30 is the default. Lower for fast-moving phases; higher when phases are long and structurally settled.

## Audit categories

### Fit

Does the machinery match what the project is actually producing? Look at the last N sessions and ask:

- Does the validate.py soft-warn distribution surface useful signal, or are we ignoring most warnings?
- Do CHANGELOG entries match what was actually material, or is the project producing material changes that aren't being logged?
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
- CHANGELOG entries — categorized changes by date.
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

- If health checks consistently produce no actionable findings — raise the cadence (e.g., 30 → 50).
- If health checks consistently produce large finding lists — lower the cadence (e.g., 30 → 15).
- During transitions between phases — consider a one-off audit at the boundary, independent of the regular cadence.

## See also

- ADR 0022 (lands S-0003) — periodic project health checks.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — telemetry sources fed by shutdown.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn categories the audit consumes.
