# Pedagogical Inference Registry

> Enumerated inventory of the inferences the system makes about teaching: what triggers each, what it produces, and where it lives. Created at S-0008 per [`docs/tensions.md`](../tensions.md) **OQ-PEDAGOGY-INFERENCE-LOCUS** as the cheap intermediate step before deciding whether to build a dedicated rule layer.
>
> **Status:** seed inventory derived from existing design docs. Entries are *expressions of intent*, not *implementation pointers* (most pre-Phase 7 — most have no production code yet). Update discipline: add a row when a new inference is committed (in an ADR, design doc, or schema); update the *Lives in* column when the inference moves from design to implementation; revisit the rule-layer question per OQ-PEDAGOGY-INFERENCE-LOCUS when the registry crosses ~30 entries.

## Format

Each entry has five fields:

- **Trigger** — the input condition that fires the inference
- **Action** — what the inference produces
- **Lives in (design)** — the design document or ADR where the inference is specified
- **Lives in (code)** — the production code surface that *will* implement the inference (target — most are pending pre-Phase 7)
- **Notes** — interactions with other inferences, open variants, audit risks

## Mode-classification inferences

### 1. Three-mode classification per teaching turn

- **Trigger:** Textual signals in the learner's most recent response (request for clarification, paraphrase quality, claim/connection/interpretation).
- **Action:** Select Mode 1 (direct explanation), Mode 2 (Socratic leading), or Mode 3 (testing interpretation) for the agent's response.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Expression Contract; [`docs/session-lifecycle.md`](../session-lifecycle.md) Mode Transitions; [`AGENT_INSTRUCTIONS.md`](../../AGENT_INSTRUCTIONS.md) (the prompt that operationalizes it at runtime).
- **Lives in (code):** Sonnet system prompt (Phase 7); no separate classifier.
- **Notes:** The classification is unannounced (per [`docs/pedagogy.md`](../pedagogy.md) and [ADR 0027](../../adr/0027-rendering-policy-prompt-layer-contract.md) "Never name the modes to the learner"). Failure mode: agent over-applies Mode 1 to advanced learners. Calibration discipline: Mode-2/3 transitions ramp on engagement signal per [ADR 0012](../../adr/0012-freshman-defaults-autodidact-ceiling.md).

### 2. Calibrating to prior exposure

- **Trigger:** Learner model marks a concept as `exposed` (prior reading history, library, or self-report) but not `proficiency`.
- **Action:** Adjust agent entry point — probe what was retained rather than re-explain from scratch; lean Mode 2/3 over Mode 1.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Calibrating to Prior Exposure; [`docs/learner-model.md`](../learner-model.md) Persistent Learner Model.
- **Lives in (code):** Sonnet teaching layer (Phase 7) — the per-turn context includes prerequisite mastery states; the agent reads them and adjusts.
- **Notes:** Self-report sets `exposed`, never `proficiency` (the verification gate is interaction, not assertion). Failure mode: agent skips the concept entirely on `exposed` evidence — forbidden.

### 3. Cold-start initial calibration

- **Trigger:** Learner model is empty on first use; learner selects a target topic.
- **Action:** Run a brief diagnostic conversation probing prerequisites; set initial mastery states (substantive answer → `proficiency`; familiarity without depth → `exposed`; no recognition → leave `not encountered`).
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Cold Start / Initial Calibration; [`docs/learner-model.md`](../learner-model.md) Persistent Learner Model § Initial population.
- **Lives in (code):** Diagnostic-conversation flow (Phase 7+); writes to `learner_events` with `interaction_type = direct_teaching` for substantive answers.
- **Notes:** Diagnostic is a probe, not a quiz — bounded by [ADR 0028](../../adr/0028-input-side-scope-structural-not-prompt.md)'s diagnostic-conversation context.

## Mastery-state inferences

### 4. Backward inference from demonstrated mastery

- **Trigger:** A concept C is verified at `mastery` and has prerequisite edges to ancestor concepts P1, P2, …
- **Action:** Generate synthetic `backward_inference` events on each immediate prerequisite, modulated by prerequisite rigor score (low rigor → high-strength inference; high rigor → low-strength).
- **Lives in (design):** [`docs/learner-model.md`](../learner-model.md) Interaction Types § `backward_inference`; [`docs/architecture.md`](../architecture.md) Backward Inference; [ADR 0023](../../adr/0023-engagement-depth-aggregation.md) (fixed `engagement_depth = 0.5`); [ADR 0009](../../adr/0009-portable-mastery.md).
- **Lives in (code):** Mastery computation layer (Phase 6+); event generator that runs on mastery-verification events.
- **Notes:** Propagates through immediate prerequisites only, not transitive closure. Defeasible — direct contradictory evidence later naturally outweighs via aggregation. No forward inference ever (per [`docs/learner-model.md`](../learner-model.md)).

