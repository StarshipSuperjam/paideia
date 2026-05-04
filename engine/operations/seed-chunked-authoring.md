# Seed chunked authoring

> Per-session migration workflow for Phase 5 seed-graph build. Each session authors one subdomain's seed migration: a chunked, atomic addition of nodes and edges to the live graph. Sessions run in parallel without merge conflicts because each writes a distinct migration file under [`product/seed-graph/migrations/`](../../product/seed-graph/migrations/).
>
> Layer 1 source-of-truth for Phase 5 chunked authoring per [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Authoring discipline (the per-migration contract block, transaction wrap, CASCADE on user FKs, RLS-enable, CHECK on enum-modeled TEXT columns) lives at [`migration-discipline.md`](migration-discipline.md); this document layers the *graph-content* discipline on top of it (the granularity principle, predicate registration, validator interaction, ENGINE_LOG handshake).

## Per-session workflow

The full sequence from session boot to commit. Each step is mandatory; the validator enforces step 6 mechanically and the audit enforces step 9 mechanically — the rest is authoring discipline.

1. **Read the target subdomain's source structure.** SEP article tables of contents are the structural reference per [ADR 0011](../../product/adr/0011-no-hosted-copyrighted-material.md). The session's job is to identify in-scope concepts at the granularity principle (one mastery state per concept; per `product/docs/architecture.md` "Granularity Principle"). Where the [Phase 4.5 dataset survey](../../product/docs/content-strategy.md) flags an applicable inventory or prerequisite-shaped graph prior, consult it as a checklist. Specific dataset-adoption decisions land as ADRs in-session if they involve non-trivial tradeoffs.

2. **Read the current `settings.graph_version`.** Per [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) "graph_version increment contract": at session boot (after slot claim, before authoring), read the value. The session's increment lands in step 4's INSERT statements.

3. **Pick the next migration file slot.** Per the [ROUTING.md numeric prefix scheme](../../product/seed-graph/migrations/ROUTING.md). A new subdomain claims the next available range; gaps are acceptable. File name follows `00NN_seed_<subdomain>_partN.sql` — for example, `0011_seed_epistemology_part1.sql`. Compound-domain concepts (a philosophy-of-science concept that's also epistemology) write to the higher-precedence subdomain's file with `domain[]` carrying both tags; do not split across two files.

4. **Author the migration file.** The contract block at the top follows [`migration-discipline.md`](migration-discipline.md) Layer 1 (Purpose, Loads tables, Preconditions, Postconditions, Invariants, Non-responsibilities, Cross-cutting decisions, Rollback, See also). The body is wrapped in `BEGIN; ... COMMIT;` per [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Each `INSERT` sets:

   - `graph_version_added = <current + 1>` (the value read in step 2 incremented by one; use the same value across every INSERT in this session)
   - `confidence_level` per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) — `EXTRACTED`, `INTERPRETED`, or `SYNTHETIC`
   - `domain[]` carrying every applicable subdomain tag (cross-domain concepts carry every tag they belong to)
   - `confidence_level: SYNTHETIC` flags the node for the Opus batch review queue ([self-correction.md](../../product/docs/self-correction.md), [ADR 0014](../../product/adr/0014-sonnet-teaches-opus-reviews.md)); use sparingly and document the authoring evidence in `teaching_notes`

5. **Register any new edge predicates.** If the migration uses an `edge_type` not already in [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md)'s "Predicate registry" table, add the row in the same session, paired with an ENGINE_LOG entry under `Added` per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md). Reserved-but-unused entries (the manifest's second table) require promotion to the registry before they may be inserted.

6. **`supabase db push`.** Applies the migration to the live `paideia-dev` DB. Connectivity assumed via the Supabase MCP server configured in `.mcp.json` (gitignored, per-clone) or via the CLI's `SUPABASE_*` env vars.

7. **`SUPABASE_DB_URL=<service-role-pooler-url> python3 engine/tools/validate.py`.** Runs the audit per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md). The service-role URL is required for ground-truth observation (gate T1-C); see [`.env.example`](../../.env.example) for the format. Three hard-fails block the commit (duplicate node IDs, dangling edge references, prerequisite cycles via Kosaraju SCC); seven soft-warns are advisory (recorded in `outcome_summary_soft_warns` at session shutdown — see [`session-shutdown-sequence.md`](session-shutdown-sequence.md)).

