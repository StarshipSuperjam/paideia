# ADR 0087 — Two-hop neighborhood retrieval shape

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0152

## Context

[`product/docs/tensions.md`](../docs/tensions.md) carries OQ-DEC1-B ("Two-hop neighborhood retrieval shape for teaching session context") as decide-before-Phase-6, open since 2026-04-29 (S-0001). [`product/docs/self-correction.md:57-61`](../docs/self-correction.md:57) commits to the teaching context shape — *"the current concept node, its immediate prerequisites and their mastery states for this learner, the learner's recent event history on the current concept, and a shallow neighborhood of the local graph topology — node IDs and labels within two hops of the current concept"* — but leaves four concrete sub-dimensions open:

1. **Prereq scope**: which prerequisites count? Immediate one-hop? Recursive-up-to-rigor-floor? All ancestors?
2. **Two-hop edge-type filter**: which edges count toward the two-hop traversal? Only `pedagogical_prerequisite`? Also `historical_influence`? Also the reserved `enables` / `informed_by`?
3. **Alias resolution**: when a learner reference matches multiple nodes ("Kant" → Transcendental Idealism, Categorical Imperative, Synthetic A Priori, ...), what does the entity-resolution service return?
4. **Token-cost target**: is there a named per-turn token budget for the neighborhood context?

A documented asymmetry to resolve: mastery computation walks only `pedagogical_prerequisite` edges (per [`product/docs/learner-model.md`](../docs/learner-model.md)), but the teaching neighborhood is currently unconstrained on edge type in the source-of-truth doc. [ADR 0014](0014-sonnet-teaches-opus-reviews.md) Consequences line 23 informally settles sub-dim 1 — *"current concept + one-hop prerequisites + two-hop entity-resolution neighborhood"* — and line 30 (post-S-0128 amendment) settles sub-dim 4 — pedagogical-degradation discipline downshifts two-hop → one-hop under context-amplification pressure, with no fixed budget. Sub-dims 2 and 3 remain open and require explicit settlement before Phase 6 entry.

This ADR depends on [ADR 0086](0086-model-agnostic-embedding-storage-architecture.md) (model-agnostic embedding storage; landed earlier in this session). ADR 0086's per-dim partition tables back the entity-resolution service that this ADR's neighborhood retrieval consumes; the alias-resolution algorithm authored here issues queries against the `node_embeddings_<dim>` partitions ADR 0086 commits to.

### Edge-type registry state (relevant for sub-dim 2)

Per [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../seed-graph/migrations/PREDICATE_MANIFEST.md):

- `pedagogical_prerequisite` — active; structural edge for traversal, syllabus generation, mastery computation. 515 edges in the current seed graph.
- `historical_influence` — active; display-only per [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md); not consumed by traversal, syllabus, or mastery. 17 edges in the current seed graph (per [`engine/STATE.md`](../../engine/STATE.md)). May legitimately form cycles (mutual influence is not a structural error).
- `enables` and `informed_by` — reserved-but-unused since the Phase 4 graph-validation gate; named in `build_plan/P_2_graph_validation.md` illustrative list; no current design document commits to them. Per the PREDICATE_MANIFEST discipline, they are due for removal at the next health-check audit if still unused.

### Load-bearing premises

