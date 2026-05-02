# Self-Correction

## Self-Correcting Graph via Feedback Loops
**Added: 2026-04-07**

The graph does not require perfect curation at launch. Five feedback mechanisms allow it to self-correct through normal user interaction:

1. **Prerequisite validation through struggle.** When the teaching AI presents a concept and the user struggles, it diagnoses why. If the cause is a missing prerequisite the graph didn't flag, that's a candidate new edge. If the user breezes through something the graph said required several prerequisites, those edges may be too strong.

2. **Mastery contradiction.** The learner model marks a concept as demonstrated. Later, the user encounters it in a new context and can't apply it. The system downgrades from "demonstrated" to "exposed" and flags the concept for reinforcement. Over time, the system learns which concepts tend to produce false mastery signals and raises its threshold for marking them complete.

3. **Path efficiency tracking.** The system records which learning paths users actually take versus which it recommended. Consistent success while skipping a recommended prerequisite weakens that edge. Consistent failure at a node followed by success after backtracking to an unlinked concept suggests a missing edge.

4. **Reading source effectiveness.** When the system recommends a source for a concept and the user still doesn't grasp it, but a different source works — that's data about source quality per concept per learner. Over time, the system learns which sources best teach which ideas for a given user.

5. **Cross-domain bridge discovery.** When a user makes a connection the graph doesn't have ("this reminds me of what we covered in Hume" while reading an economics text), the AI detects this and proposes a new cross-domain edge.

All automated corrections use a **confidence-weighted system**. First-signal corrections start as low-confidence suggestions. When the same correction emerges across multiple interactions, confidence rises and the edge updates permanently. A single bad session cannot corrupt the graph; consistent patterns reshape it. The five loops accumulate evidence continuously through the tension log but graph edits are proposed in periodic batch reviews (see Self-Correction Pipeline below). The graph is stable between review cycles — learners never encounter mid-session structural changes.

## Self-Correction Pipeline
**Added: 2026-04-08**

The self-correction feedback loops operate through a clean division of responsibility between the teaching AI (Sonnet) and the graph curation AI (Opus). Sonnet does not diagnose graph errors or propose edits in real time. It logs **tension records** — structured observations that something in the teaching interaction didn't resolve through normal pedagogical moves. A scheduled Opus review (weekly or biweekly) analyzes accumulated tension records against the full graph state, identifies patterns across sessions and learners, and proposes graph edits that enter the confidence-weighted pipeline.

This architecture prevents reactive single-signal changes, ensures graph stability between review cycles, and gives Opus the benefit of an entire period's worth of evidence to inform structural decisions. A week of tension data reveals trends that individual moments cannot — three learners all struggling at the same transition point is a qualitatively different signal than one learner struggling once.

### Tension Log Schema

**Revised: 2026-04-29 (S-0007 — `exchange_summary` shape constrained per ADR 0026 — persistent learner storage is structural, not substantive).**

