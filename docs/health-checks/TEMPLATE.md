# Health Check S-NNNN — YYYY-MM-DD

> Authored by S-NNNN against the cadence trigger (or on-demand). Per [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md). Producing script: `python3 engine/tools/health_check.py --session S-NNNN`.

**Cadence:** every <N> sessions. Last check: S-NNNN (<delta>).

## Fit

> Does the machinery match what the project is actually producing?

- Validate.py soft-warn distribution across last <N> sessions: <observation>. <corrective action or "no action">.
- ENGINE_LOG fidelity (every closed session in archive/ has a corresponding entry?): <observation>. <action or "no action">.
- ADR statuses match reality (no Accepted ADRs that are effectively superseded)?: <observation>. <action or "no action">.
- MemPalace recall on representative recent queries: <observation, including drawer counts and quality>. <action or "no action">.

## Gaps

> What's missing that should be there?

- Tensions in `product/docs/tensions.md` open >10 sessions: <list>. <per-tension action or "no action">.
- ADRs referenced in design docs that don't exist yet: <list>. <action or "no action">.
- Operations docs added but never read (no inbound MemPalace references, no inbound link citations): <list>. <action or "no action">.
- Open questions in `engine/STATE.md` that haven't progressed: <list>. <action or "no action">.
- ADR Consequences-section deliverables anticipated for past sessions but absent on disk (per validate.py adr_consequences_deliverable_audit): <list>. <action or "no action">.

## Dead weight

> What's in the repo that no longer earns its keep?

- ADRs marked `Deprecated` for >20 sessions with no successor: <list>. <action or "no action">.
- Operations docs that haven't been linked-to or referenced in N sessions: <list>. <action or "no action">.
- `product/docs/ideation.md` entries unconsumed for many sessions: <list>. <action: promote, retire, or accept long-tail>.
- Stale worktrees per `git worktree list`: <list>. <action or "no action">.
- ADR back-reference orphans (per validate.py adr_back_reference_orphan, excluding annotated Orphan-OK): <list>. <action or "no action">.

## Bloat

> What's grown past its purpose?

- Operations docs > ~300 lines: <list with line counts>. <action: split or "no action">.
- ADRs that should have been one decision but became three: <list>. <action or "no action">.
- Validation categories that fire constantly but never get acted on (persistent soft-warns per ADR 0042): <list with persistence count>. <action: promote/accept/address per soft-warn-lifecycle.md>.
- Session shutdown sequences taking longer than the productive work (median session duration trend from archive/ metadata): <observation>. <action or "no action">.

## Cadence calibration

Is the current cadence (<N> sessions) right for current project velocity?

- If consistently no-action: raise (e.g., 30 → 50).
- If consistently large action lists: lower (e.g., 30 → 15).
- During phase transitions: consider one-off audit at the boundary, independent of the cadence.

This audit's recommendation: <keep at N | raise to M | lower to M>.

## Summary

<One paragraph: what the project's discipline looks like now vs. last check, and what's queued for next session as a result of this audit.>