*Per the [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers under the "contract-shape change" class — it commits the entity-resolution neighborhood shape that Sonnet's per-turn context preparation is bound to.*

1. **The pedagogical impact of in-session vs. batch-review handling of cross-thinker references is asymmetric.** When a learner spontaneously says *"this reminds me of Nietzsche"* mid-Kant teaching, the in-session response (Sonnet recognizes the reference and engages: *"yes, Nietzsche's critique of Kantian ethics..."*) is pedagogically valuable in a way the batch-review response (logged as `spontaneous_connection`, processed by Opus weeks later) cannot replicate. The moment passes; the learner's engagement signal is in real time. *Falsifier:* a future first-exercise observation where in-session resolution of historical-influence connections produces no measurable pedagogical lift over batch-review-only handling. *Test status:* unverifiable in-context — requires Phase 6+ teaching-session empirical signal. Named in Consequences with first-exercise readiness criterion.

2. **Including `historical_influence` edges in the two-hop neighborhood does not invalidate mastery's prereq-only edge scope.** Mastery computation is about *structural readiness* (which prerequisites must exist for the current concept to be teachable); entity-resolution recognition is about *vocabulary match* (which graph nodes does this learner reference touch?). The asymmetry — narrower edge filter for mastery, broader filter for entity-resolution recognition — matches teaching intuition: *"I recognize the reference but it's not on the critical path."* *Falsifier:* a Phase 6 case where mastery-side and recognition-side edge-type scope divergence causes a teaching incoherence (e.g., Sonnet recognizes a reference via historical_influence then asks the learner to demonstrate mastery on it, treating it as a critical-path concept). *Test status:* design-level analysis suggests the asymmetry is teaching-coherent if Sonnet's prompt scaffolding distinguishes "recognized reference" from "current critical-path concept." Named in Consequences with `engine/operations/expression-contract-instantiation.md`-equivalent care at Sonnet prompt-authoring time.

3. **`enables` and `informed_by` are dead vocabulary, not deferred decisions.** PREDICATE_MANIFEST.md committed them as reserved at Phase 4; 23+ sessions have passed without any design document committing them to active use; the manifest's own discipline ("If a reserved entry never gets used by the time the next periodic project health check fires, it should be removed") names the removal trigger. *Falsifier:* a current design document references `enables` or `informed_by` as a planned edge type. *Test status:* attempted in-context. `git grep -i "enables\|informed_by"` across `product/docs/` and `product/adr/` returned only references to PREDICATE_MANIFEST.md itself and audit narrative. **Premise verified.** No active design document commits to either predicate. The reserved status is dead-code-equivalent for the predicate registry.

4. **Returning all candidates above a similarity threshold preserves teaching responsibility on Sonnet, where it belongs.** Sonnet's pedagogical agency includes asking clarifying questions when a reference is ambiguous; encoding a heuristic-best selector in the entity-resolution service moves that judgment out of Sonnet's prompt-layer surface and into infrastructure code. *Falsifier:* a Phase 6 case where the candidate-set return shape produces measurable Sonnet prompt-context bloat (e.g., per-turn token overhead > 200 tokens just for candidate-set serialization). *Test status:* design-level — n=1-3 BYOK users with two-hop neighborhoods of "a few dozen node IDs and labels" produce candidate sets of typically ≤5 candidates per reference; serialization cost is bounded. Named in Consequences as a known assumption with empirical-observation criterion.

## Decision

The teaching-session retrieval neighborhood is shaped as follows:

**Sub-dim 1 — Prerequisite scope:** **Immediate (one-hop) prerequisites only.** The current concept's direct prerequisite set, with each prerequisite's mastery state for this learner. Recursive-up-to-rigor-floor prerequisites are NOT included by default; if Sonnet needs deeper structural context for a specific turn, it issues a targeted follow-up retrieval (out-of-scope for the standing neighborhood shape). This makes explicit the ADR 0014 line 23 implicit commitment.

**Sub-dim 2 — Two-hop edge-type filter:** **`pedagogical_prerequisite` + `historical_influence`.** The two-hop traversal walks both active edge types. Mastery computation remains prerequisite-only — the asymmetry is deliberate. Entity-resolution recognition is broader than mastery's structural readiness scope so spontaneous cross-thinker references like *"this reminds me of Nietzsche"* resolve in-session against the 17 historical-influence edges currently in the graph (per [`engine/STATE.md`](../../engine/STATE.md)), rather than being deferred to Opus batch review. The reserved `enables` and `informed_by` predicates remain in their current reserved-but-unused state in PREDICATE_MANIFEST.md (the manifest's own discipline governs their fate at the next health-check audit; this ADR does not preempt that).

**Sub-dim 3 — Alias-resolution algorithm:** **Return all candidates above a similarity threshold AND mark the highest-confidence one as `presumed_match`.** The service returns the full candidate set with one tagged. Tagging combines similarity score + graph distance from current concept + learner mastery on each candidate, weighted equally at v1. Sonnet's prompt-layer scaffolding defaults to engaging the presumed match but may override based on in-context judgment (e.g., the learner's preceding turn establishes which Kant-related concept they meant). Reference cases where no candidate exceeds the threshold land as `tension_type=spontaneous_connection` per `self-correction.md:59` with `unresolved_reference` populated, preserving the existing miss-handling path.

**Sub-dim 4 — Token-cost target:** **No named budget.** The neighborhood is *"a few dozen node IDs and labels"* per the existing `self-correction.md:61` framing. The pedagogical-degradation discipline absorbed into [ADR 0014](0014-sonnet-teaches-opus-reviews.md) line 30 governs downshift triggers: under context-amplification pressure, the two-hop neighborhood shrinks to one-hop as a teaching move (not a cost-protection move). Phase 6+ empirical observation may surface a need to set a budget; this ADR commits no number now.

## Alternatives Considered

### Two-hop edge filter: `pedagogical_prerequisite` only