### 5. Mastery-state derivation from event aggregate

- **Trigger:** Mastery query for `(user_id, concept_id)`.
- **Action:** Aggregate the user's events on that concept; apply `compute_engagement_depth` per [ADR 0023](../../adr/0023-engagement-depth-aggregation.md); apply temporal decay; apply `MAX_FLOOR` floor with `max_historical_score >= 0.3` precondition (per [ADR 0025](../../adr/0025-historical-maximum-tracking.md)); map continuous score to `not_encountered` / `exposed` / `proficiency` / `mastery`.
- **Lives in (design):** [`docs/learner-model.md`](../learner-model.md) Mastery Computation; [ADR 0015](../../adr/0015-event-sourced-learner-model.md); [ADR 0023](../../adr/0023-engagement-depth-aggregation.md); [ADR 0025](../../adr/0025-historical-maximum-tracking.md).
- **Lives in (code):** Server-side mastery computation per OQ-DEC1-A (Phase 6); cached on `mastery_snapshots` per [ADR 0015](../../adr/0015-event-sourced-learner-model.md).
- **Notes:** Server-side per OQ-DEC1-A's leaning. Snapshot regen on event ingest; no client-side computation.

### 6. Engagement-depth aggregation

- **Trigger:** Per learner event, the three sub-signals (`generative_ratio`, `scaffolding_distance`, `novelty`) are recorded.
- **Action:** Composite `engagement_depth = max(0.05, sd^0.5 · gr^0.3 · n^0.2)` for composite-applicable interaction types; fixed values for `backward_inference` (0.5) and `incidental_mention` (0.3).
- **Lives in (design):** [`docs/learner-model.md`](../learner-model.md) Engagement Depth; [ADR 0023](../../adr/0023-engagement-depth-aggregation.md); [ADR 0024](../../adr/0024-engagement-depth-sub-signals-stored-raw.md).
- **Lives in (code):** Application-layer composite computation at query time (Phase 6); sub-signals stored raw on `learner_events`.
- **Notes:** Weights and floor are V1 defaults, application-layer constants tunable without migration per [ADR 0024](../../adr/0024-engagement-depth-sub-signals-stored-raw.md).

### 7. Mastery decay over time

- **Trigger:** Mastery computation reads events with timestamps; `BASE_HALF_LIFE = 60 days` modulated by per-event `engagement_depth`.
- **Action:** Each event contributes a decaying weight to the aggregate; floor of 0.6 when `max_historical_score >= 0.3` per [ADR 0025](../../adr/0025-historical-maximum-tracking.md).
- **Lives in (design):** [`docs/learner-model.md`](../learner-model.md) Mastery Decay; verified at S-0005 against five trajectory scenarios.
- **Lives in (code):** Mastery computation layer (Phase 6).
- **Notes:** Shallow events both count less and decay faster (double leverage of `engagement_depth`).

## Mastery-verification inferences

### 8. Mastery verification as organic escalation

- **Trigger:** Learner has reached `proficiency` on concept A; subsequent downstream concepts B, C, D reference A; sufficient distance accumulates and sufficient prior evidence has been gathered.
- **Action:** Agent stops scaffolding when bringing A back into a downstream conversation; asks the learner to do the work; the moment is a mastery verification with `scaffolding_distance` locked at 1.0.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Mastery Verification; [ADR 0013](../../adr/0013-mastery-verification-organic-escalation.md); [ADR 0010](../../adr/0010-continuous-contextual-assessment.md).
- **Lives in (code):** Sonnet teaching layer (Phase 7); the verification trigger is itself a small inference about distance + accumulated callback evidence.
- **Notes:** Never named to the learner. Per [ADR 0027](../../adr/0027-rendering-policy-prompt-layer-contract.md), tonal shift does the work; no labeling.

### 9. Rigor-score modulation of assessment depth

