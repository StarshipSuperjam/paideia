# P_7 — Sonnet teaching layer (first prototype) (Phase 7)

> Callable teaching endpoint that produces learner-facing prose against the rendering policy from `product/AGENT_INSTRUCTIONS.md`. The first product-facing surface; the validation point for the rendering-policy contract.

## Phase scope

Phase 7 ships the first callable teaching endpoint. Sonnet's system prompt is `product/AGENT_INSTRUCTIONS.md` verbatim per [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md). Input shape per the Phase DEC.1 ADRs ([`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md)): current concept node + one-hop prerequisite nodes + two-hop neighborhood for entity resolution. Output: teaching turn in product voice, no scaffolding tokens.

Per [ROADMAP Phase 7](../ROADMAP.md), the DeepTutor fork (Apache 2.0, per [`product/docs/infrastructure.md`](../product/docs/infrastructure.md)) is the infrastructure base. The pedagogical layer is the new Sonnet integration.

This is the first chunk that produces learner-facing surface. **Two open tensions must close before sustained operation:**

- **OQ-CONTEXT-COMPRESSION** must settle by ADR before the prototype runs sustained multi-turn engagements. The chosen strategy keeps typical concept-engagement cost inside the cost-ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) projections at a target user count.
- **OQ-OUTWARD-VOICE** must settle by ADR before any learner-facing surface ships. The third expression-contract gap covers UI labels, button text, error messages, learner-facing help, public README, App Store description, learner-visible CHANGELOG entries.

## Output

- **Sonnet teaching endpoint** — callable, accepting `concept_id` + `learner_id` (or session token), returning a teaching turn. The system prompt is `product/AGENT_INSTRUCTIONS.md` verbatim.
- **Retrieval shape** per OQ-DEC1-B: current concept + one-hop prereqs + two-hop neighborhood. The query implementation lives in the teaching endpoint's data-fetch layer.
- **DeepTutor fork integration** — DeepTutor (Apache 2.0) provides infrastructure (session management, conversation log handling); the Sonnet integration is the new layer. Where the fork lives in the tree is settled in-session — likely `engine/integrations/deeptutor-fork/` or as a Git submodule.
- **Tension emission** wired per [`P_6_self_correction.md`](P_6_self_correction.md)'s emission contract. Live teaching sessions write to `tension_log`.
- **Cost telemetry** per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) — every API call records its token usage and projected cost; the data feeds the cost-cap mechanism for [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md).
- **Two ADRs** settling OQ-CONTEXT-COMPRESSION and OQ-OUTWARD-VOICE; both required before sustained operation.

## Success criteria

- The Sonnet teaching prototype, given the `product/AGENT_INSTRUCTIONS.md` worked-example input, produces the pass-case voice.
- **Spot-check:** 10 random concept queries, manually graded for forbidden-token leakage. **Zero leakage is the bar.**
- **OQ-CONTEXT-COMPRESSION** settled with an ADR before the prototype runs sustained multi-turn engagements. Chosen strategy keeps typical concept-engagement cost inside the cost-ceiling per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md) projections at a target user count.
- **OQ-OUTWARD-VOICE** settled with an ADR before any learner-facing surface ships. The contract document operationalizes the new third expression-contract per the kindred-tool pattern in [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md).
- ENGINE_LOG entry under `[Unreleased]` for `Added` (teaching endpoint, DeepTutor fork integration, two new ADRs).
- Cost telemetry records correctly per [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md).

### 7.1 Paperclip commit

If the Phase 5 trial proved Paperclip's fit (per [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md)'s Paperclip trial), this is the moment to commit: Paperclip orchestrates teaching evaluation runs, enforces budget on API spend, dispatches comparative-evaluation tickets in [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md). The commit decision is made in-session; if the Phase 5 trial was inconclusive, the commit defers and Phase 7 runs without Paperclip.

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 7.
- [`product/AGENT_INSTRUCTIONS.md`](../product/AGENT_INSTRUCTIONS.md) — the teaching prompt, verbatim.
- [`product/adr/0027-rendering-policy-prompt-layer-contract.md`](../product/adr/0027-rendering-policy-prompt-layer-contract.md) — the contract `AGENT_INSTRUCTIONS.md` operationalizes.
- [`product/adr/0028-input-side-scope-structural-not-prompt.md`](../product/adr/0028-input-side-scope-structural-not-prompt.md) — input-side scope discipline.
- [`product/adr/0029-personal-financial-cost-ceiling.md`](../product/adr/0029-personal-financial-cost-ceiling.md) — cost-ceiling constraint.
- [`product/docs/infrastructure.md`](../product/docs/infrastructure.md) — DeepTutor fork base.
- The four Phase DEC.1 ADRs from [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — retrieval shape, embedding choice, etc.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-CONTEXT-COMPRESSION` and `OQ-OUTWARD-VOICE` entries.
- [`product/docs/pedagogy.md`](../product/docs/pedagogy.md) — three teaching modes context.
- [`product/docs/session-lifecycle.md`](../product/docs/session-lifecycle.md) — concept engagement as atomic unit.

## Load-bearing ADRs

[ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0028](../adr/0028-input-side-scope-structural-not-prompt.md), [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md), [ADR 0033](../adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](../adr/0034-discovery-planning-engagement-triad.md), [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) (the kindred-tool pattern for OQ-OUTWARD-VOICE).

## Estimated context budget

Substantive tier: target 60%, cap 70%. The prototype implementation is the smaller half; the larger budget pressure comes from the two ADRs (OQ-CONTEXT-COMPRESSION and OQ-OUTWARD-VOICE) which are decision-dense work that a coding session typically should not bundle. Expect the work to span multiple sessions.

## Session sequencing

Multi-session expected. Natural split:

- **Session A:** OQ-CONTEXT-COMPRESSION ADR (prerequisite — sustained operation depends on it).
- **Session B:** OQ-OUTWARD-VOICE ADR + the third-expression-contract operational document (mirrors the [`engine/operations/document-voice.md`](../engine/operations/document-voice.md) shape for [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md)).
- **Session C:** Sonnet teaching endpoint skeleton + DeepTutor fork integration.
- **Session D:** Endpoint hardening, cost telemetry, tension emission, spot-check.

The two ADR sessions (A and B) are independent and can run in either order. Sessions C and D depend on the ADRs.

## Open tensions consumed

- `OQ-CONTEXT-COMPRESSION` — closed by ADR.
- `OQ-OUTWARD-VOICE` — closed by ADR.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 7 — full phase scope.
- [`../AGENT_INSTRUCTIONS.md`](../product/AGENT_INSTRUCTIONS.md) — the teaching prompt.
- [`../adr/0027-rendering-policy-prompt-layer-contract.md`](../adr/0027-rendering-policy-prompt-layer-contract.md) — the contract.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-CONTEXT-COMPRESSION` and `OQ-OUTWARD-VOICE`.
- [`P_8_evaluation_harness.md`](P_8_evaluation_harness.md) — successor; verifies the prototype against stock Sonnet.