- **What:** Two-hop traversal walks only prerequisite edges. Historical-influence edges are not entity-resolution-visible. Cross-thinker spontaneous references that don't correspond to prerequisite edges become `spontaneous_connection` tension records for batch processing only.
- **Pros:** Symmetric with mastery-computation edge-type scope. Strongest single-rule simplicity. One edge type drives everything: traversal, syllabus generation, mastery, recognition.
- **Cons:** Sonnet acts like it didn't recognize a real cross-thinker reference in real time. Teaching feels colder; the cross-thinker dialogue lands as backlog data instead of in-moment engagement. The pedagogical agency Sonnet is supposed to exercise (per ADR 0014) is hampered by a structural blind spot.
- **Rejected because:** the in-session-vs-batch asymmetry (premise 1) makes the recognition value at the moment of utterance much higher than the value of delayed batch processing. Symmetry with mastery-computation scope is a structural elegance argument that loses to a real pedagogical-impact argument.

### Two-hop edge filter: all active edges + retire reserved predicates in same commit

- **What:** Same in-session pedagogical impact as the chosen Option 2. Additionally, this ADR retires the reserved `enables` + `informed_by` predicates from PREDICATE_MANIFEST.md in the same commit.
- **Pros:** Closes vocabulary-drift surface earlier than the manifest's next-health-check trigger; one fewer thing for future sessions to re-litigate.
- **Cons:** Couples two unrelated decisions (neighborhood retrieval shape + predicate registry hygiene) in one ADR. The PREDICATE_MANIFEST has its own removal-trigger discipline that fires at health-check audits; this ADR's surface doesn't need to preempt it.
- **Rejected because:** the manifest's own discipline already governs the removal cadence. Coupling here would create a precedent that any ADR touching predicate vocabulary inherits the registry's cleanup obligation. Premise 3 verified the predicates are dead vocabulary, but the cleanup is correctly scoped to the next health-check audit, not to this ADR.

### Alias resolution: heuristic-best (single-node return)

- **What:** Entity-resolution service returns one node — the candidate that minimizes graph distance to the current teaching concept AND has highest learner mastery score. Sonnet sees no candidate set; sees one resolution.
- **Pros:** Lower token cost in Sonnet's context (one node vs. set). Lower Sonnet prompt-complexity (no candidate-set adjudication scaffolding needed).
- **Cons:** Encodes a teaching heuristic in infrastructure code rather than in Sonnet's prompt. Silent miss-resolution risk — the learner meant Categorical Imperative; service returned Transcendental Idealism because of graph-distance proximity; Sonnet teaches against the wrong concept without knowing it. Pedagogical agency is moved from Sonnet (where teaching judgment belongs) into the resolution-service code (where it doesn't).
- **Rejected because:** preserving teaching responsibility on Sonnet (premise 4) is more important than the marginal token-cost savings of single-node return. The candidate-set serialization cost at n=1-3 users with two-hop neighborhoods of ≤a few dozen nodes is bounded; the silent-miss-resolution risk is structural and worse.

### Alias resolution: return all candidates with NO presumed_match tag

- **What:** Entity-resolution service returns the full candidate set with confidence scores only; no tagging. Sonnet adjudicates from scratch every time.
- **Pros:** Strongest preservation of teaching agency. Service is purely retrieval; teaching is purely prompt-layer.
- **Cons:** Common-case unhappy path — for a clear reference ("Kant on synthetic a priori" → Synthetic A Priori is the obvious match), Sonnet still scaffolds candidate-set adjudication in every prompt turn. Wasteful for the high-signal default case.
- **Rejected because:** the hybrid (return all + tag presumed_match) preserves teaching agency for ambiguous cases AND optimizes the common case where one candidate is clearly the match. The pure-return-all path makes the common case more expensive without buying additional agency.

### Prereq scope: recursive-up-to-rigor-floor

- **What:** The current concept's prerequisites + their prerequisites + their prerequisites, recursively, up to a rigor-floor threshold (e.g., stop at concepts with rigor < 0.4 — too foundational to be teaching-relevant).
- **Pros:** Sonnet sees more structural context per turn; can place the current concept in deeper dependency-chain perspective.
- **Cons:** Combinatorial growth on high-prerequisite-count nodes (e.g., Synthetic A Priori has 6+ recursive prerequisites). Token cost grows non-linearly with concept depth. Rigor-floor requires runtime rigor computation on every neighborhood retrieval. The teaching value is unclear at Phase 6 entry; ADR 0014's line 23 already commits to one-hop in informal context.
- **Rejected because:** the runtime-rigor-computation cost on every retrieval is non-trivial; the teaching-value premise for recursive context is untested; ADR 0014's existing one-hop commitment is already the implicit consensus; if Phase 6 surfaces a real need for deeper context, Sonnet can issue a targeted follow-up retrieval (out-of-scope for the standing neighborhood shape).

### Token-cost target: named ≤500-token budget with hard cap

