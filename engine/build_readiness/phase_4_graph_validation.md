# Phase 4 — Graph validation build-readiness report

> Authored by S-0034 (gate session) for S-0035 (build session) per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md). The build session reads this at boot. If Tier 1 contains unresolved items at boot, the build session halts and escalates.
>
> Chunk: [`build_plan/P_2_graph_validation.md`](../../build_plan/P_2_graph_validation.md). Source documents: [`product/docs/architecture.md`](../../product/docs/architecture.md) (graph schema), [`product/docs/self-correction.md`](../../product/docs/self-correction.md) (Phase 4 graph self-correction), [`engine/build_readiness/phase_3_sql.md`](phase_3_sql.md) (forward-pointers inherited). Load-bearing ADRs: [0016](../adr/0016-graph-construction-needs-live-validation.md) (the contract), [0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) (forbidden-token enumeration for the render-readiness check), [0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) (`confidence_level: SYNTHETIC` review queue).

## Pre-session decisions (Tier 1 resolutions)

Three Tier 1 findings settled in S-0034 before S-0035 opens. Each cites the source documents that ground the resolution.

### T1-A — Phase 4 scope: S-0035 lands all four P_2 sub-deliverables

**Decision.** S-0035 implements the full Phase 4 scope — sub-deliverables 4.1 (`validate_graph()` flesh-out), 4.2 (ROUTING.md per-session narrative + range-collision fix), 4.3 (PREDICATE_MANIFEST.md v1 registry), 4.4 (`seed-chunked-authoring.md` per-session workflow) — in one session. Partial-close is the established escape hatch if the budget caps mid-work; default is single-session full execution.

**Rationale.** [`build_plan/P_2_graph_validation.md:79-81`](../../build_plan/P_2_graph_validation.md) names the sequencing as "Single session if 4.1 alone fits the budget; otherwise split." The chunk's substantive-tier budget (target 60%, cap 70% per [`build_plan/P_2_graph_validation.md:77`](../../build_plan/P_2_graph_validation.md)) covers psycopg integration + SCC detection + manifest authoring + workflow doc — the documentation deliverables (4.2/4.3/4.4) are mechanical fill-in once the validator extension (4.1) lands. Bundling preserves the contract handshake: PREDICATE_MANIFEST.md governs `undeclared_predicate` soft-warns ([`engine/tools/validate.py:1265`](../tools/validate.py)), and shipping the validator without the registry would fire spurious warns against any future seed edge.

**Artifact.** This Tier 1 commitment lives in the report; no new ADR needed — the scope was committed in P_2 at S-0023 authoring, and the gate's job is to halt accidental deferral. If S-0035's outcome_summary records `closed_partial`, the next session inherits the unfinished sub-deliverable as its scope. The bundle is the design intent of P_2 per [`build_plan/P_2_graph_validation.md:13`](../../build_plan/P_2_graph_validation.md) ("Four deliverables per ROADMAP Phase 4").

### T1-B — PREDICATE_MANIFEST.md authoring timing: v1 registry lands at S-0035

**Decision.** The canonical edge-type registry is populated in S-0035, not deferred to Phase 5. The two predicates required by extant migration + design-document evidence land in v1: `pedagogical_prerequisite` (per [`product/seed-graph/migrations/0003_edges.sql:54`](../../product/seed-graph/migrations/0003_edges.sql), the column default; structural — used in traversal, syllabus generation, mastery computation per [`product/docs/architecture.md:182`](../../product/docs/architecture.md)) and `historical_influence` (per [`product/docs/architecture.md:182`](../../product/docs/architecture.md), display-only but a named legitimate type). Phase 5 seed-authoring sessions add new predicates as authoring discovers needs, per the same-session ENGINE_LOG-tracked discipline ([`product/seed-graph/migrations/PREDICATE_MANIFEST.md:9-13`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)).

