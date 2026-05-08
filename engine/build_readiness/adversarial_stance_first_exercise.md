# Adversarial-stance health-check audit — mechanism-first-exercise gate report

> Authored by S-0085 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first exercise of the adversarial-stance posture that [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) introduces. Required because the contract qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files — the change touches the new ADR + ops doc + TEMPLATE + ADR 0040 See-also + ADR README + CLAUDE.md = 6 surfaces; or alternately criterion #2 if the new validator-acted-on-rate freshness probe formalizes as a soft-warn category, deferred to first-exercise outcome).

## Mechanism summary

[ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) commits five contract elements that downstream cadence audits inherit:

1. **User-buffered execution** — audit findings + guidance suggestions surfaced *before* action; user adjudicates; downstream sessions execute via Issues per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).
2. **Posture inversion** — Fit / Gaps / Infrastructure-without-function / Bloat get adversarial prompt-questions; dispositions become recommendation-shape.
3. **Stats-as-proxy-for-function anti-pattern** — every system reference rests on a *content probe* run during the audit, not a cited count from a prior audit.
4. **Required output: ≥1 affirmative retire-candidate-recommendation** (or an adversarially-scrutinized explicit "no candidates" subsection).
5. **Cold-context probe per audit** — read ≥1 randomly-selected artifact as if no project context.

