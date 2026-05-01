# P_8 — Evaluation harness + Apple Developer enrollment + cost-cap test + private TestFlight cold-test (Phase 8)

> Verifies the rendering-policy worked example holds against stock Sonnet without the policy, isolating the contribution of the prompt-layer contract. Wires and tests the cost-cap mechanism. Cold-tests with a small private TestFlight cohort. Apple Developer Program enrollment starts here per the 2–4 week lead-time constraint.

## Phase scope

Phase 8 is the verification phase between the Phase 7 prototype and the Phase 9 UI ship. Per [ROADMAP Phase 8](../ROADMAP.md), four coupled deliverables:

1. **Evaluation harness** — stock Sonnet without the rendering policy as the head-to-head baseline; isolate the contribution of `product/AGENT_INSTRUCTIONS.md`.
2. **Apple Developer Program enrollment** — starts at Phase 8 boot per the 2–4 week lead-time per [`product/docs/business.md`](../product/docs/business.md). Don't defer to Phase 9 — the lead time risks blocking the UI prototype.
3. **Cost-cap mechanism wired and tested before evaluation users are admitted.** Per-user spend ceiling, aggregate-system spend ceiling, real-time spend telemetry, and a defined behavior at the cap (per OQ-WALL-BEHAVIOR settled in an ADR before this phase opens). Cost protection is a precondition for non-builder access, not a feature.
4. **Small private TestFlight cohort cold-test** — 2–3 people who haven't seen the project, given the TestFlight build with no instructions; cold-test debrief recorded as the verification artifact for the "an app I would pay for if it weren't mine" success criterion.

The cold-test cohort is *small* and *private* by design — a Phase 9 verification, not an ongoing program. Per [`product/docs/business.md`](../product/docs/business.md), the personal-project disposition does not run a beta cohort.

## Output

- **`engine/tools/eval_harness.py`** — head-to-head evaluation: stock Sonnet vs. Sonnet-with-`AGENT_INSTRUCTIONS.md`. Same input, both outputs, manual grading rubric per `AGENT_INSTRUCTIONS.md`'s worked example.
- **OQ-WALL-BEHAVIOR ADR** — settles the soft-wall degradation ladder at cost cap. Single-tier ladder per the cost-priced subscription model collapsed at S-0012; four candidate steps (model downshift, retrieval shrink, concept-engagement length cap, soft refusal) settled to a final ordering and trigger conditions.
- **Cost-cap mechanism** — implementation across the teaching endpoint and the orchestration layer (Paperclip if committed at [`P_7_teaching_layer.md`](P_7_teaching_layer.md), or direct otherwise). Per-user and aggregate-system tracking. Real-time telemetry surface (likely a `cost_telemetry` table; settled in-session).
- **Apple Developer Program enrollment** — submitted; the artifact in this chunk is the enrollment-in-flight or enrollment-complete state, recorded in `outcome_summary` and ENGINE_LOG.
- **Privacy policy + Apple App Store privacy questionnaire answers** — exist before App Store submission (which lands in [`P_9_ui_prototype.md`](P_9_ui_prototype.md)). Pinned here so submission is not blocked on policy work.
- **TestFlight build** — a build the App Store would receive; distributed to 2–3 cold-test cohort members.
- **Cold-test debrief** — recorded as the verification artifact. Lands as a new section in [`product/docs/business.md`](../product/docs/business.md) or as a sibling document; settled in-session.

## Success criteria

- Stock-Sonnet-without-rendering-policy head-to-head baseline runs against the `AGENT_INSTRUCTIONS.md` worked example; the rendering policy's contribution is isolated and recorded.
- Apple Developer Program enrollment in flight or complete.
- **Privacy policy and Apple App Store privacy questionnaire answers exist and align with the privacy ADR collection** before App Store submission. Pins the privacy-policy authoring window against the Apple lead time so that submission is not blocked. Consumer App Store posture, not institutional — no DPA, no FERPA framing.
- **Cost-cap mechanism wired and tested before evaluation users are admitted.** Per-user spend ceiling, aggregate-system spend ceiling, real-time spend telemetry, defined behavior at cap per OQ-WALL-BEHAVIOR ADR.
- **Small private TestFlight cohort cold-test** runs against the build the App Store would receive; cold-test debrief recorded as the verification artifact for the "an app I would pay for if it weren't mine" success criterion.
- ENGINE_LOG entry under `[Unreleased]` for `Added` (eval harness, cost-cap mechanism, OQ-WALL-BEHAVIOR ADR, privacy-policy artifacts, cold-test debrief).

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 8.
- [`product/AGENT_INSTRUCTIONS.md`](../product/AGENT_INSTRUCTIONS.md) — the worked example the harness consumes.
- [`product/adr/0029-personal-financial-cost-ceiling.md`](../product/adr/0029-personal-financial-cost-ceiling.md) — cost-ceiling commitment.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-WALL-BEHAVIOR` entry.
- [`product/docs/business.md`](../product/docs/business.md) — Apple App Store distribution, cancellation discipline, cost-priced subscription model.
- [`product/adr/0031-erasure-mechanism-and-individual-only-regime.md`](../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) — privacy regime that the privacy policy reflects.
- [`product/adr/0026-persistent-learner-storage-structural-not-substantive.md`](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — privacy questionnaire alignment.
- [`product/adr/0035-multi-platform-apple-expansion.md`](../product/adr/0035-multi-platform-apple-expansion.md) — App Store distribution constraint.

## Load-bearing ADRs

[ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0029](../adr/0029-personal-financial-cost-ceiling.md), [ADR 0031](../adr/0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0032](../adr/0032-personal-project-disposition.md) (Superseded by [ADR 0035](../adr/0035-multi-platform-apple-expansion.md), but its commitment-2 disposition continues to apply), [ADR 0035](../adr/0035-multi-platform-apple-expansion.md).

## Estimated context budget

Mixed tiers across sessions:

- **Mechanical** (target 70%, cap 80%) for the harness implementation and cost-cap wiring.
- **Substantive** (target 60%, cap 70%) for the OQ-WALL-BEHAVIOR ADR, the privacy-policy authoring, and the cold-test debrief.

## Session sequencing

Multi-session. Natural split:

- **Session A:** OQ-WALL-BEHAVIOR ADR (prerequisite — cost-cap behavior depends on it).
- **Session B:** Apple Developer Program enrollment kickoff + privacy policy authoring + privacy questionnaire answers (Apple lead time pins this early).
- **Session C:** `engine/tools/eval_harness.py` + the head-to-head baseline run.
- **Session D:** Cost-cap mechanism implementation + telemetry surface.
- **Session E:** TestFlight build + cohort distribution + cold-test debrief.

Sessions A and B can run in parallel with C and D. Session E depends on D (cost cap must be wired before cohort gets the build).

## Open tensions consumed

- `OQ-WALL-BEHAVIOR` — closed by ADR.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 8 — full phase scope.
- [`product/docs/tensions.md`](../product/docs/tensions.md) — `OQ-WALL-BEHAVIOR`.
- [`product/docs/business.md`](../product/docs/business.md) — Apple App Store distribution, cost-priced subscription, cancellation discipline.
- [`../adr/0029-personal-financial-cost-ceiling.md`](../adr/0029-personal-financial-cost-ceiling.md) — cost-ceiling.
- [`P_7_teaching_layer.md`](P_7_teaching_layer.md) — predecessor; produces the prototype this harness evaluates.
- [`P_9_ui_prototype.md`](P_9_ui_prototype.md) — successor; consumes the cost-cap mechanism, the App Store enrollment, the privacy policy.
