# ADR 0023 — Engagement-depth aggregation: weighted geometric mean

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0004 (prompt-pack Session 9 deliberation)

## Context

The `learner_events` log carries a per-event `engagement_depth` value that enters the mastery computation in two places (per `docs/learner-model.md`): it multiplies into `raw_strength` (Stage 1), and it modulates `half_life` in the per-event decay formula. A single event's engagement_depth therefore has double leverage on the entire mastery pipeline — shallow events both count less and decay faster.

Per ADR 0010 (continuous and contextual assessment), engagement depth is a composite of three sub-signals:

- **`generative_ratio`** — what proportion of the substantive content was learner-produced
- **`scaffolding_distance`** — how detached the response is from recent AI scaffolding
- **`novelty`** — whether the learner introduced application/connection the AI did not set up

Pre-S-0004, the aggregation function was deferred. The four canonical candidates — weighted sum, minimum-of-three, geometric mean, hybrids — sort by what they say about how the signals relate.

The relational question: are the three signals **substitutes** (one strong signal compensates for two weak ones) or **complements** (all three need to be reasonably present for the event to count as deep engagement)?

Each signal alone is insufficient evidence:

- High `generative_ratio` alone, with low `scaffolding_distance` (just-scaffolded), is the canonical false-mastery scenario ADR 0010 was written to prevent — chatty paraphrase scoring as deep mastery.
- High `scaffolding_distance` alone — "yeah we talked about that" — is shallow recall, decay-suppression evidence at most.
- High `novelty` alone is wild speculation the AI did not engage with.

The signals are **complements**. This rules out weighted sum (the canonical substitutes form), which would let a 0.95 generative ratio pull a (0.05/0.95/0.10) event up to ~0.32 — a midrange depth score for the textbook false-mastery case.

Minimum-of-three is too strict: it makes novelty a hard prerequisite for any depth, but novel cross-domain application may take months to surface for a given concept. A spontaneous, generative reconstruction weeks after the original teaching should count for *something*, even without a fresh cross-domain leap.

Geometric mean ("soft min") penalizes a low signal heavily without truncating to it. The same (0.05/0.95/0.10) example yields ~0.15 — low enough to register the false-mastery case correctly, high enough to recognize that the learner did produce content. ADR 0010 explicitly names scaffolding proximity as "the single most important calibration," which argues for *weighted* geometric mean. And the pure-zero case (any sub-signal at 0 → composite at 0 → `raw_strength = 0` AND `half_life = 0` → infinite decay rate) destabilizes the formula, so a small floor is required.

## Decision

`engagement_depth` is the **floored weighted geometric mean** of three sub-signals, computed at query time:

```
engagement_depth = max(
  0.05,
  scaffolding_distance^0.5 · generative_ratio^0.3 · novelty^0.2
)
```

All three sub-signals on `[0, 1]` in **direct evidentiary direction** (higher = stronger evidence of depth):

| Sub-signal | 0 means | 1 means |
|---|---|---|
| `generative_ratio` | AI produced all substantive content | Learner produced all substantive content |
| `scaffolding_distance` | Response co-located with AI scaffolding (just-scaffolded) | Fully detached (zero-scaffolding constraint or weeks-later spontaneous reference) |
| `novelty` | Restated in the conversation's terms | Cross-domain leap or independent example |

**Variable rename.** ADR 0010 and predecessor docs used `scaffolding_proximity` ∈ [0, 1] where 0 = far / max evidentiary weight and 1 = co-located / min weight. The relationship between value and evidentiary direction was inverted. This ADR renames the variable to `scaffolding_distance` (numerically `1 − scaffolding_proximity`) so the value direction matches the evidentiary direction and the composite formula needs no sign flips. The pedagogical concept — how recently the AI scaffolded — is unchanged. Living design docs (`docs/pedagogy.md`, `docs/learner-model.md`, `docs/MISSION.md`, `docs/CROSS_REFERENCES.md`, `docs/reading-system.md`) are updated; historical ADRs (0010, 0013) are not retroactively edited.

**Weighting (V1 defaults, tunable):**

| Weight | Sub-signal | Rationale |
|---|---|---|
| 0.5 | `scaffolding_distance` | ADR 0010 names this discount as "the single most important calibration." Also the most reliable sub-signal to estimate — a positional fact, not a judgment. |
| 0.3 | `generative_ratio` | Maps to the rubric's reconstruction dimension. AI can estimate reasonably reliably. |
| 0.2 | `novelty` | Maps to application / boundary-awareness dimensions. Hardest for the AI to estimate reliably; lower weight reflects lower signal quality. |

