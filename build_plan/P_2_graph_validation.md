# P_2 — Graph validation utility (Phase 4)

> Real-time graph validation extending `engine/tools/validate.py`'s `validate_graph()` extension point. Wired to the pre-commit hook so seed-authoring sessions cannot commit without passing audit.

## Phase scope

Phase 4 fleshes out the validation utility that Phase 5 seed-authoring sessions depend on. The validator runs against the live Supabase DB (`paideia-dev` per [`engine/STATE.md`](../engine/STATE.md) Infrastructure), reads the schema landed at [`P_1_sql_schema.md`](P_1_sql_schema.md), and emits hard-fails (block commit) and soft-warns by category (recorded in session `outcome_summary`).

Per [ADR 0016](../engine/adr/0016-graph-construction-needs-live-validation.md), graph construction needs live validation: schema-only checks at Phase 3 close are not enough; structural integrity at the graph level (cycles, dangling edges, undeclared predicates, attribute-shape inconsistency) requires runtime queries against actual data.

## Output

Four deliverables per [ROADMAP Phase 4](../ROADMAP.md):

### 4.1 Flesh out `engine/tools/validate.py`'s `validate_graph()`

Connect to the live Supabase DB via `psycopg`; read-only.

**Hard-fail (exit 2):**
- Duplicate node IDs.
- Dangling edge references (`source_id` or `target_id` not in `nodes`).
- Cycles in prerequisite-edge subgraph (SCC detection via Kosaraju).

**Soft-warn by category (printed to stderr; per-category counts):**
- Orphan leaves (zero outbound + zero inbound prerequisite edges).
- Missing `summary` or `teaching_notes`.
- Suspicious cross-domain edge ratios (e.g., epistemology subdomain with > 40% cross-domain inbound — likely a missing service node).
- `undeclared_predicate` — edge.type not in the canonical PREDICATE_MANIFEST.md.
- `attribute_shape_inconsistency` — nodes of same domain with materially different attribute coverage.
- Missing rigor score components (`rigor_score_computed` null when topology data is sufficient).
- Render-readiness violations (labels containing scaffolding tokens — `service_node`, `synthetic`, `stub` — per [ADR 0027](../product/adr/0027-rendering-policy-prompt-layer-contract.md)'s forbidden-token enumeration applied to node-label authoring).
- `confidence_level: SYNTHETIC` nodes flagged for review queue.

**Modes:**
- `--validate-only` (default) — read-only DB queries, per-category counts, exit 0/1/2.
- `--export-snapshot path/to/snapshot.json` — write current-state snapshot for offline review.

No write-back. DB writes happen via migrations only.

### 4.2 Flesh out `product/seed-graph/migrations/ROUTING.md`

Numeric prefix scheme: `00NN` schema, `001N` epistemology, `002N` ethics, `003N` metaphysics, `005N` service nodes, `006N` cross-domain edges. Per-session narrative paragraphs (~200–400 words each) documenting what each migration added and why.

### 4.3 Flesh out `product/seed-graph/migrations/PREDICATE_MANIFEST.md`

Canonical edge-type registry: `prerequisite`, `enables`, `informed_by`, `cross_domain_dependency`, etc. Adding a new predicate is an ENGINE_LOG-tracked material change requiring a new manifest entry in the same session.

### 4.4 Flesh out `engine/operations/seed-chunked-authoring.md`

Per-session migration workflow: read SEP article → identify concepts at granularity principle → write `00NN_seed_<subdomain>_partN.sql` migration → `supabase db push` → `engine/tools/validate.py` → fix in-session → commit. Replaces the current placeholder content in [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md).

## Success criteria

- `engine/tools/validate.py --validate-only` runs end-to-end against the live DB in < 3s on a 100-node test seed.
- A new predicate not in `PREDICATE_MANIFEST.md` surfaces as a soft-warn (`undeclared_predicate` category).
- A deliberately-broken edge ref triggers hard-fail with exit 2.
- Pre-commit hook blocks seed-authoring commits that fail audit (verify by attempting a commit with a deliberate hard-fail; commit must be blocked).
- `engine/tools/validate.py` clean against the schema-only state at session start (no Phase 5 content yet).
- ENGINE_LOG entry under `[Unreleased]` for `Added` (PREDICATE_MANIFEST, ROUTING, seed-chunked-authoring) and `Changed` (`validate.py` extension).

## Source documents (boot reads beyond CLAUDE.md auto-load)

- [`engine/STATE.md`](../engine/STATE.md), [`ROADMAP.md`](../ROADMAP.md) Phase 4.
- [`engine/tools/validate.py`](../engine/tools/validate.py) — current state including the `validate_graph()` stub.
- [`engine/operations/tools-validate-interpretation.md`](../engine/operations/tools-validate-interpretation.md) — soft-warn category meanings; new categories added in this session land here.
- [`engine/operations/seed-chunked-authoring.md`](../engine/operations/seed-chunked-authoring.md) — current placeholder.
- [`product/docs/architecture.md`](../product/docs/architecture.md) — node/edge schema (consumed in `P_1`; consulted again here for cross-domain ratio calibration).
- [`engine/adr/0016-graph-construction-needs-live-validation.md`](../engine/adr/0016-graph-construction-needs-live-validation.md) — the load-bearing ADR.
- [`product/adr/0027-rendering-policy-prompt-layer-contract.md`](../product/adr/0027-rendering-policy-prompt-layer-contract.md) — forbidden-token enumeration for the render-readiness check.

## Load-bearing ADRs

[ADR 0016](../engine/adr/0016-graph-construction-needs-live-validation.md), [ADR 0027](../product/adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0030](../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md).

## Estimated context budget

Substantive tier: target 60%, cap 70%. The work is implementing checks, naming categories, populating the predicate manifest. The `psycopg` integration plus the SCC detection algorithm are the substantive judgment moments; the rest is mechanical fill-in.

## Session sequencing

Single session if 4.1 alone fits the budget; otherwise split: Session 1 fleshes out 4.1 (the validator extension); Session 2 fills 4.2/4.3/4.4 (the manifests and the workflow doc). The validator extension is the load-bearing deliverable; the manifests can settle in a follow-up if budget pressure surfaces.

## Open tensions consumed

None directly. The validator may surface render-readiness or confidence-level edge cases that warrant new tension entries; if so, they file under `docs/tensions.md` per the [tension-resolution discipline](../engine/operations/session-shutdown-sequence.md).

## See also

- [`../ROADMAP.md`](../ROADMAP.md) Phase 4 — full phase scope.
- [`../adr/0016-graph-construction-needs-live-validation.md`](../engine/adr/0016-graph-construction-needs-live-validation.md) — load-bearing ADR.
- [`P_1_sql_schema.md`](P_1_sql_schema.md) — predecessor; schema this validator queries.
- [`P_4_seed_graph_build.md`](P_4_seed_graph_build.md) — successor; consumes this validator at every subdomain session.