8. **Hard-fails: fix in-session before commit.** Per [`tools-validate-interpretation.md`](tools-validate-interpretation.md) "Hard-fails (always blocking)". The pre-commit hook rejects any commit with hard-fails; do not bypass with `--no-verify`. The fix is usually obvious (a typo in `source_id`, a duplicate `id` from an earlier draft, an accidental cyclic dependency); for non-obvious cases see [`escalation-criteria.md`](escalation-criteria.md).

9. **Soft-warns: record in `outcome_summary_soft_warns` at session close.** Per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). The seven Phase-4-specific categories (`undeclared_predicate`, `attribute_shape_inconsistency`, `missing_rigor_score`, `render_readiness_violation`, `synthetic_review_queue`, `orphan_leaf`, `suspicious_cross_domain_ratio`) appear in every Phase 5+ session's archive with zero or non-zero counts. Persistent firings (3-of-5 sessions) surface at the next boot; 10-session persistence reaches the escalation criterion.

10. **Commit.** Conventional commit `feat(seed): seed <subdomain> part N — <node count> nodes, <edge count> edges`. ENGINE_LOG entry under `Added` records the subdomain and counts. Push per the standard session-shutdown sequence ([`session-shutdown-sequence.md`](session-shutdown-sequence.md)).

## Validator skip behavior

When `SUPABASE_DB_URL` is unset, the validator records `graph_audit_skipped` in `checks_run` and does not query the DB — non-seed-authoring sessions are not gated on DB connectivity. Phase 5 sessions **must** set the env var for the workflow to engage; the audit-skip path is an escape hatch for engine-only sessions, not for seed authoring.

### One-time setup of `SUPABASE_DB_URL`

Per Issue #7 / S-0048: run `python3 engine/tools/setup_env.py` once on a fresh clone. The helper reads `.env.example` to discover canonical keys, prompts only for missing/empty values, validates `SUPABASE_DB_URL` with a real `psycopg.connect()` + `SELECT version()`, and writes `.env` atomically with 0600 permissions. The DB password is dashboard-only by Supabase's design (not retrievable via MCP, REST, or CLI); get it from `https://supabase.com/dashboard/project/<project-ref>/settings/database` ("Connection string" section — Direct connection or Session pooler tab both work) and paste when prompted. Reset the database password first if the dashboard shows it as `[YOUR-PASSWORD]`.

After this one-time setup, `.env` is gitignored and persists. Subsequent routine fires read it automatically — no per-session prompting. The `engine/tools/hooks/session-start.sh` boot hook emits a LOUD pointer at every boot when `auto_target.json` is present and `SUPABASE_DB_URL` is missing from `.env`, so the gap is impossible to miss.

## Snapshot mode

`python3 engine/tools/validate.py --export-snapshot path/to/snapshot.json` writes a full nodes-and-edges JSON dump for offline review. Useful for cold-context review at session shutdown (per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) Step 8 — sub-agent reads the snapshot against the contract block). Snapshot mode skips the validation checks; run `--validate-only` (default) for the audit, then `--export-snapshot` separately if a snapshot is wanted.

## Parallel sessions and the eager-claim discipline

Phase 5 is the first natural parallel-work moment per ROADMAP. Two subdomain sessions (epistemology + ethics) running concurrently do not collide: each claims its own session slot via the eager-claim ritual ([`session-build-lifecycle.md`](session-build-lifecycle.md)), each writes a distinct migration file (per the ROUTING.md range scheme), and each `supabase db push` is atomic at the SQL level. The `graph_version` counter is monotonically advanced per session via the increment contract, so cross-session inserts carry distinct `graph_version_added` values even when they land within minutes of each other.