- **What:** Set a per-turn neighborhood-context budget (e.g., ≤500 tokens); fail closed if exceeded.
- **Pros:** Predictable per-turn cost; easier to reason about per-turn API spend at scale.
- **Cons:** Premature mechanization. The pedagogical-degradation discipline absorbed into ADR 0014 line 30 already governs downshift triggers (two-hop → one-hop under pressure). A named budget without empirical data is arbitrary; the n=1-3-user Phase 6 entry scale doesn't surface budget pressure yet.
- **Rejected because:** ADR 0014 already names the downshift mechanism (pedagogical-degradation discipline); a named budget commits a number without empirical grounding. Defer until Phase 6+ empirical signal surfaces a real need.

## Consequences

- **`product/docs/self-correction.md` "Teaching Session Context" subsection (lines 55-61) gains a forward-pointer to ADR 0087** for the four-sub-dimension settlement. Done in this commit.

- **`product/docs/architecture.md` Entity-Resolution-Service paragraph** gains a back-reference to ADR 0087 for the alias-resolution algorithm. Done in this commit.

- **`product/docs/learner-model.md`'s mastery-edge-scope vs. teaching-neighborhood-edge-scope asymmetry is documented explicitly** as a deliberate design — mastery walks `pedagogical_prerequisite` only; entity-resolution recognition walks `pedagogical_prerequisite` + `historical_influence`. The asymmetry is teaching-coherent because mastery is about structural readiness on the critical path while entity resolution is about vocabulary recognition; Sonnet's prompt scaffolding distinguishes "recognized reference" from "current critical-path concept." Done in this commit.

- **PREDICATE_MANIFEST.md is unchanged.** `enables` and `informed_by` remain in their current reserved-but-unused state. Premise 3 verified they are dead vocabulary; the manifest's own discipline governs removal at the next health-check audit. This ADR explicitly does not preempt that cadence.

- **Sub-dim 2's edge-filter decision creates an entity-resolution recognition surface that walks `historical_influence`.** The 17 current historical-influence edges become entity-resolution-visible at Phase 6 entry. Future seed-authoring sessions that add historical_influence edges enlarge this surface; the cost is proportional to the edge count (each historical_influence edge adds at most 2 nodes to the two-hop neighborhood of one or both endpoints).

- **First-exercise readiness for this ADR** is consolidated into the first Phase 6 teaching session that exercises the neighborhood retrieval against a real learner-reference. Tier-1 closures: (T1-A) two-hop traversal returns prereq + historical_influence nodes correctly; (T1-B) alias resolution returns full candidate set with `presumed_match` tag; (T1-C) Sonnet's prompt-layer correctly distinguishes presumed_match adjudication from candidate-set override. No separate `engine/build_readiness/` note — the closure surfaces naturally in the Phase 6 self-correction master plan's first teaching-session-loop work item.

- **`product/docs/tensions.md` OQ-DEC1-B section flips from "Open" to "Resolved by ADR 0087"** in the same commit as this ADR.

- **No supersession.** ADR 0014 (Sonnet teaches, Opus reviews), ADR 0026 (persistent learner storage structural-not-substantive), ADR 0061 (historical_influence retyping), and ADR 0086 (model-agnostic embedding storage) all remain Accepted; this ADR commits to a retrieval shape that consumes their substrates.

- **OQ-DEC1-D (chunk-resolver vs SEP URL pointers) is now the last open Phase-6-blocker.** ADR 0088 (next in this session) settles D; Phase 6 entry unblocks after.

## See also

- [ADR 0014](0014-sonnet-teaches-opus-reviews.md) — Sonnet teaches, Opus reviews; line 23 implicitly committed to one-hop prerequisites in this ADR's sub-dim 1; line 30 governs sub-dim 4's pedagogical-degradation discipline.
- [ADR 0026](0026-persistent-learner-storage-structural-not-substantive.md) — Persistent learner storage structural-not-substantive; the schema substrate for unresolved-reference recording per sub-dim 3.
- [ADR 0061](0061-historical-influence-retyping-for-history-terminator-bridges.md) — Historical-influence retyping; this ADR extends `historical_influence`'s role from "display-only on Discovery surface" to "display-only + entity-resolution-visible during teaching."
- [ADR 0086](0086-model-agnostic-embedding-storage-architecture.md) — Model-agnostic embedding storage; the substrate this ADR's alias-resolution queries run against.
- [ADR 0084](../../engine/adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — Extraction step (third natural exercise in this session).
- [`product/docs/self-correction.md`](../docs/self-correction.md) "Teaching Session Context" — original commitment now ADR-specified.
- [`product/docs/architecture.md`](../docs/architecture.md) "Entity Resolution Service" — alias-resolution algorithm consumer.
- [`product/docs/learner-model.md`](../docs/learner-model.md) — mastery-vs-entity-resolution edge-scope asymmetry now documented as deliberate.
- [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../seed-graph/migrations/PREDICATE_MANIFEST.md) — `enables` and `informed_by` reserved status unchanged.
- [`product/docs/tensions.md`](../docs/tensions.md) OQ-DEC1-B — resolved by this ADR.
