# ADR 0016 — Graph construction needs live validation

- **Status:** Accepted
- **Date:** 2026-04-29
- **Deciders:** S-0001 plan conversation; formalized in S-0003

## Context

The seed graph is authored across many chunked sessions (per `docs/operations/seed-chunked-authoring.md`, Phase 5 — six subdomain sessions plus a service-nodes session plus a cross-domain edges pass). Each session writes a migration with INSERT statements. Without live validation, structural mistakes accumulate silently across sessions: a duplicate node ID introduced in session N is undetectable until session N+5 tries to author a downstream edge that depends on the duplicated node and fails confusingly.

Three failure classes are catastrophic enough to be **hard-blocking** during authoring: (1) duplicate node IDs, (2) dangling edge references (source or target not in nodes), (3) cycles in the prerequisite-edge subgraph (which would make topological sort undefined). These cannot be left to discover at query time; they break the contract the rest of the system depends on.

Several other failure classes are **signal**, not blockers: orphan leaves, missing summaries, undeclared predicates (edge.type not in the canonical manifest), suspicious cross-domain ratios, render-readiness violations (scaffolding tokens leaking into labels), `confidence_level: SYNTHETIC` nodes flagged for review. Each indicates either drift across sessions or a granularity choice worth examining.

Per-session authoring also needs **pre-commit gating**: the pre-commit hook must run the validator and reject hard-fails. Otherwise an authoring session can commit broken state, and the next session inherits it.

## Decision

Graph construction is **gated by a live validation utility** (`tools/validate.py`'s `validate_graph()` extension point) that runs against the live Supabase DB after each session's `supabase db push`. The utility is wired to the pre-commit hook so seed-authoring sessions cannot commit without passing audit. Hard-fails (duplicate node IDs, dangling edges, prerequisite cycles) exit `2` and block the commit. Soft-warns (orphan leaves, undeclared predicates, attribute-shape inconsistency, missing rigor scores, render-readiness violations, synthetic review queue, suspicious cross-domain ratios) exit `1`, are categorized, and are recorded in `session/current.json`'s `outcome_summary` at session close.

## Consequences

- [`engine/tools/validate.py`](../tools/validate.py) carries the live `validate_graph()` implementation. The function connects to the live Supabase DB via `psycopg` (lazy import; service-role connection string consumed from `SUPABASE_DB_URL`), runs the listed hard-fail and soft-warn checks, and returns a `ValidationResult` with categorized findings. Runtime budget: <3s on the schema-only state.
- When `SUPABASE_DB_URL` is unset in the environment, the audit records `graph_audit_skipped` and runs no DB query — non-seed-authoring sessions are not gated on connectivity. Phase 5+ seed-authoring sessions set the env var; the audit-skip path is an escape hatch for engine-only sessions.
- Modes: `--validate-only` (default; read-only DB queries; categorical counts; exit 0/1/2) and `--export-snapshot path/to/snapshot.json` (write current-state snapshot for offline review). No write-back path — DB writes happen via Supabase migrations only.
- Soft-warn categories feed health-check trend analysis (per ADR 0022). The `tools/validate-history.jsonl` telemetry log captures per-category counts per invocation; recurring health checks consume the trend data.
- The seed-chunked-authoring workflow (per `docs/operations/seed-chunked-authoring.md`) includes the validate step explicitly: read SEP article → identify concepts at the granularity principle → write migration → `supabase db push` → `tools/validate.py` → fix in-session → commit.
- The `PREDICATE_MANIFEST.md` (Phase 4) becomes the canonical edge-type registry; adding a new predicate is an ENGINE_LOG-tracked material change requiring a manifest entry in the same session. The validator detects undeclared predicates via this manifest.
- This ADR is the contract the Phase 4 implementation must honor. Changes to the contract (adding a hard-fail category, removing a soft-warn) require Status: Superseded plus the Phase 4 code update.

## See also

- [`tools/validate.py`](../tools/validate.py) — `validate_graph()` extension point; ADR 0016 cited inline.
- [`docs/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) — exit codes, hard-fail vs soft-warn responses.
- [`docs/operations/seed-chunked-authoring.md`](../operations/seed-chunked-authoring.md) — per-session authoring workflow (Phase 4 placeholder, fleshed at Phase 4).
- [`ROADMAP.md`](../../ROADMAP.md) — Phase 4 success criteria.
- ADR 0022 — Periodic project health checks (consumes validate-history telemetry).
- `product/seed-graph/migrations/PREDICATE_MANIFEST.md` — canonical edge-type registry; v1 authored at S-0037 per [`engine/build_readiness/phase_4_graph_validation.md`](../build_readiness/phase_4_graph_validation.md) T2-G.
