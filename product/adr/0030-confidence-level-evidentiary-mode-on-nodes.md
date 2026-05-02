# ADR 0030 — `confidence_level` is the evidentiary-mode axis on nodes

- **Status:** Accepted
- **Date:** 2026-04-30
- **Deciders:** S-0010 (Phase 1.3 — column addition completing Phase 1)

## Context

The Node Schema in [`docs/architecture.md`](../docs/architecture.md) already carries two columns whose semantics could plausibly be conflated with one another and with the column this ADR adds:

- **`provenance`** (`'human' | 'ai_proposed' | 'ai_confirmed'`) — *who* authored the node and where it sits in the proposal-to-confirmed lifecycle. Mirrors the edge `provenance` model. Authoring channel and lifecycle stage.
- **`confidence`** (REAL, 0.0–1.0) — *how sure we are* the node belongs in the graph at all. A numeric belief that updates over time as evidence accumulates through learner events and the Opus batch review (per [ADR 0014](0014-sonnet-teaches-opus-reviews.md) / [`docs/self-correction.md`](../docs/self-correction.md)).

[ROADMAP.md](../ROADMAP.md) Phase 1.3 specifies a third axis: `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`), naming the *type* of evidence backing the node's existence at authoring time. Phase 5.2 already commits to "mark `confidence_level: INTERPRETED` until validated against learner outcomes or expert review" for first-pass seed-graph nodes. [ADR 0016](0016-graph-construction-needs-live-validation.md) already commits the Phase 4 graph-audit utility to a soft-warn category for `confidence_level: SYNTHETIC` flagged for review queue. The column has scattered downstream commitments before it has a schema slot or a settled semantic.

Two questions the spec leaves to this session.

**Are the three columns genuinely orthogonal?** The naming invites conflation: `confidence` and `confidence_level` read as variants of the same notion. If the column is a discretization of the numeric belief — "high / medium / low confidence-bin" — it duplicates the numeric column and adds nothing. If it is a third independent axis, the orthogonality argument has to hold up under examination. Two combinations test the orthogonality:

- **`provenance = 'human'` + `confidence_level = 'SYNTHETIC'`** is permitted and not paradoxical: a human curator authors a service node to terminate a cross-domain prerequisite chain (per the Termination Principle in [`docs/architecture.md`](../docs/architecture.md) Cross-Domain Porosity) where no source independently structures the concept as a coherent unit.
- **`confidence = 0.3` + `confidence_level = 'EXTRACTED'`** is permitted but rare: a node lifted from a source's structuring whose belief has decayed under accumulated counter-evidence (e.g., the source's own classification turns out to disagree with how the field treats the concept). The label *does not* update with that decay; the numeric belief does. The label records evidentiary mode at authoring time, full stop.

These combinations are the working test for orthogonality. The columns answer different questions: who, how-sure-now, and what-kind-of-evidence-at-authoring. They are independent axes that happen to correlate in practice (most EXTRACTED nodes carry high confidence; most SYNTHETIC nodes carry low confidence at first), but the correlation is empirical, not definitional.

**What is the right default?** Three precedent comparisons:

- `provenance DEFAULT 'human'` — biases toward strongest claim (highest authority).
- `confidence DEFAULT 1.0` — biases toward strongest claim (highest belief).
- `status DEFAULT 'active'` — biases toward most-common-state (active).

The precedent has two patterns: strongest-claim and most-common-state. Following strongest-claim would default to `EXTRACTED` (highest evidentiary mode), but that silently overclaims source backing for the *typical* Phase 5 authoring case (INTERPRETED per Phase 5.2). Following most-common-state defaults to `INTERPRETED` and matches Phase 5.2's explicit baseline. The `SYNTHETIC` default would over-flag the Phase 4 review queue. Most-common-state wins.

A third question is named here for the durable record but does not block the column landing.

**Does the label update over time?** No. The label records evidentiary mode at the moment of authoring; supersession is the channel for changing it. If accumulated evidence repromotes a SYNTHETIC node to a coherent unit warranting INTERPRETED status, the SYNTHETIC node is deprecated (per [ADR 0021](0021-node-deprecation-status-superseded-by.md)) and a new INTERPRETED node carries the same semantic content via `superseded_by`. This keeps the label stable for audit purposes and prevents drift where labels migrate silently as belief moves. The numeric `confidence` is the channel for belief updates; `confidence_level` is the channel for evidentiary-mode lock-in at authoring.

## Decision

`confidence_level` is added to the Node Schema as `TEXT NOT NULL DEFAULT 'INTERPRETED'`, with allowed values `'EXTRACTED' | 'INTERPRETED' | 'SYNTHETIC'`.

**The column is a third epistemic axis, orthogonal to `provenance` and to numeric `confidence`.**

- `provenance` answers: *who authored the node and what's its lifecycle stage?*
- `confidence` answers: *how sure are we the node belongs in the graph, and how does that belief move with evidence?*
- `confidence_level` answers: *what kind of evidence backed the node's existence at the moment of authoring, fixed-at-write?*

**Enum semantics:**