The operational surface ([`engine/operations/health-check.md`](../operations/health-check.md)) carries the freshness-probe inventory per external system and the new "Accumulated pushbacks and lessons" section. The canonical report template ([`docs/health-checks/TEMPLATE.md`](../../docs/health-checks/TEMPLATE.md)) carries the new sections (Freshness probes run, Accumulated pushbacks and lessons, Affirmative retire candidates, Cold-context probe, User adjudication).

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No (refines the existing audit mode; doesn't add a new session type) |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | Latent — the validator-acted-on-rate freshness probe could formalize as a soft-warn (e.g., `validator_warn_unactioned`); deferred to first-exercise outcome |
| #3 — introduces a new state file the boot procedure reads | No (consumes existing `last_audit_session` from `register_state.json`) |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | **Yes** (6 surfaces: ADR 0057, health-check.md, TEMPLATE.md, ADR 0040 See-also, ADR README, CLAUDE.md) |

**Qualifies; first-exercise gate report needed before unattended use.** This report IS the gate report.

**First exercise: S-0097** (deferred from the S-0087-projected slot for the issue close-out campaign; landed at S-0097 with `slots_since=20` overdue by 10). The audit is at [`docs/health-checks/S-0097.md`](../../docs/health-checks/S-0097.md). Concurrent in-session deliverable: cadence raise from 10 → 20 per [ADR 0022](../adr/0022-periodic-project-health-checks.md) S-0097 Consequences amendment.

## What success at first exercise looks like

The S-0087 audit lands a hand-authored report at `docs/health-checks/S-0087.md` against the new TEMPLATE.md shape. Specifically:

- **Freshness probes run** subsection is non-empty. The audit ran fresh content probes against MemPalace, validator, Supabase, hooks, and registries — not citations of cached stats from S-0077 STATE.md or earlier audits. Each probe entry names what was probed and what it surfaced.
- **Accumulated pushbacks and lessons** subsection is non-empty. The audit ran `mempalace_search` against `pushback` and `lesson` tags scoped to drawers since `last_audit_session: S-0077`, *read each drawer's verbatim content* (not just count), and surfaced clusters in prose. If zero captures across the window, the audit explicitly distinguishes "posture not exercised" from "capture surface failing silently" by sampling diary entries.
- **Affirmative retire candidates** subsection carries ≥1 retire-candidate-with-reasoning OR an explicit "no retire candidates this audit" subsection that adversarially scrutinizes its own claim.
- **Cold-context probe** subsection names which artifact was randomly selected and what gaps a context-cold consumer would see.
- **User adjudication** subsection arrives **blank**. The audit session does not pre-fill it.
- **Posture sections (Fit / Gaps / Infrastructure-without-function / Bloat)** carry adversarial prompt-questions. Infrastructure-without-function dispositions are recommendation-shape (`recommend retire` / `recommend convert` / `recommend preserve-with-affirmative-case`).

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | The audit AI must read MemPalace `pushback`/`lesson` drawer *content* (not just counts) at audit time | **Resolved at S-0097.** The S-0097 audit's "Accumulated pushbacks and lessons" section quotes verbatim from three substantive `[pushback]`-prefixed drawers (S-0005 callback_reference, S-0048 manual-review-framing, S-0071 defer-indefinitely-hedge) and surfaces Cluster A (defer-hedging at session close) with a recommendation for validator-side mechanization. The audit also distinguishes posture-not-exercised from capture-surface-failure for the lesson-drawers (3 tagged) by cross-referencing the hooks freshness probe (substrate healthy) against the campaign's procedural shape (low novel-discovery moments). |
| T1-B | User adjudication subsection must arrive blank — audit cannot pre-fill | **Resolved at S-0097.** The S-0097 report's User-adjudication section carries the canonical placeholder `<populated post-audit by the user>` — eight findings/recommendations are surfaced in posture sections + retire-candidate subsections, all routed via "Routes through User adjudication" tail-lines, none disposed in-session. |
| T1-C | Freshness probes must produce content findings, not cite cached stats | **Resolved at S-0097.** The S-0097 "Freshness probes run" section describes five RUN probes with commands invoked and results observed: five `mempalace_search` queries with similarity scores, validator acted-on-rate per category via `git log --grep` + archive `outcome_summary_soft_warns` deltas, hooks via `tail` of all five `.claude/logs/*.log` files (surfacing the new `env_pointer=missing-supabase-db-url` finding), registries via `git log --since=2026-04-25` + content reads. Supabase live probe explicitly deferred-to-routine with reasoning rather than cited from cached stats. |
| T1-D | Cold-context probe randomly selects an artifact, not the audit's preferred target | **Resolved at S-0097.** The S-0097 "Cold-context probe" subsection names the random-pick command (`find engine/operations engine/adr docs/health-checks engine/build_readiness -name '*.md' -type f \| sort -R \| head -1`) — using `sort -R` as the macOS-friendly substitute for `shuf` (substantive note about Darwin tooling). Picked `engine/operations/cascade-discipline.md`; surfaced one cross-doc handshake gap (the orphan-OK list audit is committed-to but not mechanized). |
| T1-E | ≥1 retire-candidate or adversarially-scrutinized "no candidates" subsection | **Resolved at S-0097.** The S-0097 "Affirmative retire candidates" section carries three retire candidates with affirmative arguments and what-would-be-lost analysis: (A) three legacy `dead_weight_candidates_S-NNNN.md` scanner outputs; (B) two MemPalace-skip soft-warn categories (re-class to `informational-only-accepted`, not full delete); (C) ADR 0049 unkept Consequences promise (in-place amendment). Each routes through User adjudication. |

## Tier 2 findings (settle in advance, document)

- **T2-A — `health_check.py` is not modified.** The script's `audit_mempalace()` already runs `pushback`/`lesson` adoption-count probes via the local `mempalace search` CLI; ADR 0057 documents these as canonical. The first-exercise session does not need to re-implement them. The audit AI runs *additional* MCP-side `mempalace_search` calls during prose authoring against current-session-relevant terms (per the freshness-probe specification in [`engine/operations/health-check.md`](../operations/health-check.md)).

- **T2-B — Random-pick procedure for cold-context probe.** Recommended invocation pattern (the audit may refine):
  ```bash
  find engine/operations engine/adr docs/health-checks engine/build_readiness \
      -name '*.md' -type f | shuf -n 1
  ```
  The audit can broaden the find scope (e.g., add `engine/tools/hooks/*.sh`) or narrow it (focus on artifacts >N sessions old) per its own posture. The discipline: *random selection from the candidate pool*, not auditor-chosen target.

- **T2-C — Freshness-probe outputs feed the posture sections.** The Fit posture's adversarial prompt about "what category is firing 30+ times per session that no one reads" consumes the validator-acted-on-rate probe's output. The Infrastructure-without-function posture consumes the registry capture-rate probe. The audit should structure its prose so the freshness-probe section's findings are *referenced* in the posture sections, not duplicated.

- **T2-D — Cluster detection for `pushback`/`lesson` drawers is AI-judgment work, not script.** Per Issue #36's scope notes; per ADR 0057 Consequences. If volume warrants automation later, that's a follow-on Issue under the audit's own posture, not a precondition for the contract's force.

## Tier 3 findings (forward pointers; deferred)

- **T3-A — Validator soft-warn for unacted persistent warns.** Latent under criterion #2. If the S-0087 first-exercise session surfaces persistent soft-warns with zero acted-on commits across the window, ADR 0042's persistent-warn surface could grow a new validator-side check (`validator_warn_unactioned: <count>`) that promotes after N consecutive audit windows. Defer ADR-level decision until S-0087 surfaces concrete data.

- **T3-B — Posture-rule mechanization driven by `pushback`/`lesson` clusters.** If S-0087 (or any subsequent audit) surfaces a cluster of pushbacks against the same risk-class, the recommendation will likely be "new ADR + validator soft-warn + hook gate." That's normal contract evolution, not a precondition for ADR 0057's force. Defer until concrete clusters surface.

- **T3-C — Apparatus-improvement retrospective for the audit-posture overhaul.** If S-0087's first exercise reveals that the contract over-specified or under-specified, an apparatus-improvement report (build_readiness file class 6) covering the S-0087 → S-NEXT_AUDIT window may be warranted. Defer until two cadence audits have run under the new posture.

## Recovery / abort

The new posture is *additive* over the existing audit framework — the old prompt-questions are preserved alongside the adversarial rewrites; the old four postures still organize the report; the old report sections (Fit / Gaps / Bloat / Cadence calibration / Summary) are unchanged. If S-0087 finds the new sections (Freshness probes run, Accumulated pushbacks and lessons, Affirmative retire candidates, Cold-context probe, User adjudication) consume disproportionate session capacity relative to their value, the contract amends per ADR 0057's amendment discipline rather than reverting.

The recovery shape: ENGINE_LOG-tracked refinement to `health-check.md` and `TEMPLATE.md` based on first-exercise observations. If the contract's posture itself fails (e.g., user-buffered execution proves to fragment audit recommendations across too many subsequent sessions to be effective), a superseding ADR is the path — not a unilateral revert.

## Closure criteria

This first-exercise readiness note closes when:

1. The S-0087 audit (or any subsequent first-exercise audit if S-0087 is consumed by another priority) lands a hand-authored report at `docs/health-checks/S-NNNN.md` against the new TEMPLATE.md shape. — **Done at S-0097 ([docs/health-checks/S-0097.md](../../docs/health-checks/S-0097.md), 20-session audit window covering S-0078 → S-0096).**
2. T1-A through T1-E each move to "Resolved at S-NNNN" with the closure observation. — **Done above (all five T1 rows resolved at S-0097 with closure observations citing audit-report sections).**
3. ENGINE_LOG carries a `Changed` entry referencing the first-exercise audit and any refinements to `health-check.md` / `TEMPLATE.md` the exercise surfaced. — **Landed at S-0097 close (see [ENGINE_LOG.md](../ENGINE_LOG.md) `[Unreleased]`).**
4. The build_readiness/README.md table row for this report flips to `Closed`. — **Landed at S-0097 close.**

**Status: CLOSED at S-0097.**

If the first exercise reveals ADR-warranting structure, the findings flow into an amendment to ADR 0057 (refinement) or a successor ADR (posture change). The S-0097 audit surfaced no ADR-warranting structural changes — the contract held. Two refinement-class observations (Non-obvious findings A and B in the audit report) route through User adjudication; both are documentation-class or category-re-class scope, not contract-amending. Consequence: ADR 0057 stands as authored.

## See also

- [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) — the citable contract this exercise tests.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the first-exercise gate framework.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — gate-side structural sibling.
- [`../operations/health-check.md`](../operations/health-check.md) — operational surface; freshness-probe inventory; pushback/lesson drawer-query procedure.
- [`../../docs/health-checks/TEMPLATE.md`](../../docs/health-checks/TEMPLATE.md) — canonical report shape.
- [`../operations/mechanism-first-exercise-gate.md`](../operations/mechanism-first-exercise-gate.md) — first-exercise procedure.
- [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md) and [`mempalace_mechanical_adoption_first_exercise.md`](mempalace_mechanical_adoption_first_exercise.md) — sibling first-exercise notes (file class 5 in [`README.md`](README.md)).
