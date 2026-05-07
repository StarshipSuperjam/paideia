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

**Qualifies; first-exercise gate report needed before unattended use.** This report IS the gate report; the first-exercise session is the next cadence-fired audit (S-0087 by recommended sequencing per [`~/.claude/plans/i-need-a-plan-prancy-ripple.md`](https://github.com/StarshipSuperjam/paideia/issues/30) — campaign session S-E `apply_migration` postcondition verification, with cadence trigger firing concurrently at `slots_since == 10`).

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
| T1-A | The audit AI must read MemPalace `pushback`/`lesson` drawer *content* (not just counts) at audit time | **Pending S-0087.** Closes when the audit produces a non-empty Accumulated-pushbacks-and-lessons subsection that quotes or summarizes drawer content; or, if zero captures, a subsection explicitly distinguishing posture-not-exercised from capture-surface-failure. |
| T1-B | User adjudication subsection must arrive blank — audit cannot pre-fill | **Pending S-0087.** Closes when the audit's hand-authored report's User adjudication subsection is empty (or carries a placeholder like `<populated post-audit by the user>`) and is populated subsequently by the user. |
| T1-C | Freshness probes must produce content findings, not cite cached stats | **Pending S-0087.** Closes when the Freshness-probes-run subsection's MemPalace / validator / Supabase / hooks / registries entries each describe a probe RUN (commands invoked, results observed) rather than referencing a count from a prior STATE.md row or audit report. |
| T1-D | Cold-context probe randomly selects an artifact, not the audit's preferred target | **Pending S-0087.** Closes when the Cold-context-probe subsection names the random-pick procedure (the `find` filter and `shuf -n 1` invocation, or equivalent) used to select the artifact. |
| T1-E | ≥1 retire-candidate or adversarially-scrutinized "no candidates" subsection | **Pending S-0087.** Closes when the Affirmative-retire-candidates subsection carries either ≥1 retire-candidate-with-reasoning OR a "no retire candidates this audit" subsection adversarially scrutinizing its own claim. |

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

1. The S-0087 audit (or any subsequent first-exercise audit if S-0087 is consumed by another priority) lands a hand-authored report at `docs/health-checks/S-NNNN.md` against the new TEMPLATE.md shape.
2. T1-A through T1-E each move to "Resolved at S-NNNN" with the closure observation.
3. ENGINE_LOG carries a `Changed` entry referencing the first-exercise audit and any refinements to `health-check.md` / `TEMPLATE.md` the exercise surfaced.
4. The build_readiness/README.md table row for this report flips to `Closed`.

If the first exercise reveals ADR-warranting structure, the findings flow into an amendment to ADR 0057 (refinement) or a successor ADR (posture change).

## See also

- [ADR 0057](../adr/0057-adversarial-stance-for-health-check-audits.md) — the citable contract this exercise tests.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the first-exercise gate framework.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — gate-side structural sibling.
- [`../operations/health-check.md`](../operations/health-check.md) — operational surface; freshness-probe inventory; pushback/lesson drawer-query procedure.
- [`../../docs/health-checks/TEMPLATE.md`](../../docs/health-checks/TEMPLATE.md) — canonical report shape.
- [`../operations/mechanism-first-exercise-gate.md`](../operations/mechanism-first-exercise-gate.md) — first-exercise procedure.
- [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md) and [`mempalace_mechanical_adoption_first_exercise.md`](mempalace_mechanical_adoption_first_exercise.md) — sibling first-exercise notes (file class 5 in [`README.md`](README.md)).