- **Trigger:** Assessment of any kind on a concept with rigor score R.
- **Action:** Low R (~0.0–0.3): reconstruction + basic application suffices. Mid R (~0.3–0.6): + lightweight boundary probe. High R (~0.6–1.0): all three dimensions, substantive boundary probe.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Rigor Score; [ADR 0010](../../adr/0010-continuous-contextual-assessment.md); [ADR 0019](../../adr/0019-two-column-rigor-score-override.md).
- **Lives in (code):** Sonnet teaching layer (Phase 7); rigor score is in the per-turn context.
- **Notes:** Three dimensions always *evaluated*; rigor scales which must be *satisfied* for proficiency.

### 10. Learner-relative assessment

- **Trigger:** Evaluating the learner's response to a probe.
- **Action:** Score against what someone who has mastered the learner's current prerequisites — and nothing else — should produce. Do not benchmark against the AI's full field knowledge.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) Learner-Relative Assessment.
- **Lives in (code):** Sonnet teaching layer (Phase 7); enforced by prompt instruction.
- **Notes:** Failure mode: agent expects sophisticated objections the learner cannot have. Audit risk: this is hard to grade automatically; relies on Sonnet's calibration.

## Path and traversal inferences

### 11. Path generation from target topic

- **Trigger:** User selects a target concept node.
- **Action:** Topologically sort prerequisites (recursive CTE per [ADR 0017](../../adr/0017-postgres-recursive-ctes-over-owl-rdf.md)); generate reading syllabus (primary + supplementary per step).
- **Lives in (design):** [`docs/architecture.md`](../architecture.md); [`docs/MISSION.md`](../MISSION.md).
- **Lives in (code):** Server-side path generator (Phase 6+).
- **Notes:** "Reading syllabus" is the user-facing path; the underlying traversal is the inference. Inactive prerequisites (already at proficiency) skipped.

### 12. AI-initiated awareness introduction

- **Trigger:** Prerequisite concept is about to become relevant on the learning path; or mastery of current concept activates a cross-domain bridge.
- **Action:** Agent surfaces the concept proactively, gives a vivid framing, ends with an open question. Sets concept to `exposed` in learner model.
- **Lives in (design):** [`docs/pedagogy.md`](../pedagogy.md) AI-Initiated Awareness Introduction.
- **Lives in (code):** Sonnet teaching layer (Phase 7); requires a "what's next?" inference at end of each concept engagement.
- **Notes:** Threshold act before teaching begins. Distinct from cold-start diagnostic.

## Tension-emission inferences (the five feedback loops per ADR 0014)

### 13. Tension classification — `struggle_unresolved`

- **Trigger:** Multiple teaching moves attempted, learner difficulty unresolved.
- **Action:** Write `tension_log` row with `tension_type = struggle_unresolved` and `pattern_observed` per [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md) emission policy.
- **Lives in (design):** [`docs/self-correction.md`](../self-correction.md) Tension Log Schema; [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md); [`AGENT_INSTRUCTIONS.md`](../../AGENT_INSTRUCTIONS.md) Tension emission section.
- **Lives in (code):** Sonnet teaching layer (Phase 7); writes to `tension_log` table.
- **Notes:** Sonnet classifies at coarse type only; fine diagnosis is Opus's job per [ADR 0014](../../adr/0014-sonnet-teaches-opus-reviews.md).

### 14. Tension classification — `unexpected_ease`

- **Trigger:** Learner moves through concept faster than the rigor score and prerequisite mastery profile predicted.
- **Action:** Write `tension_log` row with `tension_type = unexpected_ease`.
- **Lives in (design):** Same as above.
- **Lives in (code):** Same as above.
- **Notes:** Feeds path-efficiency feedback loop (over-strong prerequisite edges).

### 15. Tension classification — `spontaneous_connection`

- **Trigger:** Learner references a concept the AI didn't introduce; entity-resolution against two-hop neighborhood succeeds *or* fails.
- **Action:** If resolved → log `cross_domain_connection` event in `learner_events`; populate `learner_reference_node_id` on tension row. If unresolved → write `tension_log` row with `tension_type = spontaneous_connection`, `unresolved_reference` populated in `exchange_summary`.
- **Lives in (design):** [`docs/self-correction.md`](../self-correction.md); [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md).
- **Lives in (code):** Sonnet teaching layer + entity-resolution service (Phase 7).
- **Notes:** Two-hop boundary is practical, not theoretical (per [`docs/self-correction.md`](../self-correction.md)).