Cross-session schema drift (e.g., an inadvertent predicate variant introduced in session A and a different variant in session B) is detected post-merge by the next validator run. Each session's commit must pass the audit at its own shutdown; the next session's boot validator catches drift that emerges only when the two sessions' outputs are merged.

## What the validator does and does not catch

The audit catches structural integrity — schema-shaped failures that would degrade query correctness. It does **not** catch pedagogical-quality failures: an inverted prerequisite ordering ("Kant's transcendental idealism" listed as a prerequisite for "concept of a category" rather than the other way around) is a content-judgment error invisible to the validator. The session author is responsible for pedagogical-quality review at the granularity principle. Soft-warns surface signals that *might* indicate quality issues (e.g., `suspicious_cross_domain_ratio` suggests a missing service node on the inside of the subdomain) but the call is the author's.

[ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s cold-review step at session close is the second layer: a sub-agent reads the migration cold against the contract block and the architecture.md schema, surfacing premise drift the author would not see in the moment of authoring.

## Worked example (Phase 5 epistemology session, S-0040 hypothetical)

Suppose S-0040 opens to author the first epistemology seed migration. The session:

- Reads the SEP article on epistemology, identifies ~25 in-scope concept names at the granularity principle (e.g., `epistemic_justification`, `gettier_problem`, `reliabilism`, `internalism`, `externalism`, ...). Cross-references the Phase 4.5 survey for prerequisite-shaped priors (none currently named for epistemology, so falls back to generative seeding).
- Reads `settings.graph_version = 1` (the post-Phase-3-init value).
- Picks `0011_seed_epistemology_part1.sql` as the next file (the first Phase 5 epistemology migration; `0010` is reserved for Phase 4 metadata, currently unused).
- Authors the file with a contract block, `BEGIN; ... COMMIT;` wrap, ~25 INSERT statements into `public.nodes` (each with `graph_version_added = 2`, `domain[] = '{epistemology}'`, `confidence_level = 'INTERPRETED'`), and a smaller number of `pedagogical_prerequisite` INSERTs into `public.edges`.
- Skips PREDICATE_MANIFEST.md update (only `pedagogical_prerequisite` used; already in the registry).
- Runs `supabase db push`. Postgres applies the migration in a single transaction.
- Runs `SUPABASE_DB_URL=... python3 engine/tools/validate.py`. The audit reports zero hard-fails plus a small `orphan_leaf` count (the leaf concepts are inevitable in a partial seed; resolved when downstream subdomains add edges that consume them) and a small `missing_rigor_score` count (the rigor formula expects topology data; 25 nodes are not enough).
- Records the soft-warn counts in `outcome_summary_soft_warns` at session close.
- Commits with `feat(seed): seed epistemology part 1 — 25 nodes, 38 edges` and an ENGINE_LOG entry under `Added`.

The session's commit lands cleanly because the structural checks pass; the soft-warns are advisory and the next session continues from this state.

## See also

- [`migration-discipline.md`](migration-discipline.md) — Layer 1 contract for SQL migrations the validator gates.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — exit codes, hard-fail vs soft-warn category meanings.
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure, eager-claim ritual.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — close procedure including `outcome_summary_soft_warns` shape.
- [`build-readiness-gate.md`](build-readiness-gate.md) — gate procedure for substantive build sessions; Phase 5 subdomain sessions read their gate report at boot.
- [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) — the load-bearing contract.
- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — universal expression contract; SQL/migrations row.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — build-readiness gate; cold-review step at shutdown.
- [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) — numeric prefix scheme, graph_version increment contract, per-session narrative.
- [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) — canonical edge-type registry.
- [`engine/tools/validate.py`](../tools/validate.py) — the validator implementation.
