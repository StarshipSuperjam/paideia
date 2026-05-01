# P_6 — Self-correction pipeline (Phase 6)

> Tension log + Opus batch review pipeline operational. Sonnet teaching-side emits tension records; Opus reviewer reads the log and proposes graph edits via a confidence-weighted pipeline.

## Phase scope

Phase 6 implements [`product/docs/self-correction.md`](../product/docs/self-correction.md) as live machinery. The `tension_log` schema landed at [`P_1_sql_schema.md`](P_1_sql_schema.md); this chunk fills the producer side (Sonnet emits records during teaching) and the consumer side (Opus batch reviewer proposes graph edits).

Per [ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), the division of labor is structural: Sonnet teaches in-session (production cost); Opus reviews offline in batch (judgment cost). The self-correction pipeline is what closes the loop between the two.

## Output

- **`engine/tools/opus_review.py`** (new file) — the Opus batch reviewer. Reads from `tension_log`, applies the confidence-weighted pipeline per [`product/docs/self-correction.md`](../product/docs/self-correction.md), proposes graph edits as **provisional ADR-status decisions**. Provisional means: a human approval step gates the actual graph mutation; the Opus output is recommendation, not action.
- **`product/AGENT_INSTRUCTIONS.md`** updates — emission-side prose for Sonnet to write `struggle_unresolved`, `unexpected_ease`, `spontaneous_connection`, `source_ineffective`, `mastery_contradiction` records per [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md)'s structured-fields constraint. The emission contract is appended to `AGENT_INSTRUCTIONS.md` (or filed as a sibling, settled in-session).
- **Stability constraint enforcement** — between review cycles the graph is read-only at the structural level. Learners never encounter mid-session structural changes per [ROADMAP Phase 6](../ROADMAP.md). Implementation: a database constraint or application-level guard prevents node/edge mutations during active learner sessions.
- **Scheduling** — Opus reviewer runs as a scheduled batch job. Cadence settled in-session (likely daily or per-N-tension-records).
- **Provisional ADR file output** — the reviewer writes proposed graph edits as draft ADR files in a `_proposed/` subdirectory (or equivalent staging area settled in-session); the human approves or rejects before promotion to `engine/adr/` or `product/adr/`.

## Success criteria

- `engine/tools/opus_review.py` runs end-to-end against a seed-graph DB with synthetic `tension_log` records; produces at least one provisional graph-edit recommendation.
- The five tension categories (per [`product/docs/self-correction.md`](../product/docs/self-correction.md)) emit correctly from a Sonnet teaching session per the updated `AGENT_INSTRUCTIONS.md` contract.
- Stability constraint verified: a write attempt during a simulated active learner session is blocked.
- The provisional-ADR pipeline produces a draft ADR file with the Nygard structure per [`engine/operations/adr-authoring.md`](../engine/operations/adr-authoring.md).
- ENGINE_LOG entry under `[Unreleased]` for `Added` (`opus_review.py`, the emission contract additions, the stability-constraint mechanism).

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 6.
- [`product/docs/self-correction.md`](../product/docs/self-correction.md) — the load-bearing design doc.
- [`product/AGENT_INSTRUCTIONS.md`](../product/AGENT_INSTRUCTIONS.md) — the existing emission contract context.
- [`product/adr/0014-sonnet-teaches-opus-reviews.md`](../product/adr/0014-sonnet-teaches-opus-reviews.md) — division of labor.
- [`product/adr/0026-persistent-learner-storage-structural-not-substantive.md`](../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — `tension_log` `exchange_summary` structured-fields constraint.
- The Phase DEC.1 ADRs from [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — the retrieval shape constrains the Opus reviewer's neighborhood-query patterns.
- [`engine/tools/validate.py`](../engine/tools/validate.py) — for validation patterns the Opus reviewer's recommended-edit verification can borrow.

## Load-bearing ADRs

[ADR 0014](../adr/0014-sonnet-teaches-opus-reviews.md), [ADR 0026](../adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0027](../adr/0027-rendering-policy-prompt-layer-contract.md) (forbidden-token discipline applies to the emission contract additions to `AGENT_INSTRUCTIONS.md`), the four Phase DEC.1 ADRs.

## Estimated context budget

Substantive tier: target 60%, cap 70%. The work spans Python implementation (`opus_review.py`), prose authoring (`AGENT_INSTRUCTIONS.md` emission contract), and database constraint design. Context-amplification risk is moderate — `self-correction.md` is long; selective reading per the chunk's responsibilities is the discipline.

## Session sequencing

Multi-session likely. Natural split:

- **Session 1:** `opus_review.py` skeleton + `AGENT_INSTRUCTIONS.md` emission-contract additions + the Sonnet-side smoke test.
- **Session 2:** stability-constraint mechanism + provisional-ADR pipeline + the Opus-side end-to-end test against seed-graph DB.

If the Opus API integration proves heavier than expected, a third session may be needed.

## Open tensions consumed

None directly. The Phase DEC.1 ADRs (`OQ-DEC1-A` through `OQ-DEC1-D`) are consumed as input.

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 6 — full phase scope.
- [`product/docs/self-correction.md`](../product/docs/self-correction.md) — the load-bearing design doc.
- [`../adr/0014-sonnet-teaches-opus-reviews.md`](../adr/0014-sonnet-teaches-opus-reviews.md) — the division-of-labor ADR.
- [`P_5_retrieval_mastery_decisions.md`](P_5_retrieval_mastery_decisions.md) — predecessor; informs Opus reviewer's retrieval queries.
- [`P_7_teaching_layer.md`](P_7_teaching_layer.md) — successor; consumes the Sonnet emission contract from this chunk.