**Rationale.** [`build_plan/P_2_graph_validation.md:44-46`](../../build_plan/P_2_graph_validation.md) explicitly assigns "Flesh out `product/seed-graph/migrations/PREDICATE_MANIFEST.md`" to Phase 4, with example predicates (`prerequisite`, `enables`, `informed_by`, `cross_domain_dependency`, etc.). [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:19`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)'s placeholder prose ("The first entries land when Phase 5's epistemology session ships the first seed migration.") is stale — a pre-P_2-finalization framing from S-0001. P_2 supersedes it. Resolution: Phase 4 populates the registry with what current design documents commit to (the two architecture.md-cited types); P_2's example list (`enables`, `informed_by`, `cross_domain_dependency`) is illustrative and is *not* committed in v1 because no current design document names them as required. Phase 5 sessions add as needed.

**Artifact.** Resolution lands in S-0035's PREDICATE_MANIFEST.md authoring. The placeholder prose at [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:19`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) is replaced by the v1 registry table (see T2-G below for the concrete table contents). ENGINE_LOG entry under `Added` for the two predicates at S-0035 close.

### T1-C — Database connection: psycopg with service_role authentication

**Decision.** `validate_graph()` connects via `psycopg` (committed in [`build_plan/P_2_graph_validation.md:17`](../../build_plan/P_2_graph_validation.md): "Connect to the live Supabase DB via `psycopg`; read-only.") The connection authenticates with the Supabase project's `service_role` JWT, not `anon`. Service role bypasses RLS, ensuring the validator sees every row in `nodes` and `edges` regardless of RLS policy.

**Rationale.** Both [`product/seed-graph/migrations/0002_nodes.sql:81-86`](../../product/seed-graph/migrations/0002_nodes.sql) and [`product/seed-graph/migrations/0003_edges.sql:67-72`](../../product/seed-graph/migrations/0003_edges.sql) enable RLS with `read-allowed-to-authenticated` policies (`USING (true)`), so authenticated would also see all rows in practice. Service role is the safer choice because (a) the validator's claim is "audit the database against ADR 0016" — the validator's correctness depends on observing ground truth, not policy-filtered truth, and (b) downstream RLS policy changes (e.g., a future "hide deprecated nodes from learner-facing queries" policy) must not silently degrade the validator. Service role makes the validator's observation surface contract-stable. The connection string is sourced from environment (recommended pattern: `SUPABASE_DB_URL` with the service-role connection string, distinct from the anon key).

**Artifact.** S-0035 implements the psycopg connection in `validate_graph()` per the stub's contract docstring at [`engine/tools/validate.py:1249-1293`](../tools/validate.py). Connection-string env-var name and any `.env.example` update are session-internal authoring details for S-0035; the gate commits the role choice and the library choice, not the env-var spelling.

## Tier 2 decisions

Concrete answers S-0035 implements without re-deciding. Each carries its source citation.

### T2-A — Cycle-detection algorithm: SCC via Kosaraju, restricted to prerequisite-edge subgraph

```
Algorithm: Kosaraju strongly connected components.
Input: prerequisite-edge subgraph only — edges WHERE edge_type = 'pedagogical_prerequisite'.
Output: any SCC of size > 1 is a cycle; report each cycle's node-id list.
Hard-fail: exit 2 if any prerequisite cycle is detected.
```

