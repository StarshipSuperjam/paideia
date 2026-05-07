# Health Check S-NNNN — YYYY-MM-DD

> Authored by S-NNNN against the cadence trigger (or on-demand). Per [ADR 0022](../../engine/adr/0022-periodic-project-health-checks.md) and [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md). Producing script: `python3 engine/tools/health_check.py --session S-NNNN`. Operational surface: [`engine/operations/health-check.md`](../../engine/operations/health-check.md).
>
> **The audit is conversational by default — surface findings + guidance suggestions to the user; the user adjudicates; downstream sessions execute approved actions.** The "User adjudication" subsection below is left **blank on arrival** by the audit author. Do not pre-fill it. (Per ADR 0057 user-buffered execution.)

**Cadence:** every <N> sessions. Last check: S-NNNN (Δ = <delta>).

## Freshness probes run

> Per [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md) stats-as-proxy-for-function. Each external system the audit references gets a fresh content probe at audit-time. Counts and existence checks alone do not satisfy this section.

- **MemPalace.** `mempalace search` against ≥3 representative recent terms (derived from last sessions' `working_on` / `outcome_summary`). Result: <observation about content quality, not just drawer count>.
- **Validator.** Acted-on rate of soft-warns across the audit window (`git log --grep` per persistent category vs. archive `outcome_summary_soft_warns` deltas). Result: <observation>.
- **Supabase.** Most-recent migration's empirical effect (sample row counts, predicate distribution, schema shape vs. contract header). Result: <observation>.
- **Hooks.** `.claude/logs/*-hook.log` tail across the audit window — verify recent fires show `OK exit=0`. Result: <observation per hook>.
- **Registries.** Capture rate per register (`tensions.md`, dead-weight scanner output, `auto_target.json`, `HANDOFF.md`) — `git log --since` + content read. Result: <observation per register>.

## Operative diagnostic applied

> Brief restatement: which files / categories / rules surfaced as candidates against "is this thing doing the work it was created to do, or is it plumbing waiting for a function that never arrived?" The dead-weight scanner output ([`engine/health_check/dead_weight_candidates_S-NNNN.md`](../../engine/health_check/dead_weight_candidates_S-NNNN.md)) goes here as evidence; the audit's judgment is what makes this section non-trivial.

<observations>

## Non-obvious finding(s)

> ≥1 required, per [`engine/operations/health-check.md`](../../engine/operations/health-check.md). Not on any mechanical scanner's output. The audit's own observation — what the AI/user noticed that no rule would catch.

### Non-obvious finding A — <title>

<observation + recommendation, routed through User adjudication below>

## Fit

> **Adversarial prompt:** *what machinery is silently ignored, what telemetry is being treated as load-bearing without anyone acting on it, and what category is firing 30+ times per session that no one reads?*

- Validate.py soft-warn distribution across last <N> sessions, with acted-on-rate per persistent category: <observation>. <recommendation or "no action with reasoning">.
- ENGINE_LOG fidelity (every closed session in archive/ has a corresponding entry?): <observation>. <recommendation or "no action">.
- ADR statuses match reality (no Accepted ADRs that are effectively superseded)?: <observation>. <recommendation or "no action">.
- MemPalace recall content quality on representative recent queries (per the freshness probe above): <observation>. <recommendation or "no action">.
- **Argue retirement / replacement:** which validator soft-warn categories should be retired (no acted-on signal)? which `Accepted` ADRs should move to `Superseded`? <recommendation or "no candidate, because <reasoning>">.

## Gaps

> **Adversarial prompt:** *if a new collaborator joined the project tomorrow and tried to do work, what would they discover is missing only by tripping over it?*

- Tensions in `product/docs/tensions.md` open >10 sessions: <list>. <recommendation per tension or "no action">.
- ADRs referenced in design docs that don't exist yet: <list>. <recommendation or "no action">.
- Operations docs added but never read (no inbound MemPalace references, no inbound link citations): <list>. <recommendation or "no action">.
- Open questions in `engine/STATE.md` that haven't progressed: <list>. <recommendation or "no action">.
- ADR Consequences-section deliverables anticipated for past sessions but absent on disk (per validate.py adr_consequences_deliverable_audit): <list>. <recommendation or "no action">.
- **Argue retirement / replacement:** which "missing thing" is actually unneeded? which open question should be closed by ADR rather than carried? <recommendation or "no candidate, because <reasoning>">.

## Infrastructure-without-function (dead weight)

> **Adversarial prompt:** *argue this candidate's retirement. What's the affirmative case for keeping it? If the case is "inbound references" alone, the references are themselves candidates for retirement.*

For each scanner-surfaced candidate AND any non-obvious additions, the explicit *recommendation*: **recommend retire**, **recommend convert to active use**, or **recommend preserve-with-affirmative-case** (the affirmative case must specify *what work this artifact does that no other artifact does* — not "inbound references" alone). Recommendations route through User adjudication below.

- ADRs marked `Deprecated` for >20 sessions with no successor: <list>. <recommendation>.
- Operations docs that haven't been linked-to or referenced in N sessions: <list>. <recommendation>.
- Register files unconsumed for many sessions (per the registry freshness probe above): <list>. <recommendation>.
- Stale worktrees per `git worktree list`: <list>. <recommendation>.
- ADR back-reference orphans (per validate.py adr_back_reference_orphan, excluding annotated Orphan-OK): <list>. <recommendation>.

## Bloat

> **Adversarial prompt:** *if the project's machinery were forced to halve in size, what would go first?*

- Operations docs > ~300 lines: <list with line counts>. <recommendation: split / retire / no action>.
- ADRs that should have been one decision but became three: <list>. <recommendation>.
- Validator categories that fire constantly but never get acted on (persistent soft-warns per ADR 0042; the Fit-posture validator freshness probe identifies these): <list with persistence count>. <recommendation: promote / retire / accept>.
- Session shutdown sequences taking longer than the productive work (median session duration trend from archive/ metadata): <observation>. <recommendation>.
- **Argue retirement / replacement:** which doc / ADR / convention should go first? <recommendation or "no candidate, because <reasoning>">.

## Accumulated pushbacks and lessons

> Per [Issue #36](https://github.com/StarshipSuperjam/paideia/issues/36) and [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md). The audit reads `pushback`-tagged and `lesson`-tagged drawer content (not just count) since `last_audit_session`, surfaces clusters, recommends posture rules for mechanization when clusters appear.

**Pushback drawers since last audit:** <count>. **Lesson drawers since last audit:** <count>.

### Pushback clusters

<For each cluster of pushbacks against the same risk-class, name the cluster and recommend whether the posture rule should be mechanized (new ADR, validator soft-warn, hook gate). If zero clusters or zero captures, name the signal explicitly — was the posture not exercised, or is the capture surface failing silently?>

### Lesson clusters

<Same shape: cluster of lessons against the same workflow → recommendation for ops-doc update, validator addition, or new ADR.>

## Affirmative retire candidates

> Per [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md): ≥1 retire-candidate-with-reasoning OR an explicit "no retire candidates this audit" subsection adversarially scrutinizing its own claim. Recommendations route through User adjudication below.

### Retire candidate A — <title>

<artifact + affirmative argument for retirement + what would be lost>

<OR, if no candidates surfaced:>

### No retire candidates this audit

<Adversarial scrutiny of the claim: "I argue no retire candidates because X; if X were false, Y would be a candidate.">

## Cold-context probe

> Per [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md): the audit reads ≥1 randomly-selected artifact as if it had no project context. Surfaces compound drift in artifacts the warm-context audit can't see.

**Artifact selected (random):** <path>. <Random-pick procedure: e.g., `find` filter + `shuf -n 1` against operations docs, ADRs, registers, build-plan chunks, hook scripts.>

**Cold-read findings:** Do cross-references resolve? Does the prose tell a future cold consumer how to *use* this artifact? Does the artifact name a sibling that no longer exists? Does it carry a rule whose successor superseded it without a back-reference?

<observations + recommendations>

## User adjudication

> **Left blank on arrival.** Per [ADR 0057](../../engine/adr/0057-adversarial-stance-for-health-check-audits.md) user-buffered execution. The user (or the next interactive session that picks up the audit's recommendations) populates this subsection with accept/reject/modify dispositions per recommendation. The audit closes with recommendations *surfaced*, not *executed*.
>
> Recommendations route to one of four execution lanes per [ADR 0048](../../engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md):
> - **Inline trivial cleanup** (typos, broken cross-refs noticed in passing) — only for fix-in-context items, NOT adversarial recommendations.
> - **Next-session work item in `engine/STATE.md`** — large items requiring substantial scope.
> - **New GitHub Issue** with `health-check-finding` label — default lane for adversarial recommendations.
> - **New tension in `product/docs/tensions.md`** — if not yet actionable.

<populated post-audit by the user>

## Cadence calibration

Is the current cadence (<N> sessions) right for current project velocity?

- If consistently no-action: raise (e.g., 10 → 20).
- If consistently large action lists: lower (e.g., 10 → 5).
- During phase transitions: consider one-off audit at the boundary, independent of the cadence.

This audit's recommendation: <keep at N | raise to M | lower to M> — routed through User adjudication above.

## Summary

<One paragraph: what the project's discipline looks like now vs. last check, and what's queued for next session as a result of this audit's recommendations once user adjudication completes.>