```sql
CREATE TABLE tension_log (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  concept_id                TEXT NOT NULL REFERENCES nodes(id),
  session_id                UUID NOT NULL,
  tension_type              TEXT NOT NULL,  -- struggle_unresolved, unexpected_ease, spontaneous_connection, source_ineffective, mastery_contradiction
  exchange_summary          JSONB NOT NULL, -- structured shape per ADR 0026; see field list below
  learner_reference_node_id TEXT REFERENCES nodes(id),  -- populated when the learner references another concept and it resolved
  created_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

The `tension_type` values map to the five feedback loops: `struggle_unresolved` feeds prerequisite validation, `unexpected_ease` feeds path efficiency tracking, `spontaneous_connection` feeds cross-domain bridge discovery, `source_ineffective` feeds reading source effectiveness, and `mastery_contradiction` feeds mastery contradiction detection. Sonnet classifies at this coarse level without attempting deeper diagnosis — that is Opus's job during the batch review.

**`exchange_summary` JSONB shape (per ADR 0026).** The required semantic fields:

- `teaching_moves_tried` — array of enum values from a constrained vocabulary (authored at Phase 3 alongside the migration)
- `friction_type` — enum value, more granular than `tension_type` (e.g. `prerequisite_gap`, `formula_vs_grounding`, `source_register_mismatch`)
- `pattern_observed` — bounded-length structural description (target ~280 chars, hard cap ~600); third-person; descriptive, not quotational; **forbidden** from carrying first-person learner claims, contested doctrinal positions, or political/religious framings as substantive content
- `suggested_review_focus` — enum value or null
- `unresolved_reference` — string or null; populated when `tension_type = spontaneous_connection` and the reference did not resolve to a graph node (when it does resolve, `learner_reference_node_id` is populated instead)

The constrained enum vocabularies and the `pattern_observed` writing policy are authored at Phase 3 alongside the schema migration. Phase 4 `tools/validate.py` adds a periodic-batch soft-warn category that scans `pattern_observed` for substantive-content markers (per ADR 0026 Consequences). The pre-S-0007 schema used `exchange_summary TEXT NOT NULL`; that shape is superseded — see ADR 0026 for the principle and the rationale.

### Teaching Session Context

Sonnet's teaching session carries a bounded context sufficient for both effective teaching and tension logging: the current concept node, its immediate prerequisites and their mastery states for this learner, the learner's recent event history on the current concept, and a **shallow neighborhood of the local graph topology** — node IDs and labels within two hops of the current concept.

The neighborhood serves entity resolution. When a learner spontaneously references a concept — including concepts not in their mastery history that they know from prior independent study — Sonnet resolves the reference against the local topology. References that resolve are engaged with pedagogically in the moment and logged as `cross_domain_connection` events in the learner event stream. References that don't resolve against the local neighborhood are logged as tension records with type `spontaneous_connection` and the unresolved reference recorded in the `exchange_summary.unresolved_reference` field (per ADR 0026), for Opus to evaluate with full graph context.

This context is lightweight — a few dozen node IDs and labels — and does not require Sonnet to carry the full graph or reason about graph structure. The two-hop boundary is a practical limit, not a theoretical one; it can be adjusted if entity resolution miss rates are too high in practice.

### Batch Review Cycle

The Opus review is a scheduled task, not a triggered one. It runs on a fixed cadence (weekly or biweekly) regardless of tension log volume. The review receives: all tension records since the last review, the current graph state, and aggregate learner event data for the concepts involved. Opus proposes graph edits — candidate edges with confidence scores, edge weight adjustments, node split recommendations — which enter the existing confidence-weighted pipeline. Proposed edits do not land immediately; they accumulate confidence through the normal mechanism described above.

At current scale (n=1–3 users), the Opus review may surface patterns slowly. This is acceptable — the graph doesn't need to be perfect, and premature edits based on thin evidence are worse than patience. The batch cadence can be shortened as user count grows and tension log volume increases.

### Synthetic-Node Review Queue
**Added: 2026-04-30 (S-0010 — Phase 1.3 cross-link per [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md))**

Nodes carry a `confidence_level` label (`EXTRACTED | INTERPRETED | SYNTHETIC`) recording the type of evidence backing their existence at authoring time, per the Node Schema in [`docs/architecture.md`](architecture.md) and [ADR 0030](../adr/0030-confidence-level-evidentiary-mode-on-nodes.md). The label is fixed at authoring time (it does not update with belief evidence — that channel is the numeric `confidence` column).

**SYNTHETIC nodes are first candidates for self-correction review.** They have the weakest evidentiary claim — no source structures the concept as a coherent unit; the node was generated to fill a structural gap (e.g., a service node terminating a cross-domain prerequisite chain per the Termination Principle in [`docs/architecture.md`](architecture.md), or a node-split replacement Opus proposed without direct source basis). When the Opus batch review (above) selects review candidates from a window of accumulated tension records and graph state, SYNTHETIC nodes whose surrounding tension density exceeds threshold are surfaced ahead of EXTRACTED and INTERPRETED nodes carrying equivalent tension. The review may propose splitting, merging, deprecating, or repromoting SYNTHETIC nodes — the latter happens when accumulated learner-event evidence and source-cross-reference work confirms the concept's coherence post-hoc, at which point the node may be repromoted to INTERPRETED via supersession (the SYNTHETIC node is deprecated and a new INTERPRETED node carries the same semantic content).

The Phase 4 graph audit (per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) and [ROADMAP.md](../ROADMAP.md) Phase 4) emits a soft-warn category for SYNTHETIC nodes during validation runs. The soft-warn populates a review queue that the Opus batch cycle consumes; it is not a hard-fail because SYNTHETIC nodes are legitimate authoring outputs (not bugs) and the Phase 4 utility is read-only during validation. The review queue is cleared by either repromotion (supersession to INTERPRETED) or sustained low tension density (the node is not surfacing problems and can sit at SYNTHETIC indefinitely).

## Model Tiering
**Added: 2026-04-07**

Opus for graph construction, cross-domain edge generation, and periodic self-correction review — infrequent tasks requiring heavy reasoning and nuanced judgment about conceptual dependencies across frameworks. The self-correction review (see above) is an Opus responsibility: analyzing accumulated tension logs against the full graph state to propose structural edits. Sonnet for daily teaching interactions — high-volume, well-constrained tasks (Socratic dialogue, concept checks, syllabus lookups, learner state updates, tension logging) where Sonnet's capabilities are fully sufficient.

---
*Last updated: 2026-04-30 (S-0010 — Synthetic-Node Review Queue subsection added under Self-Correction Pipeline, cross-linking to the new `confidence_level` column on the Node Schema per Phase 1.3 / ADR 0030; previous update 2026-04-29 (S-0007 — `tension_log.exchange_summary` shape constrained from `TEXT NOT NULL` to JSONB-with-named-fields per ADR 0026; spontaneous-connection unresolved-reference handling clarified))*
