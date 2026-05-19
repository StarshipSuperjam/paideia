---
session_id: S-0208
session_type: build
closed_at: "2026-05-19T05:35:00Z"
material_change_class: mixed
module: multi
summary: Tier-A Cluster 2 (ADR 0098 + migration 0130 + rollback); Issue #152 closed; #151 re-scoped + TCP keepalive. ADR 0094/0095 T1-A re-verified.
---

# S-0208 — Tier-A Cluster 2 + #152 closure + #151 re-scope — 2026-05-19

Second Tier-A cluster-implementation ADR per [ADR 0094 product](../../../product/adr/0094-phase-6-scope.md) dependency order C1 → **C2** → C4 → C3 → C5. Three-phase session: (1) Issue #151 re-scope + TCP keepalive mitigation; (2) ADR 0098 + migration 0130 + paired rollback; (3) Issue #152 validator soft-warn + companion ADR 0098 soft-warn + Cluster-2-aware PREREQUISITE_EDGE_TYPES tuple rename.

## Added

- **[`product/adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md`](../../../product/adr/0098-tier-a-cluster-2-edge-type-taxonomy-and-three-relation-layering.md)** — three-relation layering (`pedagogical_dependence` / `conceptual_relatedness` / `historical_influence`) + per-layer controlled-vocabulary `edge_type` (16-pair compound CHECK constraint). Three plan-mode adjudications (compound CHECK over Postgres ENUM and lookup table; `edge_cross_layer_default_routing` forward-pointer only; defer L1.10 node-type partial coverage to Cluster 4). 6 ADR 0084 load-bearing premises (T1-A + T2-A + T2-B named).
- **[`product/seed-graph/migrations/0130_edges_three_relation_layering.sql`](../../../product/seed-graph/migrations/0130_edges_three_relation_layering.sql)** + paired **[`0130_edges_three_relation_layering_rollback.sql`](../../../product/seed-graph/migrations/0130_edges_three_relation_layering_rollback.sql)** — applied via `mcp__supabase__apply_migration`; round-trip verified (apply → rollback → re-apply produced identical row-level state at each step). Full contract block + 14-line Postcondition-Assertions per [ADR 0055](../../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5.
- **`engine/tools/validate.py`** — `_KEEPALIVE_KWARGS` module-level constant + extended `_read_graph_from_db` SELECT (fetches `edge_layer`, `expert_confidence`, `counterexamples`, `provenance`) + `_detect_edges_contestability_unguarded_high_confidence` (Issue #152) + `_detect_edges_provisional_hard_prerequisite` (ADR 0098 deliverable) + 2 new entries in `GRAPH_SOFT_WARN_CATEGORIES` + main audit loop wiring.
- **`engine/tools/apply_migration.py`** — `_KEEPALIVE_KWARGS` constant + threaded through all 4 `psycopg.connect` sites.
- **`engine/tools/test_validate.py`** — 18 new pytests across `TestPrerequisiteEdgeTypesRecognition` (4), `TestEdgesContestabilityUnguardedHighConfidence` (7), `TestEdgesProvisionalHardPrerequisite` (7); existing `TestReadGraphFromDbTimeouts` extended with keepalive assertions.
- **`engine/tools/test_apply_migration.py`** — 4 new pytests verifying keepalive kwargs reach all 4 connect sites + 2 helper functions.
- **engine_memory drawers:** decisions `f6b547da` (ADR 0098 conversational reasoning); pushback `1d1b2170` (user-pushback on "look at server-side logs first before designing client-side mitigation"); lesson `c8f90de5` (TCP keepalive is necessary-but-not-sufficient when server keeps L4 link active via low-level traffic); diary `1731842c`.

## Changed

- **Issue #151 on GitHub** — title re-scoped from "Supabase pooler wedge" to "Client-side hang in validate.py graph_audit during pre-commit — likely silent idle-connection drop (TCP keepalive mitigated S-0208)"; body rewritten with `mcp__supabase__get_logs` server-side-clean evidence + working hypothesis + S-0208 mitigation + diagnostic capture hints for any future recurrence. Closure criterion #4 observation window opened (5 wedge-free build sessions to close).
- **Issue #152 on GitHub** — closed (auto-closed by eager-claim commit message's "Close #152" keyword; closure comment added separately).
- **[`product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md`](../../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md)** — in-body amendment: the 17 historical_influence edges now carry `edge_layer='historical_influence'` + `edge_type='influenced_by'` per ADR 0098; lossless retyping; ADR 0061 commitment preserved within Cluster 2's three-layer structure.
- **[`product/adr/0094-phase-6-scope.md`](../../../product/adr/0094-phase-6-scope.md)** — T1-A re-verification marker added (Cluster 2 implementable without re-decomposition).
- **[`product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md`](../../../product/adr/0095-phase-6-tool-stack-postgres-jsonb-confirmed-with-oss-revisit-bar.md)** — T1-A re-verification marker added (Postgres+JSONB continues to hold through Cluster 2).
- **[`product/docs/architecture.md`](../../../product/docs/architecture.md):182** — edge_type framing flips from "intentionally unconstrained" to "constrained by per-layer compound CHECK per ADR 0098"; new edge_layer documentation added.
- **[`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)** — restructured around the per-layer registry: 16 new predicate rows (10 pedagogical + 3 conceptual + 3 historical); prior 2 (`pedagogical_prerequisite`, `historical_influence`) flipped to "Superseded by ADR 0098" section.
- **[`product/seed-graph/migrations/ROUTING.md`](../../../product/seed-graph/migrations/ROUTING.md)** — prefix-scheme table amended (C2=0130-0139 used; C4/C3/C5 reserved); new S-0208 narrative entry documenting migration 0130 + rollback + round-trip verification.
- **[`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md)** — new "TCP keepalive on psycopg connections" section + 2 new soft-warn entries in the Graph-audit listing with SQA-review disposition guidance.
- **`public.edges` schema (live DB)** — 1 ADD COLUMN (`edge_layer`) + 2 CHECK constraints (`edges_edge_layer_valid` + `edges_edge_layer_type_coupling`) + 533 row UPDATEs (516 + 17); row count invariant; UNIQUE preserved; RLS preserved; settings.graph_version unchanged at 16 (pure schema + retyping).

## Notes

- **TCP keepalive falsified empirically mid-session.** At ~30 min after Phase 1 landed, the next pre-commit invocation of validate.py wedged exactly the documented #151 shape (ESTABLISHED TCP, state S on poll(), 6+ min elapsed past both the 45s watchdog AND the keepalive detection window). Kernel keepalive idle-timer apparently doesn't engage when pgbouncer/Supavisor maintains L4 traffic on the link even when application-layer protocol has wedged. Recovery: user restarted workstation (NOT Supabase). Post-restart, validate.py ran clean. User hypothesis at session close: cross-process Python contamination from non-project tools may be the interference vector — investigation candidate for #151's next iteration.
- **#152 firing-volume mismatch.** Issue's body predicted ~17 fires post-Cluster-2; reality is all 533 because Cluster 2 retyped only `edge_type`, not `expert_confidence`. The 516 retyped soft_prerequisite edges all retain prior high-band confidence from Phase 5 seed authoring + production-audit follow-ups. Cluster 7 SQA predictive-validity pipeline is the natural successor that downgrades confidence based on learner-trace evidence; until then the warn is a counter over the entire seed corpus rather than a defect indicator on specific edges.
- **PREREQUISITE_EDGE_TYPE silent breakage.** Pre-S-0208 the validator's hardcoded `PREREQUISITE_EDGE_TYPE = "pedagogical_prerequisite"` silently broke at the Phase 2 commit (migration 0130 retyped all 516 production edges). Every topology-aware soft-warn lost signal — observed as `orphan_leaf: 380` in the Phase 2 commit's validator output. Phase 3 fix: tuple containing strict-prereq sub-types + backward-compat entry; 8 affected check sites updated from `!= constant` to `not in tuple`. 4 regression pytests verify recognition.
- **Round-trip verification of migration 0130.** Apply → rollback → re-apply produced identical row-level state at each step (516 + 17 by layer/type counts confirmed via `mcp__supabase__execute_sql` at each step).
- **End-to-end ADR 0094 / 0095 T1-A re-verification.** Cluster 2's clean landing (1 new column + 2 CHECK constraints + 2 retyping UPDATEs within one transaction; no scope re-shape; no Postgres-shape friction) further reinforces both premises. Both ADRs' Consequences sections amended in-body.