- **`EXTRACTED`** — The concept is lifted from a source's own structuring. A SEP article whose TOC names it as a coherent unit, a curriculum prerequisite list naming it, a graph dataset framing it as a node. Pedagogical work is vocabulary alignment, not concept invention. Strongest evidentiary mode: a third-party source has independently judged the concept coherent at the granularity it appears.
- **`INTERPRETED`** — The concept emerges from pedagogical judgment about source material that does not itself structure around the concept. Source material exists and is consulted; the human curator or AI infers that the concept exists at the granularity required by the Node Granularity Principle in [`docs/architecture.md`](../docs/architecture.md). Most Phase 5 first-pass nodes are INTERPRETED per [ROADMAP.md](../ROADMAP.md) Phase 5.2.
- **`SYNTHETIC`** — The concept is generated wholesale. No clear source structures the concept as a coherent unit; the node was generated to fill a structural gap. Service nodes terminating cross-domain prerequisite chains (per the Termination Principle in [`docs/architecture.md`](../docs/architecture.md) Cross-Domain Porosity) are common SYNTHETIC candidates. Opus batch-review node-split proposals lacking direct source basis also start SYNTHETIC. **First candidates for self-correction review** per [`docs/self-correction.md`](../docs/self-correction.md) (Synthetic-Node Review Queue) and the Phase 4 audit soft-warn category per [ADR 0016](0016-graph-construction-needs-live-validation.md) and [ROADMAP.md](../ROADMAP.md) Phase 4.

**Default choice:** `'INTERPRETED'` matches Phase 5.2's seed-authoring baseline and is the middle epistemic claim. EXTRACTED would silently overclaim source backing on forgot-the-column writes; SYNTHETIC would over-flag the Phase 4 review queue. Authoring sessions explicitly downgrade to SYNTHETIC for service nodes and explicitly upgrade to EXTRACTED for corpus-aligned nodes; the default is the most-common-conscious-case.

**Update discipline:** the label does not update over time. Repromotion or demotion happens via supersession (per [ADR 0021](0021-node-deprecation-status-superseded-by.md)) — the existing node is deprecated and a new node with the appropriate `confidence_level` is authored, linked through `superseded_by`. The `confidence` numeric column is the channel for belief evolution; `confidence_level` is fixed-at-write.

**Storage representation:** `TEXT` (not Postgres ENUM) following the precedent of `provenance` and `status` in the same schema. Allowed-value enforcement is application-side and Phase 4 audit-side, not DB-level. Adding a new value (e.g., a hypothetical `OBSERVED` or `DERIVED` mode if a future need surfaces) does not require migration; it requires this ADR to be superseded with the new enum value documented and the Phase 4 audit updated to recognize it.

## Consequences

- **Naming risk acknowledged.** The name `confidence_level` reads as a categorical bin of `confidence`. The name is settled across [STATE.md](../STATE.md), [ROADMAP.md](../ROADMAP.md) Phase 1.3 / Phase 4 / Phase 5.2, and [ADR 0016](0016-graph-construction-needs-live-validation.md); renaming now would invalidate downstream references and force a chain of updates whose value is purely cosmetic. This ADR's Decision section is the durable mitigation: future sessions reasoning about either column must read this ADR first to avoid conflating the categorical evidentiary-mode label with the numeric belief score.
- **Schema is now Phase-3-ready for the column.** The Phase 3 SQL migration includes `confidence_level` per [ROADMAP.md](../ROADMAP.md) Phase 3 success criteria (already names `confidence_level` in the column list).
- **Phase 4 audit category lands without code change.** [ADR 0016](0016-graph-construction-needs-live-validation.md) already names the SYNTHETIC soft-warn; the Phase 4 implementation against the live DB now has a concrete column to query. No revision to ADR 0016 is required.
- **Phase 5.2 baseline is concrete.** First-pass authored nodes carry `confidence_level: 'INTERPRETED'` matching Phase 5.2's commitment. Service-node sessions (P_8.5) explicitly downgrade to `'SYNTHETIC'` at authoring; corpus-aligned sessions explicitly upgrade to `'EXTRACTED'` when a source's TOC or structuring frames the concept directly.
- **Self-correction pipeline gains a queue.** [`docs/self-correction.md`](../docs/self-correction.md) (Synthetic-Node Review Queue, added S-0010) names SYNTHETIC nodes as first review candidates within the Opus batch cycle. The cross-link makes the column's downstream consumer concrete instead of leaving it implicit.
- **Repromotion discipline.** A SYNTHETIC node confirmed coherent post-hoc is repromoted via supersession (per [ADR 0021](0021-node-deprecation-status-superseded-by.md)), not via in-place label update. This preserves audit clarity: every label is the label authored at write-time; belief evolution lives in `confidence`.
- **Open future ADR.** If the SYNTHETIC review-queue workload exceeds Opus batch capacity, a sub-decision about queue prioritization (tension density vs. age vs. cross-domain centrality) may warrant an ADR superseding or extending the simple "by tension density above threshold" cited in [`docs/self-correction.md`](../docs/self-correction.md) Synthetic-Node Review Queue. Not blocking; surfaces if and when Phase 5/6 evidence shows the simple rule is insufficient.

## See also

- [`docs/architecture.md`](../docs/architecture.md) — Node Schema with `confidence_level` column landed S-0010.
- [`docs/self-correction.md`](../docs/self-correction.md) — Synthetic-Node Review Queue subsection added S-0010.
- [ADR 0016](0016-graph-construction-needs-live-validation.md) — Phase 4 graph-audit soft-warn category for SYNTHETIC nodes.
- [ADR 0021](0021-node-deprecation-status-superseded-by.md) — supersession is the channel for evidentiary-mode change.
- [ROADMAP.md](../ROADMAP.md) Phase 1.3 (this ADR's spec); Phase 4 (the audit consumer); Phase 5.2 (the seed-authoring consumer).
