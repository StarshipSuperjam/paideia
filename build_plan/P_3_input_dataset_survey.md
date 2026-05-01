# P_3 — Input dataset survey (Phase 4.5)

> Tiered survey of external datasets useful as **cross-reference inventories and prerequisite-shape priors** for Phase 5 seed authoring. Lands as a new section in [`product/docs/content-strategy.md`](../product/docs/content-strategy.md).

## Phase scope

Phase 4.5 sits between the engine work of Phase 4 and the product-content work of Phase 5. The deliverable is **research and recording**, not commitment: per [ROADMAP Phase 4.5](../ROADMAP.md), specific dataset adoption decisions are deferred to the Phase 5 sessions that consume them. The survey gives the Phase 5 generation pass better starting inventories per domain and surfaces any prerequisite-shaped graph priors worth consulting.

The survey **does not** revise the Generative Graph Independence position in [`product/docs/business.md`](../product/docs/business.md) or the SEP-as-structural-reference posture in [`product/docs/content-strategy.md`](../product/docs/content-strategy.md). Concept nodes and prerequisite edges remain generatively seeded; the survey supplies the priors.

## Output

A new section in [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) titled **"Cross-Domain Reference Inventories — Survey"**. The section structure (already scaffolded at S-0009 per [`product/docs/content-strategy.md`](../product/docs/content-strategy.md)) carries:

- The **five usability axes** (graph-shape orientation, license, form, coverage breadth, depth uniformity / methodology transparency).
- The **four tiers** of survey scope (prerequisite-shaped exhaustive; per-domain cross-reference inventories comprehensive; bibliographies and citation graphs representative; long-form prose minimal).
- **Per-tier candidate assessments** filling the per-candidate-template scaffolded at S-0009.
- The **Önduygu philo-browser worked example** as the survey's calibration reference (already present per the S-0009 scaffolding).

## Success criteria

- The "Cross-Domain Reference Inventories — Survey" section in [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) is populated per the five axes and four tiers per [ROADMAP §4.5](../ROADMAP.md).
- **Tier 1 (prerequisite-shaped)** is exhaustive: every known candidate is named, license-checked, graph-shape-evaluated, and either tagged for Phase 5 consultation or explicitly excluded with reason. Known candidates: Khan Academy knowledge map, ConceptNet's `Prerequisite` relation (CC BY-SA), university CS curriculum prerequisite graphs, Mathlib / Metamath dependency graphs.
- **Tier 2** has at least one named candidate per non-philosophy domain in [`product/docs/expansion.md`](../product/docs/expansion.md).
- The survey output cross-links to Phase 5.2 (the seed-authoring source approach) so Phase 5 sessions consult it.
- No survey finding requires revising **Generative Graph Independence** or the SEP-structural-reference posture; if one does, it lands as an ADR in this phase.
- ENGINE_LOG entry under `[Unreleased]` for `Added` (the populated survey section).

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 4.5.
- [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) — current Cross-Domain Reference Inventories — Survey section scaffold + the SEP-structural-reference posture.
- [`product/docs/expansion.md`](../product/docs/expansion.md) — the non-philosophy domains list (Tier 2 coverage requirement).
- [`product/docs/business.md`](../product/docs/business.md) — Generative Graph Independence position (the survey must not revise this; verify alignment).
- [`product/adr/0001-pedagogical-edges-not-historical.md`](../product/adr/0001-pedagogical-edges-not-historical.md) — the prerequisite-shape filter (axis 1).
- [`product/adr/0007-cross-domain-porosity.md`](../product/adr/0007-cross-domain-porosity.md) — the cross-domain coverage criterion (axis 4).
- [`product/adr/0011-no-hosted-copyrighted-material.md`](../product/adr/0011-no-hosted-copyrighted-material.md) — license axis context.

## Load-bearing ADRs

[ADR 0001](../adr/0001-pedagogical-edges-not-historical.md), [ADR 0007](../adr/0007-cross-domain-porosity.md), [ADR 0011](../adr/0011-no-hosted-copyrighted-material.md).

## Estimated context budget

Substantive tier: target 60%, cap 70%. The work is research synthesis — name candidates per tier, evaluate against axes, record per-candidate assessments. Each candidate's web-fetch + license-check + graph-shape evaluation is a small unit of work; the budget pressure comes from the cumulative count rather than any single candidate.

## Session sequencing

Single session preferred. Multi-session fallback split: Session 1 lands Tier 1 (exhaustive, smaller candidate count, novel value); Session 2 lands Tiers 2–4 (broader candidate count, less novel per-candidate). The Tier 1 / Tier 2 boundary is the natural budget halt.

## Phase 4.5 scope discipline

The survey is **research and recording**, not commitment. Specific dataset adoption decisions (e.g., "use ConceptNet's Prerequisite relation as Tier-1 input for the math service-node subdomain") are deferred to the Phase 5 sessions that consume them; if such a decision involves a non-trivial tradeoff, it lands as an ADR at that point. The Phase 4.5 deliverable is the inventory, not the bindings.

## Open tensions consumed

None directly.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 4.5 — full phase scope.
- [`product/docs/content-strategy.md`](../product/docs/content-strategy.md) — the host document.
- [`product/docs/expansion.md`](../product/docs/expansion.md) — Tier 2 domain list.
- [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md) — the consumer of this survey.
