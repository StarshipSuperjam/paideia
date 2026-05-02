# tension_log enum vocabularies — v1

> Constrained vocabularies for the JSONB fields on `tension_log.exchange_summary` per [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md) sub-decision (1) and [`product/docs/self-correction.md`](../../docs/self-correction.md). Authored at S-0027 build-readiness gate per [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md) T1-C; Phase 3 schema migration consumes these as `CHECK (... IN (...))` constraints.

## Versioning

This file is v1. Vocabulary changes are tracked in `engine/ENGINE_LOG.md` per [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s amendment posture (refinements within the structural-not-substantive principle are ENGINE_LOG-tracked; structural shape changes — adding fields, removing fields, switching from enum to free-text — require superseding ADR).

Phase 6 batch review may surface patterns that justify additional values; refining the enum is a Phase 6 deliverable, not an in-flight Phase 7 teaching-layer decision.

## `teaching_moves_tried` (enum array)

Moves Sonnet attempted during the exchange that produced this tension record. Multiple values record sequence-agnostic; the tension log captures coarse signal, not move-by-move telemetry.

| Value | Meaning |
|---|---|
| `direct_explanation` | Stated the concept in declarative form. |
| `concrete_example` | Gave a specific instance illustrating the concept. |
| `analogy` | Drew a structural parallel to a familiar concept. |
| `decomposition` | Broke the concept into smaller parts and addressed each. |
| `prerequisite_check` | Tested whether the learner holds a stated prerequisite. |
| `restatement` | Rephrased the concept in a different register. |
| `socratic_question` | Asked a leading question intended to elicit insight. |
| `contrast_pair` | Showed the concept against a deliberate non-example. |
| `redirect_to_source` | Pointed the learner at a specific passage in a source text. |
| `pause_and_reframe` | Paused, shifted angle of approach, and re-engaged. |

## `friction_type` (enum, more granular than `tension_type`)

The specific friction Sonnet detected during the exchange. The coarser `tension_type` column on `tension_log` records which of the five feedback loops the record feeds; `friction_type` records the immediate diagnostic Sonnet logged at exchange close.

| Value | Meaning |
|---|---|
| `prerequisite_gap` | Learner appears to lack a prerequisite the graph names. |
| `formula_vs_grounding` | Learner applies procedurally but lacks conceptual grounding, or holds grounding but cannot apply. |
| `source_register_mismatch` | The source's register or level does not meet the learner where they are. |
| `terminology_drift` | The learner uses a key term in a way that differs from the source or system definition. |
| `aliasing_confusion` | The learner conflates two distinct concepts that share a label. |
| `cross_domain_transfer_block` | A concept does not transfer across domains as the graph predicts it should. |
| `cognitive_overload` | Too many concepts engaged at once for the learner's current capacity. |
| `motivation_gap` | The learner does not see why the concept matters in their current path. |
| `false_mastery` | The learner believed they held the concept but the exchange revealed they did not. |
| `unexpected_ease` | The learner moved through faster than the graph's prerequisite weight predicted. |

## `suggested_review_focus` (enum or NULL)

Sonnet's suggested direction for the Opus batch review. Sonnet does not propose graph edits; it suggests where the review should look. NULL is acceptable when Sonnet has no preference.

| Value | Meaning |
|---|---|
| `prerequisite_node` | Review the prerequisite chain for the current concept. |
| `current_node` | Review the current node's structure (split, merge, or restate). |
| `parent_concept` | Zoom out to the parent or wider context. |
| `cross_domain_link` | Examine the cross-domain edge that surfaced. |
| `source_alternative` | Consider alternative source texts for this concept. |
| `synthetic_node_review` | This is a SYNTHETIC node per [ADR 0030](../../adr/0030-confidence-level-evidentiary-mode-on-nodes.md); review whether it should split, merge, deprecate, or repromote. |
| `skip_for_now` | This is not the right moment for the learner; the system can return later. |
| (NULL) | No specific focus suggested. |

## SQL constraint shape

Phase 3 schema migration enforces these vocabularies via JSONB shape checks. The exact SQL pattern is settled in [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md) T2-A; the pattern below is the v1 expectation:

```sql
-- exchange_summary JSONB validation: required fields present and within
-- declared vocabularies. The column-level CHECK runs on every INSERT/UPDATE.
ALTER TABLE public.tension_log ADD CONSTRAINT exchange_summary_shape_v1 CHECK (
  -- teaching_moves_tried is an array of values from the v1 enum
  (
    SELECT bool_and(
      v IN (
        'direct_explanation', 'concrete_example', 'analogy', 'decomposition',
        'prerequisite_check', 'restatement', 'socratic_question',
        'contrast_pair', 'redirect_to_source', 'pause_and_reframe'
      )
    )
    FROM jsonb_array_elements_text(exchange_summary->'teaching_moves_tried') v
  )
  -- friction_type is in the v1 enum
  AND exchange_summary->>'friction_type' IN (
    'prerequisite_gap', 'formula_vs_grounding', 'source_register_mismatch',
    'terminology_drift', 'aliasing_confusion', 'cross_domain_transfer_block',
    'cognitive_overload', 'motivation_gap', 'false_mastery', 'unexpected_ease'
  )
  -- suggested_review_focus is in the v1 enum or null
  AND (
    exchange_summary->>'suggested_review_focus' IS NULL
    OR exchange_summary->>'suggested_review_focus' IN (
      'prerequisite_node', 'current_node', 'parent_concept',
      'cross_domain_link', 'source_alternative', 'synthetic_node_review',
      'skip_for_now'
    )
  )
);
```

The actual migration may break the constraint into per-field CHECKs, or use a trigger, or use a JSON Schema validation extension. The shape above is the contract; the implementation is Phase 3's discretion within the [`migration-discipline.md`](../../../engine/operations/migration-discipline.md) Layer 1 contract.

## `pattern_observed` writing policy

Per [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md) sub-decision (1), `pattern_observed` is bounded-length structural description (target ~280 chars, hard cap ~600). It is third-person; descriptive, not quotational; and forbidden from carrying first-person learner claims, contested doctrinal positions, or political/religious framings as substantive content.

The Phase 4 [`engine/tools/validate.py`](../../../engine/tools/validate.py) extension that adds a `pattern_observed_substantive_content` soft-warn category (per ADR 0026 Consequences) is the mechanical detection layer. Sonnet's authoring discipline is the primary enforcement; the soft-warn is the secondary catch.

This policy is structural — Sonnet does not narrate learner identity, opinion, or worldview; the column captures the structural shape of the observed friction without polluting persistent storage with substantive learner content.

## Phase 6 refinement protocol

The Opus batch review is positioned to refine these vocabularies as patterns surface across many tension records. The refinement protocol:

1. Opus surveys the previous review window's tension records.
2. If a `friction_type` enum value covers a frequent pattern poorly (e.g., the friction is consistently more specific than `cognitive_overload`), Opus proposes a new value with examples.
3. The proposal lands as an ENGINE_LOG entry under [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s amendment discipline. The Phase 3 migration's CHECK constraint is updated in a follow-up migration that adds the new value to the IN list.
4. Existing tension records under the old vocabulary are not retroactively re-classified; the v1 vocabulary remains in the audit trail.

## See also

- [ADR 0026](../../adr/0026-persistent-learner-storage-structural-not-substantive.md) — structural-not-substantive learner storage; the citable contract for `exchange_summary`'s shape.
- [ADR 0030](../../adr/0030-confidence-level-evidentiary-mode-on-nodes.md) — `confidence_level` enum; the `synthetic_node_review` value in `suggested_review_focus` references SYNTHETIC nodes from this ADR.
- [`product/docs/self-correction.md`](../../docs/self-correction.md) — the source-of-truth for tension log shape and the five feedback loops.
- [`engine/build_readiness/phase_3_sql.md`](../../../engine/build_readiness/phase_3_sql.md) — the gate report that consumes this vocabulary as T1-C resolution.
- [`engine/operations/migration-discipline.md`](../../../engine/operations/migration-discipline.md) — Layer 1 source-of-truth for the SQL/migrations pattern; the Phase 3 schema migration that consumes this vocabulary follows this contract.