### 16. Tension classification — `source_ineffective`

- **Trigger:** Source A recommended for a concept; learner did not grasp from it; alternate source worked (or learner flagged it explicitly).
- **Action:** Write `tension_log` row with `tension_type = source_ineffective`.
- **Lives in (design):** [`docs/self-correction.md`](../self-correction.md).
- **Lives in (code):** Sonnet teaching layer (Phase 7).
- **Notes:** Per-learner source-quality signal; aggregates over time.

### 17. Tension classification — `mastery_contradiction`

- **Trigger:** Concept previously verified at `proficiency` (or `mastery`); learner cannot reapply in new context.
- **Action:** Write `tension_log` row with `tension_type = mastery_contradiction`. Mastery state may be downgraded.
- **Lives in (design):** [`docs/self-correction.md`](../self-correction.md).
- **Lives in (code):** Sonnet teaching layer (Phase 7); state downgrade logic in mastery computation.
- **Notes:** Feeds mastery-contradiction feedback loop; over time the system raises threshold for marking similar concepts complete.

## Concept-engagement-lifecycle inferences

### 18. Session-resume reorientation

- **Trigger:** Learner returns to a concept engagement after a gap; gap exceeds ~1 day.
- **Action:** Brief minimal reorientation — restate the last point of discussion; do not re-explain the concept.
- **Lives in (design):** [`docs/session-lifecycle.md`](../session-lifecycle.md) Concept Engagement as the Atomic Unit.
- **Lives in (code):** Sonnet teaching layer (Phase 7).
- **Notes:** Failure mode: agent re-greets at every session start (sub-day gaps); forbidden. Cross-session continuity comes from the structured event log per [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md), not transcript replay.

### 19. Decay-floor activation

- **Trigger:** `max_historical_score >= 0.3` for a concept.
- **Action:** Apply `MAX_FLOOR = 0.6` to the decayed mastery aggregate.
- **Lives in (design):** [ADR 0025](../../adr/0025-historical-maximum-tracking.md); [`docs/learner-model.md`](../learner-model.md) Mastery Computation.
- **Lives in (code):** Mastery computation layer (Phase 6+).
- **Notes:** Floor activation is a per-concept boolean derived from snapshot column; client computes locally without per-event recomputation per [ADR 0025](../../adr/0025-historical-maximum-tracking.md).

---

## Open inferences (named but not yet specified)

These are inferences the design implies but has not yet specified at the level of "trigger / action / lives in." They are listed so they cannot be silently dropped; specification is downstream work.

- **Cross-domain edge generation by Opus** — the inference Opus performs during periodic batch review, proposing candidate cross-domain edges from accumulated `cross_domain_connection` events. Specification: Phase 6 (self-correction pipeline). Per [ADR 0014](../../adr/0014-sonnet-teaches-opus-reviews.md).
- **Per-learner source-quality scoring** — aggregating `source_ineffective` tensions and successful-source signals into per-learner per-source quality estimates. Specification: Phase 6. Per [`docs/self-correction.md`](../self-correction.md).
- **Path-efficiency edge-weight adjustment** — aggregating `unexpected_ease` and `struggle_unresolved` evidence into edge-weight proposals. Specification: Phase 6. Per [`docs/self-correction.md`](../self-correction.md).
- **Bridge-surfacing-in-context inference** — mapping mastery state + cross-domain bridges to contextual surfacing in Planning convergence notes and Engagement callback references per [ADR 0034](../../adr/0034-discovery-planning-engagement-triad.md)'s bridge-surfacing-in-context convention. Replaces the prior mastery-glow / globe-rendering visualization framing per [ADR 0033](../../adr/0033-mission-realignment-structured-guidance-for-self-learners.md). Specification: Phase 9. Per [`docs/ui-architecture.md`](../ui-architecture.md).
- **Soft-wall degradation triggering** — the inference that a user is approaching cap and the agent should downshift. Specification: Phase 8 per [ADR 0029](../../adr/0029-personal-financial-cost-ceiling.md) and OQ-WALL-BEHAVIOR.

---

*Created: 2026-04-29 (S-0008) per [`docs/tensions.md`](../tensions.md) OQ-PEDAGOGY-INFERENCE-LOCUS. Maintenance discipline: add a row when a new inference is committed; update the *Lives in (code)* column when a design inference moves into production code; revisit the rule-layer question when the registry crosses ~30 entries or one of the other revisit triggers fires.*