The prerequisite-only restriction is load-bearing. Other edge types (`historical_influence`, etc.) are display features per [`product/docs/architecture.md:182`](../../product/docs/architecture.md) and may legitimately form cycles (mutual influence between two thinkers' concepts is not a structural error). Only the prerequisite subgraph is required to be a DAG per [`product/docs/architecture.md:81`](../../product/docs/architecture.md): "the recursion terminates because the graph is a DAG — a cycle in the prerequisite graph is always a bug, and the computation hanging is a useful structural integrity check."

**Citations.** Algorithm choice: [`engine/tools/validate.py:1262`](../tools/validate.py) ("detect via SCC/Kosaraju") + [`build_plan/P_2_graph_validation.md:22`](../../build_plan/P_2_graph_validation.md) ("Cycles in prerequisite-edge subgraph (SCC detection via Kosaraju)"). DAG invariant: [`product/docs/architecture.md:81`](../../product/docs/architecture.md). Subgraph restriction: [`product/docs/architecture.md:182`](../../product/docs/architecture.md).

### T2-B — Sub-signal NULL permissiveness: out of `validate_graph()` scope

The S-0028 forward-pointer ([STATE.md L31](../STATE.md), [`engine/build_readiness/phase_3_sql.md:86-105`](phase_3_sql.md) T2-B) asks whether `validate_graph()` should enforce sub-signal NULL discipline.

**Decision.** Out of scope. `validate_graph()` operates on `nodes` and `edges` only per [`engine/adr/0016-graph-construction-needs-live-validation.md:9-19`](../adr/0016-graph-construction-needs-live-validation.md). The sub-signal NULL constraint lives on `learner_events` ([`engine/build_readiness/phase_3_sql.md:97-104`](phase_3_sql.md) `sub_signals_range_or_null` CHECK) and is enforced by Postgres at insert time — the constraint cannot be violated post-insert without a manual `UPDATE` bypassing the CHECK. There is no defensible scenario where `validate_graph()` would observe a violation that the SQL CHECK constraint did not already block.

**Citations.** Scope: [`engine/adr/0016-graph-construction-needs-live-validation.md:9-19`](../adr/0016-graph-construction-needs-live-validation.md) (Decision and Context name nodes/edges; learner_events absent from the contract). Existing enforcement: [`engine/build_readiness/phase_3_sql.md:97-104`](phase_3_sql.md) (CHECK constraint). Forward-pointer source: [STATE.md L31](../STATE.md).

If the project later wants `learner_events` audited as defense-in-depth (e.g., post-restore validation, drift-detection across CHECK constraint changes), that is a new contract surface — a separate `validate_learner_events()` function or a renamed `validate_database()` umbrella, with its own ADR. S-0035 does not author that surface; the existing forward-pointer is closed by this scope decision.

### T2-C — Hard-fail enumeration

Three categories, exactly the ADR 0016 contract. Each is hard-fail (exit 2):

1. **Duplicate node IDs.** Query: `SELECT id, COUNT(*) FROM public.nodes GROUP BY id HAVING COUNT(*) > 1`. Report each duplicate id. Cited: [`engine/adr/0016-graph-construction-needs-live-validation.md:11`](../adr/0016-graph-construction-needs-live-validation.md), [`build_plan/P_2_graph_validation.md:20`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1260`](../tools/validate.py).
2. **Dangling edge references.** Query: `SELECT id, source_id, target_id FROM public.edges WHERE source_id NOT IN (SELECT id FROM public.nodes) OR target_id NOT IN (SELECT id FROM public.nodes)`. Cited: [`engine/adr/0016-graph-construction-needs-live-validation.md:11`](../adr/0016-graph-construction-needs-live-validation.md), [`build_plan/P_2_graph_validation.md:21`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1261`](../tools/validate.py). (Note: the schema FK constraint at [`product/seed-graph/migrations/0003_edges.sql:52-53`](../../product/seed-graph/migrations/0003_edges.sql) prevents inserts of dangling refs, but the validator runs the check anyway as defense-in-depth — covers any post-restore window before constraints are validated.)
3. **Cycles in prerequisite-edge subgraph.** Per T2-A above.

### T2-D — Soft-warn enumeration (seven categories)

Exactly the seven categories named in [`engine/tools/validate.py:1265-1278`](../tools/validate.py) and confirmed in [`engine/operations/tools-validate-interpretation.md:90-96`](../operations/tools-validate-interpretation.md). Each category cited from its source document:

| Category | Definition | Source citation |
|---|---|---|
| `undeclared_predicate` | `edges.edge_type` not in PREDICATE_MANIFEST.md v1 registry. | [`engine/adr/0016-graph-construction-needs-live-validation.md:13`](../adr/0016-graph-construction-needs-live-validation.md), [`build_plan/P_2_graph_validation.md:28`](../../build_plan/P_2_graph_validation.md) |
| `attribute_shape_inconsistency` | Same-domain nodes with materially different attribute coverage (e.g., one ethics node has `teaching_notes` populated, another doesn't). Concrete v1 metric: a domain-tag's nodes split >70/30 on `teaching_notes` populated-vs-NULL is a shape inconsistency signal. | [`build_plan/P_2_graph_validation.md:29`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1266-1267`](../tools/validate.py) |
| `missing_rigor_score` | `rigor_score_computed` is at the column default (0.5) when topology data is sufficient to compute (i.e., the node has prerequisite edges and the formula at [`product/docs/architecture.md:69-77`](../../product/docs/architecture.md) would produce a non-default value). | [`build_plan/P_2_graph_validation.md:30`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1268-1269`](../tools/validate.py), [`product/docs/architecture.md:69-77`](../../product/docs/architecture.md) |
| `render_readiness_violation` | `nodes.label` contains scaffolding tokens — `service_node`, `synthetic`, `stub`. The forbidden-token list is the ADR 0027 enumeration as P_2 names it. | [`build_plan/P_2_graph_validation.md:31`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1270-1271`](../tools/validate.py) |
| `synthetic_review_queue` | `nodes.confidence_level = 'SYNTHETIC'` flagged; not a defect, populates the Opus batch review consumer per [`product/docs/self-correction.md:69-76`](../../product/docs/self-correction.md). | [`product/docs/self-correction.md:69-76`](../../product/docs/self-correction.md), [`product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md`](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md), [`engine/tools/validate.py:1272-1273`](../tools/validate.py) |
| `orphan_leaf` | Zero inbound + zero outbound prerequisite-type edges (other edge types do not count toward in/out degree for this category). | [`engine/adr/0016-graph-construction-needs-live-validation.md:13`](../adr/0016-graph-construction-needs-live-validation.md), [`build_plan/P_2_graph_validation.md:25`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1274-1275`](../tools/validate.py) |
| `suspicious_cross_domain_ratio` | A subdomain (single domain tag) where >40% of inbound prerequisite edges originate from nodes carrying no overlap with that domain tag. Cross-domain = `source.domain[]` and `target.domain[]` have empty array intersection. | [`build_plan/P_2_graph_validation.md:27`](../../build_plan/P_2_graph_validation.md), [`engine/tools/validate.py:1276-1278`](../tools/validate.py) |

The seven categories are exhaustive for v1; new categories are an ADR 0016 supersession event (per the ADR's own Consequences at [`engine/adr/0016-graph-construction-needs-live-validation.md:29`](../adr/0016-graph-construction-needs-live-validation.md)).

### T2-E — Soft-warn output format: per-category counts in ValidationResult

Each soft-warn fires through `ValidationResult.soft_warn(category, message)` where `category` is one of the seven enum-like strings above and `message` carries the row-specific detail (e.g., `"orphan_leaf: node_id='thucydides_history_method'"`). The validator's existing telemetry pipeline ([`engine/tools/validate.py:1304+`](../tools/validate.py) `session_id_from_current` + `validate-history.jsonl` writer) consumes per-category counts and feeds them into `outcome_summary_soft_warns` at session close per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md).

S-0035 adds the seven new keys to the `outcome_summary_soft_warns` block schema in [`engine/operations/session-shutdown-sequence.md:144-156`](../operations/session-shutdown-sequence.md). All seven keys appear in every archive even with zero counts (per the documented "absent keys signal 'this category did not exist at this session's close'" convention at [`engine/operations/session-shutdown-sequence.md:158`](../operations/session-shutdown-sequence.md)).

**Citations.** Output format: [`engine/tools/validate.py:1264`](../tools/validate.py) ("printed to stderr, counted, logged to JSONL"). Telemetry: [`engine/operations/tools-validate-interpretation.md:112-116`](../operations/tools-validate-interpretation.md). Schema: [`engine/operations/session-shutdown-sequence.md:144-156`](../operations/session-shutdown-sequence.md).

### T2-F — `--export-snapshot` mode is implemented in S-0035

The mode is named in the contract at [`engine/tools/validate.py:1282-1285`](../tools/validate.py) and in [`build_plan/P_2_graph_validation.md:36`](../../build_plan/P_2_graph_validation.md). Output shape: a single JSON file with two top-level keys, `nodes` (array of node row dicts) and `edges` (array of edge row dicts). No row filtering; this is a full snapshot for offline review. Mode is opt-in via CLI flag `--export-snapshot <path>`; default invocation runs `--validate-only`.

**Citations.** Mode definition: [`engine/tools/validate.py:1282-1285`](../tools/validate.py), [`build_plan/P_2_graph_validation.md:35-36`](../../build_plan/P_2_graph_validation.md). Snapshot shape: derived from the row schemas at [`product/seed-graph/migrations/0002_nodes.sql:60-79`](../../product/seed-graph/migrations/0002_nodes.sql) and [`product/seed-graph/migrations/0003_edges.sql:50-65`](../../product/seed-graph/migrations/0003_edges.sql).

### T2-G — PREDICATE_MANIFEST.md v1 registry contents

The v1 registry table replaces [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:21-23`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md):

| Predicate | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `pedagogical_prerequisite` | `nodes` | `nodes` | many-to-many | Source node is a prerequisite for understanding target node. The structural edge type used in traversal, syllabus generation, and mastery computation per [`product/docs/architecture.md:182`](../../product/docs/architecture.md). Default for new edges per [`product/seed-graph/migrations/0003_edges.sql:54`](../../product/seed-graph/migrations/0003_edges.sql). |
| `historical_influence` | `nodes` | `nodes` | many-to-many | Source concept historically influenced target concept's development. Display-only (Discovery surface annotation) per [`product/docs/architecture.md:182`](../../product/docs/architecture.md); not consumed by traversal or mastery computation. |

The placeholder prose at [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:19`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) ("Empty until Phase 4. The first entries land when Phase 5's epistemology session ships the first seed migration.") is replaced by a one-line "v1 registry authored at S-0035 per Phase 4 build-readiness gate." Future Phase 5 additions follow the same-session ENGINE_LOG-tracked discipline at [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:9-13`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md).

**Citations.** Predicate sources: [`product/docs/architecture.md:182`](../../product/docs/architecture.md), [`product/seed-graph/migrations/0003_edges.sql:54`](../../product/seed-graph/migrations/0003_edges.sql). Authoring discipline: [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:9-13`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md).

### T2-H — ROUTING.md range-collision fix

The current ROUTING.md prefix scheme has a range collision: [`product/seed-graph/migrations/ROUTING.md:12`](../../product/seed-graph/migrations/ROUTING.md) assigns `0010-0019` to "Seed metadata (graph_version=1, ontology metadata) — Phase 4" while [`product/seed-graph/migrations/ROUTING.md:13`](../../product/seed-graph/migrations/ROUTING.md) assigns `0011-0019` to "Seed: epistemology — Phase 5." The same range serves two purposes.

**Decision.** S-0035 amends the table to: `0010` reserved for Phase 4 metadata (single slot — there's at most one Phase 4 metadata migration); `0011-0019` reserved for Phase 5 epistemology; remaining ranges unchanged. The amendment is a one-line table edit.

**Citations.** Collision: [`product/seed-graph/migrations/ROUTING.md:11-13`](../../product/seed-graph/migrations/ROUTING.md). Phase 4 metadata scope (singular): [`build_plan/P_2_graph_validation.md:42`](../../build_plan/P_2_graph_validation.md) (no metadata migration is named; Phase 4 deliverables are the validator extension + three docs, none of which is a SQL migration). Reserving `0010` keeps the slot available without committing Phase 4 to author one.

### T2-I — Stale path corrections in tools-validate-interpretation.md and ADR 0016

Two stale-path drifts surfaced during gate authoring; both reference `supabase/migrations/PREDICATE_MANIFEST.md` instead of the post-S-0027 path `product/seed-graph/migrations/PREDICATE_MANIFEST.md`:

- [`engine/operations/tools-validate-interpretation.md:90`](../operations/tools-validate-interpretation.md) — `undeclared_predicate` description.
- [`engine/adr/0016-graph-construction-needs-live-validation.md:38`](../adr/0016-graph-construction-needs-live-validation.md) — See also section.

**Decision.** S-0035 corrects both paths in passing. The validate.py docstring at [`engine/tools/validate.py:1265`](../tools/validate.py) does not name a path (it just says "PREDICATE_MANIFEST.md") — leave as-is.

**Citations.** Drift sources: cited above. Resolution path: in-passing fix during S-0035 authoring; no new ADR.

The ADR 0016 path correction is a Status-preserving content edit (the ADR remains Accepted; the path was correct at authoring date 2026-04-29 per [`engine/adr/0016-graph-construction-needs-live-validation.md:4`](../adr/0016-graph-construction-needs-live-validation.md), pre-S-0024 partition). ENGINE_LOG entry under `Changed`.

## Tier 3 forward pointers

Decisions explicitly deferred. Each names the deferral and where it's marked.

### T3-A — Branch-based rollback verification (S-0028 forward-pointer)

**Deferral.** Phase 5+ pending local Supabase CLI setup or explicit user budget approval for development branches.

The S-0028 forward-pointer ([STATE.md L31](../STATE.md), [`product/seed-graph/migrations/ROUTING.md:69`](../../product/seed-graph/migrations/ROUTING.md), [`engine/build_readiness/phase_3_sql.md:233`](phase_3_sql.md) T3-G context) asks whether Phase 4 should commit to branch-based rollback verification. Cost-gating is explicit: Supabase development branches have associated costs, and S-0028's auto-mode posture defers cost-bearing operations to explicit user confirmation.

**Decision in S-0034.** Phase 4's `validate_graph()` is read-only ([`build_plan/P_2_graph_validation.md:38`](../../build_plan/P_2_graph_validation.md), [`engine/adr/0016-graph-construction-needs-live-validation.md:25`](../adr/0016-graph-construction-needs-live-validation.md), [`engine/tools/validate.py:1287`](../tools/validate.py): "No write-back path. DB writes happen via Supabase migrations only.") and does not mutate the database, so rollback verification is not in scope for the validator itself. The forward-pointer carries forward to Phase 5+ migration discipline; the gate session for the first Phase 5 migration is the right surface to revisit. Recorded here so the next gate session inherits the open question.

### T3-B — `architecture.md` status-enum prose drift (2 values vs 3 values)

**Deferral.** Documentation-cleanup task for a future architecture.md sweep session.

[`product/docs/architecture.md:140`](../../product/docs/architecture.md) names `status ('active' | 'deprecated')` (two values). The migration at [`product/seed-graph/migrations/0002_nodes.sql:73-74`](../../product/seed-graph/migrations/0002_nodes.sql) enforces the 3-value enum `(active, deprecated, superseded)` per phase_3_sql.md T2-A. The migration's own comment block at [`product/seed-graph/migrations/0002_nodes.sql:21-26`](../../product/seed-graph/migrations/0002_nodes.sql) explains the expansion. The drift does not affect `validate_graph()` (the validator doesn't enforce the enum — that's the SQL CHECK's job; the validator queries the live DB which carries the 3-value enum). Cleanup belongs to a future architecture.md edit pass, not Phase 4.

**Marked at.** This Tier 3 entry; no other surface tracks it. Future architecture.md editor reads this report and addresses inline.

### T3-C — `attribute_shape_inconsistency` v1 metric calibration

**Deferral.** Phase 5+ — the >70/30 split metric proposed in T2-D is a starting point; the right threshold depends on observed seed-graph distribution which Phase 5 produces.

Phase 4's validator implementation uses the proposed metric. If Phase 5 seed authoring shows the metric fires too aggressively or too rarely, the metric is amended in a follow-up session (a P_2-style refinement, not an ADR 0016 supersession — the *category* is contract-stable; the *threshold* is a tuning parameter).

**Marked at.** This Tier 3 entry; future Phase 5 gate session inherits the question via STATE.md's next-session work item if seed-authoring telemetry warrants.

### T3-D — `seed-chunked-authoring.md` stale `supabase/migrations/` paths

**Deferral.** Address in S-0035 sub-deliverable 4.4 (Phase 4 fleshes out `seed-chunked-authoring.md` per [`build_plan/P_2_graph_validation.md:48-50`](../../build_plan/P_2_graph_validation.md)).

[`engine/operations/seed-chunked-authoring.md`](../operations/seed-chunked-authoring.md) currently uses `supabase/migrations/` paths (pre-S-0024 partition). Sub-deliverable 4.4 rewrites the workflow doc — the rewrite naturally corrects the paths. This isn't a separate Tier 2 fix; it's already in scope for S-0035 work.

**Marked at.** P_2 sub-deliverable 4.4; this entry is a reminder so S-0035 doesn't author the rewrite while preserving stale paths.

## Success criteria for S-0035

Inherits from [`build_plan/P_2_graph_validation.md:52-59`](../../build_plan/P_2_graph_validation.md) plus session-specific verifications surfaced by the gate exercise:

**P_2 inherited:**
- `engine/tools/validate.py --validate-only` runs end-to-end against the live `paideia-dev` DB in <3s on the schema-only state (no Phase 5 content yet — empty nodes/edges).
- A new (test) predicate not in `PREDICATE_MANIFEST.md` surfaces as `undeclared_predicate` soft-warn (smoke-test).
- A deliberately-broken edge ref (test fixture) triggers `dangling_edge` hard-fail with exit 2.
- Pre-commit hook blocks seed-authoring commits that fail audit (smoke-test against a deliberate hard-fail).
- `engine/tools/validate.py` clean against the schema-only state at session start (no Phase 5 content).
- ENGINE_LOG entry under `[Unreleased]` for `Added` (PREDICATE_MANIFEST v1 registry, ROUTING.md S-0035 narrative entry, fleshed seed-chunked-authoring.md) and `Changed` (validate.py extension, tools-validate-interpretation.md path correction, ADR 0016 path correction).

**S-0034 gate-specific:**
- Every Tier 2 decision in this report is implemented exactly as documented. The build session does not re-decide.
- The cold-review pass at S-0035 shutdown reports per-file matches against contract blocks; no premise drift surfaced.
- T2-G's PREDICATE_MANIFEST.md v1 registry is authored verbatim from this report (two predicates, the table column shape preserved).
- T2-H's ROUTING.md range-collision fix lands as a single-line table edit; rollback verification narrative for S-0035 itself appears in ROUTING.md per the per-session-narrative discipline.
- T2-I's stale-path corrections land in the same commit as the validator extension (or in a small grouped fix-commit); both paths point at `product/seed-graph/migrations/PREDICATE_MANIFEST.md`.
- The seven new soft-warn keys (`undeclared_predicate`, `attribute_shape_inconsistency`, `missing_rigor_score`, `render_readiness_violation`, `synthetic_review_queue`, `orphan_leaf`, `suspicious_cross_domain_ratio`) appear in S-0035's `outcome_summary_soft_warns` block (zero or non-zero counts).
- STATE.md next-session work-item points at S-0036 (or first Phase 5 chunk per ROADMAP).

**Forward-pointer status at S-0035 close:**
- T3-A (branch-based rollback): unchanged — still pending, reaffirmed in S-0035's `outcome_summary` for inheritance by the next gate session.
- T3-B (architecture.md status enum prose): unchanged — still pending; future architecture.md sweep session.
- T3-C (attribute_shape_inconsistency metric): metric is in code; calibration awaits Phase 5 seed-graph distribution.
- T3-D (seed-chunked-authoring.md stale paths): closed by S-0035 sub-deliverable 4.4 rewrite.

## Authored resolution artifacts (in S-0034)

Gate session deliverables (this is the only file the gate authors; S-0035 implements per the report):

- This file ([`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md)).
- [`engine/build_readiness/README.md`](README.md) — index updated to add the S-0034 → S-0035 row.
- `engine/STATE.md` — last-session row updated to S-0034; next-session work-item points at S-0035 with the gate-pointer line per [`engine/operations/build-readiness-gate.md:118`](../operations/build-readiness-gate.md) step 9.
- `engine/ENGINE_LOG.md` `[Unreleased]` — Added entry for the gate report.

No new ADRs. No sibling Layer 1 documents authored at this gate (PREDICATE_MANIFEST.md and ROUTING.md edits land in S-0035 per T2-G/T2-H, not in this gate). The `expression-contract-instantiation.md` table is unchanged — Phase 4 authors Python under engine/ which already has its row; no new authoring pattern is introduced.

## See also

- [`build_plan/P_2_graph_validation.md`](../../build_plan/P_2_graph_validation.md) — the chunk being prepared.
- [`engine/adr/0016-graph-construction-needs-live-validation.md`](../adr/0016-graph-construction-needs-live-validation.md) — the load-bearing contract S-0035 implements against.
- [`product/docs/architecture.md`](../../product/docs/architecture.md) — graph schema (nodes, edges, JSONB shapes); the design-source any T2 schema-shape decision cites per ADR 0040 amendment.
- [`product/docs/self-correction.md`](../../product/docs/self-correction.md) — Phase 4 graph self-correction; downstream consumer of `synthetic_review_queue` soft-warn.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the gate protocol this report executes (gate-on-the-gate citation + cold-review).
- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn telemetry consumed by the seven new categories.
- [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) — gate procedure operational doc.
- [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md) — Phase 5+ migration discipline that consumes the validator.
- [`engine/build_readiness/phase_3_sql.md`](phase_3_sql.md) — prior gate report; T2-B sub-signal CHECK and T3-G validate_graph stub references inherited.