**Floor at 0.05** prevents zero-collapse when any sub-signal is 0. With `BASE_HALF_LIFE = 60`, an engagement_depth of 0.05 yields ~3 days half-life on a mid-rigor concept — paraphrases register weakly and fade fast, which matches the design intent.

**Edge cases — interaction types where the composite does not apply:**

| Interaction type | engagement_depth | Rationale |
|---|---|---|
| `direct_teaching` | composite | Real learner exchange. |
| `callback_reference` | composite | Real exchange; typically scores moderate. |
| `cross_domain_connection` | composite | Composite naturally scores high (high `novelty` + high `scaffolding_distance` + high `generative_ratio`). |
| `assessment` | composite (with `scaffolding_distance = 1.0` locked) | The zero-scaffolding constraint pins one input. |
| `backward_inference` | **fixed 0.5** | Synthetic; no learner exchange. The interaction-type weight already rigor-attenuates (`0.4 · (1 − rigor_score)`); composite would double-attenuate. 0.5 yields ~30-day half-life at rigor 0.5 — inference fades naturally without dominating. |
| `incidental_mention` | **fixed 0.3** | Concept appeared but learner did not engage. Composite ill-defined (no learner utterance to score). 0.3 yields ~18-day half-life at rigor 0.5 and trivial mastery contribution. If the learner *did* engage, classify as `direct_teaching` or `callback_reference` instead. |

The fixed values (0.5, 0.3) and the weights (0.5/0.3/0.2) and the floor (0.05) are V1 starting points. They are application-layer constants, not stored on events — revisable without data migration (per ADR 0024).

## Consequences

- **Worked examples confirm the formula behaves correctly across the canonical scenarios.** A just-scaffolded paraphrase (`s_dist=0.05, g=0.15, n=0.10`) yields engagement_depth ≈ 0.08; a generative paraphrase / false-mastery test (`s_dist=0.05, g=0.85, n=0.20`) yields ≈ 0.15 (vs ≈ 0.32 from weighted sum); a spontaneous cross-domain connection (`s_dist=0.95, g=0.85, n=0.90`) yields ≈ 0.91; a zero-scaffolding mastery verification with quality response (`s_dist=1.0, g=0.85, n=0.60`) yields ≈ 0.86. The formula cleanly separates strong evidence from thin evidence.

- **Weights are calibration assertions, not derivations.** They reflect (a) ADR 0010's load-bearing status of the scaffolding discount and (b) signal-quality intuitions about how reliably Sonnet can estimate each input. Phase 8 evaluation may revisit them; revision is parameter-only and does not require migration (per ADR 0024).

- **The 0.05 floor is a magic constant.** It must be small enough that paraphrases barely register but not so small that decay rate explodes. Tunable.

- **Signal-quality risk** (Phase 7 calibration). The math here is a fraction of the total uncertainty. Whether Sonnet can produce well-calibrated 0–1 estimates of each sub-signal — particularly `novelty` — is a separate engineering problem the math cannot solve. If sub-signal estimates are noisy (±0.3), the composite is noisy regardless of formula. The aggregation is robust enough that small estimation errors in any one signal do not catastrophically distort the composite, but systematic bias in one sub-signal would. This is a calibration risk to surface in the Phase 7 Sonnet teaching prototype evaluation.

- **Double-leverage of engagement_depth is preserved.** The same scalar multiplies `raw_strength` AND modulates `half_life`. Shallow events both count less and decay faster. But this means the dynamic range of engagement_depth has high leverage on the whole pipeline. Session 10 (Decay Parameter Verification) verifies that `BASE_HALF_LIFE = 60 days` produces correct trajectories given the realistic engagement_depth distribution this aggregation produces (roughly 0.1–0.9 for real teaching exchanges).

- **The decision closes prompt-pack Session 9** (Engagement Depth Aggregation) per `ROADMAP.md` §1.1. Session 10 is unblocked.

## See also

- [`docs/learner-model.md`](../docs/learner-model.md) — Engagement Depth section, Mastery Computation pseudocode (updated S-0004).
- [`docs/pedagogy.md`](../docs/pedagogy.md) — Scaffolding Distance section (renamed from Scaffolding Proximity, S-0004).
- [`docs/prep-paideia-prompt-pack.md`](../docs/prep-paideia-prompt-pack.md) — Session 9 deliberation prompt.
- ADR 0010 — Continuous and contextual assessment (the rubric the composite operationalizes; uses `scaffolding_proximity` language pre-rename).
- ADR 0015 — Event-sourced learner model (the storage discipline that ADR 0024 honors).
- ADR 0024 — Engagement-depth sub-signals stored raw, composite derived (the storage commitment that supports parameter tunability).
