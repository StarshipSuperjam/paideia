# Project health check

> Periodic audit of the project's own machinery: does our discipline match what we're producing? Per ADR 0022 (lands in S-0003). Cadence trigger fires automatically at session boot when `next_id mod health_check_cadence == 0` (default cadence: 30) — the slot about to be claimed is the cadence-numbered session.

The first check landed at S-0030 (manual fire at the project-setup-to-project-build phase boundary; see [`docs/health-checks/S-0030.md`](../../docs/health-checks/S-0030.md)). [`engine/tools/health_check.py`](../tools/health_check.py) was authored at S-0029 per [ADR 0022](../adr/0022-periodic-project-health-checks.md). Future cadence triggers fire at S-0060, S-0090, etc.

## When the trigger fires

At session boot, the SessionStart hook (`engine/tools/hooks/session-start.sh` per [ADR 0043](../adr/0043-hook-architecture.md)) parses the trailing 4-digit counter from `next_id` (the slot about to be claimed; e.g., `next_id: "0030"` → `30`) and computes `counter % cadence`. If `0`, surface the proposal:

> "Next slot is S-0030. Cadence trigger fires for a project health check. Run the audit now or defer?"

The `/start-engine` slash command's documented procedure mirrors this logic at step 2; the hook surfaces the prompt regardless of how the session is launched. The pre-S-0031 logic used `last_claimed` rather than `next_id` and fired the trigger at the session AFTER the cadence-numbered session, contradicting ROADMAP.md and ADR 0022 prose intent. The S-0030 audit surfaced the off-by-one; S-0031 corrected it across all three carriers (this doc, `start-engine.md`, the SessionStart hook).

The user's response routes:

- **Accept** — the session's work *is* the audit. Author a report (template below) and commit it under `docs/health-checks/S-NNNN.md`.
- **Defer** — proceed with planned work; the trigger fires again next session, and again the session after, until accepted or the user explicitly disables the cadence in `register_state.json` for some bounded window.

The cadence is configurable per-project in `register_state.json` (add `health_check_cadence: <integer>`). 30 is the default. Lower for fast-moving phases; higher when phases are long and structurally settled.

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

- If health checks consistently produce no actionable findings — raise the cadence (e.g., 30 → 50).
- If health checks consistently produce large finding lists — lower the cadence (e.g., 30 → 15).
- During transitions between phases — consider a one-off audit at the boundary, independent of the regular cadence.

## See also

- ADR 0022 (lands S-0003) — periodic project health checks.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — telemetry sources fed by shutdown.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn categories the audit consumes.
