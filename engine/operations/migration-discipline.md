# Migration discipline — expression contract for AI-authored SQL migrations

> An expression contract is a tool that constrains how the AI expresses itself for a specific surface. This document is the Layer 1 source-of-truth for the SQL/migrations pattern row in [`expression-contract-instantiation.md`](expression-contract-instantiation.md), under [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Sibling to [`code-discipline.md`](code-discipline.md) (Python/engine pattern) and [`document-voice.md`](document-voice.md) (prose/inward pattern). The contracts are kindred tools, separately scoped.

## Posture

SQL migrations under `product/seed-graph/migrations/` are authored under three discipline layers that compose. The compound-drift mode [`code-discipline.md`](code-discipline.md) names is the named target here too — a wrong premise about Postgres CASCADE evaluation order, JSONB constraint behavior, RLS policy interaction with `auth.uid()`, or migration-application ordering built upon consistently across many migration lines, producing internally coherent SQL that passes ad-hoc inspection. The user cannot reliably audit migration semantics at scale; reading line-by-line does not reveal premise drift.

The schema is the substrate every downstream phase reads or writes to. A subtly-wrong constraint authored at Phase 3 (a missing CASCADE, a CHECK constraint that admits invalid enum values, an RLS policy that gates wrong rows) compounds across Phase 4 graph audit, Phase 5 seed authoring, Phase 6 self-correction, Phase 7 teaching layer. Compounding amplifies the cost of late detection; the discipline pays off when the schema lands clean.

The three layers compensate. **Layer 1** forces the auditable layer up into prose — the per-migration discipline checklist below, the migration's own contract comment block, and ADR-level decisions for cross-cutting choices (table relationships, RLS posture, cascade graph). **Layer 2** mechanizes the drift mechanization can catch — transaction wrap, FK CASCADE presence on learner-state references, RLS-enable on `public.*` tables, CHECK constraint shape on enum-modeled TEXT columns. **Layer 3** introduces fresh eyes — a sub-agent with no session context reads the diff against this contract and the migration's contract comment block at session shutdown.

## Layer 1 — Contract-first prose

Before non-trivial migration is authored, the AI writes a contract comment block at the top of the `.sql` file. The block names what the migration does, what state it requires (preconditions on the database before application), what state it produces (postconditions), what invariants it preserves, and explicit non-responsibilities (changes a reader might expect that this migration does NOT make).

The form of the block is a SQL comment header at the top of the file:

```sql
-- Migration: 0001_nodes
-- Purpose: Create public.nodes table per build_plan/P_1_sql_schema.md.
-- Loads tables: public.nodes
-- Preconditions:
--   * paideia-dev project at PostgreSQL 17.6.
--   * No prior public.nodes table (idempotent via IF NOT EXISTS or
--     migration-ordering enforcement).
-- Postconditions:
--   * public.nodes exists with columns per build_plan/P_1_sql_schema.md.
--   * RLS enabled with v1 policy gating by user_id = auth.uid() (if
--     applicable; nodes carry no user_id — RLS posture decision in
--     phase_3_sql.md).
--   * confidence_level CHECK constraint enforced.
-- Invariants:
--   * No data-modification statements; this is a structural migration only.
-- Non-responsibilities:
--   * Does not seed graph data — Phase 5 seed-authoring sessions populate.
--   * Does not create indexes beyond PK; secondary indexes land per
--     query-pattern decisions at Phase 4.
--   * Does not author RLS policies for learner-state tables; those land
--     in their own migrations.
-- Cross-cutting decisions:
--   * Cascade discipline: see ADR 0031.
--   * RLS posture: see build_readiness/phase_3_sql.md (S-0027 gate).
-- See also: build_plan/P_1_sql_schema.md, ADR 0031, ADR 0030.
```

The contract block is the auditable surface; the migration's body is judged against it. A reader who consults only the block can tell what the migration does and does not do; the body is verification, not interpretation.

The form depends on scope:

- **Per-migration scope** — the SQL comment header above. Every migration file under `product/seed-graph/migrations/` carries one.
- **Module-level decisions** — an ADR. Cross-cutting choices (the cascade graph for learner-state tables per [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md), the RLS posture for `paideia-dev` per [`../build_readiness/phase_3_sql.md`](../build_readiness/phase_3_sql.md), the partition between schema migrations and seed migrations) warrant ADR-level deliberation.

What "non-trivial" means: any migration that creates or alters a table, defines or modifies constraints, authors a trigger, authors an RLS policy, or seeds data of structural significance. Index-only migrations and column-comment-only migrations may use a one-line header. When in doubt, write the contract block.

## Layer 2 — Mechanical gates

The pre-commit hook gates any modified `.sql` file under `product/seed-graph/migrations/` on:

- **Transaction wrap** — every migration starts with `BEGIN;` and ends with `COMMIT;` (or uses `BEGIN;` / `END;`). Idempotent migrations may use `CREATE TABLE IF NOT EXISTS`; non-idempotent migrations rely on Supabase migration ordering and must wrap in a transaction so partial application does not leave the schema in an indeterminate state.

- **CASCADE presence on learner-state FKs** — every foreign-key declaration that references `public.users(id)` includes `ON DELETE CASCADE`. Per [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md), account deletion cascades to every learner-state row; the gate enforces the discipline at the syntactic level.

- **RLS-enable on public tables** — every `CREATE TABLE` in the `public.*` namespace is followed by an explicit `ALTER TABLE <name> ENABLE ROW LEVEL SECURITY;` statement somewhere in the same migration (or a paired migration loaded immediately after). RLS-disable requires an explicit comment naming the deferral and the deciding ADR or build-readiness report.

- **CHECK constraint shape on enum-modeled TEXT columns** — columns named in [`expression-contract-instantiation.md`](expression-contract-instantiation.md)'s SQL row enumeration (`confidence_level`, `interaction_type`, `friction_type`, `nodes.status`, etc.) carry a `CHECK (... IN (...))` clause. The list of enum-modeled columns is maintained alongside the gate — a column added to the list updates the gate.

- **Optional: sqlfluff lint** — if `sqlfluff` is installed and importable, the gate runs `sqlfluff lint --dialect postgres <files>`. Output is hard-fail if `sqlfluff` is configured for the project; advisory if `sqlfluff` is not yet wired. The gate is structured so adding `sqlfluff` to the toolchain is a refinement, not a posture change.

The gates do not validate the meaning of the migration. They make the category of low-level drift that mechanization catches visible cheaply, freeing Layer 1 (the contract block) and Layer 3 (cold-review) to focus on the harder modes.

The gate stack is enumerated here, not in [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md), so that adding a tool to the stack is a refinement under this contract rather than a posture change.

### Gate-stack invocation

Pre-commit invokes these via `validate.py`'s `validate_sql_gates()` function, which is called from [`../tools/hooks/pre-commit`](../tools/hooks/pre-commit) when the staged diff includes any `product/seed-graph/migrations/**/*.sql` file. Soft-warns are not used for SQL gates — missing CASCADE, missing RLS-enable, missing transaction wrap, malformed CHECK constraint shape are all hard-fails. The gates are calibrated to be high-signal; a soft-warn gate would erode the discipline.

Local on-demand invocation:

```bash
python3 engine/tools/validate.py --sql-gates --files product/seed-graph/migrations/0001_nodes.sql
```

The `--sql-gates` flag is mutually exclusive with `--code-gates` and the default repo-structure run; each invocation does one thing.

## Layer 2.5 — Empirical postcondition verification (post-apply, pre-record)

Layers 1–2 verify what the SQL *says*. Layer 3 reads the SQL against its contract block. **None of these query the live DB after the migration commits.** A migration body that says `INSERT INTO nodes ... 28 rows` is signed off if the body claims 28 inserts; the DB might have 27 (or 24, or 0) due to silent FK drops, `ON CONFLICT DO NOTHING`, CHECK constraints rejected and continued, or trigger logic mutating row counts. The drift stays invisible until a downstream session queries the table and finds the gap, possibly many sessions later, after compounding damage.

Layer 2.5 closes that gap. Per [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) Consequences amendment landed at S-0094 (Issue [#23](https://github.com/StarshipSuperjam/paideia/issues/23)), every migration's contract block carries an inline `-- Postcondition-Assertions:` block following the prose `-- Postconditions:` field. Each assertion line is `--   <SELECT returning one integer> :: <expected integer>`. After [`engine/tools/apply_migration.py`](../tools/apply_migration.py) commits the body and records the row in `supabase_migrations.schema_migrations`, every assertion runs against the live DB. Mismatches surface new exit code 8 with all failures listed (not just the first), explicit MANUAL ADJUDICATION guidance, and a cross-reference to this section.

### Authoring rules

- Every new migration carries a `-- Postcondition-Assertions:` block. Migrations without one apply cleanly (apply_migration emits a soft-warn `WARNING: no '-- Postcondition-Assertions:' block declared; skipping Layer 2.5 verification` and exits 0) for backward compatibility, but new authoring is expected to include the block.
- The assertions copy the integers from the prose `-- Postconditions:` field into machine-readable form. Common shapes for the seed-graph corpus (15 examples in `product/seed-graph/migrations/`):

  ```
  -- Postcondition-Assertions:
  --   (one-line prose preamble explaining what these check)
  --   SELECT count(*)::int FROM public.nodes WHERE graph_version_added = N AND '<dom>' = ANY(domain) :: <expected nodes>
  --   SELECT count(*)::int FROM public.edges WHERE graph_version_added = N AND edge_type = 'pedagogical_prerequisite' :: <expected edges>
  --   SELECT graph_version FROM public.settings WHERE id = 1 :: N
  ```

- Each assertion's SELECT must return a single integer in a single row. Returning a non-integer (e.g., a TEXT column), zero rows, or multiple columns counts as a failure with a descriptive message.
- The block ends at the next contract section header (e.g., `-- Invariants:`, `-- Rollback:`) or the first non-`--` line. Lines without `::` inside the block are treated as inline prose and skipped — authors may interleave explanation.
- Malformed grammar (a non-integer to the right of `::`, an empty SELECT to the left) is caught at shape-verification time (exit 2) before any DB connection — the migration never runs against the live DB.

### Exit-code semantics

- **Exit 8** — body applied, schema_migrations recorded, one or more assertions failed. The schema state is post-apply but does NOT match the contract. Manual adjudication: identify whether (a) the assertion SQL is wrong, (b) the prose `-- Postconditions:` block is wrong, or (c) the migration body silently misbehaved. Re-running the migration after fixing would refuse with exit 6 unless `--force`.
- **Exit 3** — assertion query itself raised a SQL error (typo in SELECT, table not found). Treats author-error in assertion SQL the same as author-error in body SQL. The body has already committed; recovery is to fix the assertion grammar in a follow-up commit and re-run with `--force`.
- **Exit 4** — connection failure during the assertion phase (network drop, server restart). Same recovery as any other connection-loss exit 4.

### Why exit 8 still records in schema_migrations

The body has committed; the DB schema is post-apply regardless of the assertion outcome. Skipping the schema_migrations record would mean a re-fire either refuses with exit 6 ("already applied") OR re-executes the body and FK-collides on the now-existing rows. Recording matches reality (the migration *did* apply); the assertion mismatch is a contract-drift signal for the operator, not a recording fault. Exit 8 is distinct from exit 7 (recording fault) so the operator knows where to look.

### Cross-reference: Layer 2.5 vs. Layer 3

Layer 2.5 is empirical (queries the live DB). Layer 3 is text-only (reads the migration file in cold context). They are complementary: assertions catch silent-skip drift between contract claims and live state; cold-review catches premise drift between contract claims and migration body. A passing assertion does not imply the contract is well-conceived; a passing cold-review does not imply the body actually wrote what it said. Both layers are required.

## Layer 3 — Cold-context review pass

At session shutdown, if the session modified tracked SQL under `product/seed-graph/migrations/`, the shutdown sequence launches a sub-agent review pass with no session context. The agent reads each modified migration file's contract block, then reads the migration body, then reports whether the body matches its contract and whether the migration honors this document's discipline. Findings land in [`../session/current.json`](../session/current.json)'s `outcome_summary` before archive.

Fresh eyes that do not share the authoring AI's premises catch what the authoring AI missed. The cold-review pass is the analog to the human spot-check [`document-voice.md`](document-voice.md) relies on — the closest available channel for catching premise drift the authoring session did not surface.

### Cold-review prompt template

The shutdown sequence dispatches an Explore-type sub-agent with this brief:

```
You are reviewing AI-authored SQL migrations for compound drift between
contract and implementation. You have no context for this session — that
is the point. Your premises are not the authoring agent's premises.

For each migration file in the diff:

1. Read the file's contract comment block at the top: it names purpose,
   loaded tables, preconditions, postconditions, invariants, and explicit
   non-responsibilities.

2. Read the migration body. For each contract claim, ask: does the SQL
   actually do this? Does it preserve the invariant the contract names?
   Does it leak behavior the contract says it does not perform? In
   particular, check:
   - CASCADE presence: every FK to users(id) ends in ON DELETE CASCADE
     (per ADR 0031).
   - RLS-enable: every CREATE TABLE in public.* is paired with ENABLE
     ROW LEVEL SECURITY (per build_readiness/phase_3_sql.md, unless the
     migration explicitly defers with a comment naming the deferral).
   - CHECK constraints: enum-modeled TEXT columns
     (confidence_level, status, interaction_type, friction_type, ...)
     carry CHECK (... IN (...)) constraints.
   - Transaction wrap: BEGIN/COMMIT envelope.
   - JSONB constraints: jsonb_typeof check or named-field validation
     where the contract claims structured shape.
   - Idempotency: CREATE TABLE IF NOT EXISTS or migration-ordering
     enforcement.

3. Read the `-- Postcondition-Assertions:` block (if present). Verify
   that each assertion line empirically exercises a claim the prose
   `-- Postconditions:` field makes — assertions that don't correspond
   to a prose claim signal contract-vs-assertion drift, as do prose
   claims with no matching assertion. If the migration applied
   successfully (exit 0), Layer 2.5 already verified the assertions
   passed against the live DB; you may defer to "Layer 2.5 verified
   the row counts" for claims expressed as integer assertions, and
   focus your reading on body-vs-contract premise drift the assertions
   cannot catch (e.g., "all edges are within-domain" is a structural
   claim assertions can approximate but not fully verify). If the
   migration is missing a `-- Postcondition-Assertions:` block
   entirely, flag it as a follow-up authoring task — new migrations
   are expected to include the block per Layer 2.5.

4. Report per-file. For each file, either: "matches contract" with one
   sentence summarizing the match, or a list of specific contract-vs-body
   mismatches. Cite contract claim and SQL line for each mismatch.

You are not reviewing for general SQL style or performance — lint,
syntax, and structural gates run separately. You are reviewing for
premise drift between the contract block and the migration body.

Files in this session's diff (under product/seed-graph/migrations/):
<list of modified .sql files>

Report under 500 words.
```

The findings the sub-agent returns get appended to `outcome_summary` verbatim, with a one-line authoring-session-author response noting which findings were addressed in-session and which (if any) defer to a follow-up.

The cold-review pass runs on SQL under `product/seed-graph/migrations/` only. Sessions that authored prose only, or modified only Python, or only shell scripts, skip this branch. Sessions that modified both Python and SQL run both branches (the Python branch per [`code-discipline.md`](code-discipline.md), the SQL branch per this document).

## Naming and ordering conventions

Migration files follow `NNNN_<table_or_purpose>.sql` where NNNN is a four-digit zero-padded counter. The counter is monotonic per migration directory; Supabase's migration tool consumes the order. Counter values are not session IDs and do not align with `S-NNNN` session IDs.

Migrations are independent unless explicitly noted. A migration that depends on a prior migration (e.g., `0002_user_trigger.sql` depending on `0001_users.sql`) names the dependency in its contract block under "Preconditions."

Migration filenames are immutable once committed and applied to a deployment target. Renaming a committed migration is a posture change requiring an ADR. (Internal to a single in-flight session, before any commit, renames are free.)

## Rollback authorship

Every up-migration has a tested down-migration. If Supabase's tooling provides a `down` step, that step is authored at the same time as the up-step. If not, a sibling `NNNN_<purpose>_rollback.sql` documents the rollback at the SQL level and is verified end-to-end (apply → capture `\d+` output → rollback → apply → diff `\d+` output for stability).

The rollback test is named in the migration's contract block under "Postconditions" or "Cross-cutting decisions" so the cold-review pass can verify the up-and-down symmetry.

## Worked examples

### Good per-migration contract block

```sql
-- Migration: 0003_learner_events
-- Purpose: Create public.learner_events table per ADR 0015 and
--   build_plan/P_1_sql_schema.md.
-- Loads tables: public.learner_events
-- Preconditions:
--   * public.users exists (depends on 0001_users.sql).
--   * public.nodes exists (depends on 0002_nodes.sql).
-- Postconditions:
--   * public.learner_events exists with structured context columns
--     (path_id, source_text_id, session_id) per ADR 0026.
--   * FK learner_events.user_id → users(id) ON DELETE CASCADE per ADR 0031.
--   * FK learner_events.concept_id → nodes(id) (no cascade — node
--     deletion preserves event audit trail per ADR 0021).
--   * CHECK constraint on interaction_type per build_readiness/phase_3_sql.md.
--   * RLS enabled with v1 policy: user_id = auth.uid().
-- Invariants:
--   * Append-only event log; no UPDATE or DELETE statements in this migration.
-- Non-responsibilities:
--   * Does not author secondary indexes; query-pattern indexes at Phase 4.
--   * Does not seed events; Phase 7 onward populates.
-- Cross-cutting decisions:
--   * Cascade discipline: see ADR 0031.
--   * Structured-context discipline: see ADR 0026.
--   * Auth model (local users mirror): see ADR 0031 amendment, S-0027.
-- Rollback: see 0003_learner_events_rollback.sql.
-- See also: build_plan/P_1_sql_schema.md, ADR 0015, ADR 0026, ADR 0031.

BEGIN;

CREATE TABLE public.learner_events ( ... );

ALTER TABLE public.learner_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY learner_events_user_isolation ON public.learner_events
  USING (user_id = auth.uid());

COMMIT;
```

The block names purpose, preconditions, postconditions, invariants, non-responsibilities, and cross-cutting decisions. A reader can tell from the block alone what the migration does and does not do; the SQL is judged against this surface.

### Bad per-migration contract block

```sql
-- Create learner_events table

BEGIN;
CREATE TABLE public.learner_events ( ... );
COMMIT;
```

The block is too thin to audit. The reader cannot tell what columns matter, what cascade behavior the migration commits to, what RLS posture applies, what the rollback is. Compound drift in the body has nothing to drift against in the contract; review is a no-op.

### Module-level contract via ADR

Cross-cutting decisions — the cascade graph spanning multiple tables, the RLS posture, the partition between schema migrations and seed migrations — live in ADRs. The migration's contract block summarizes and links:

```sql
-- Cross-cutting decisions:
--   * Cascade graph: ADR 0031 (every learner-state FK to users(id) carries
--     ON DELETE CASCADE; account deletion cascades through to events,
--     snapshots, tension log).
```

The ADR carries the durable contract; the migration's contract block is the in-file pointer. Posture changes to the cascade graph require updating [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) (not a posture change to ADR 0039 — the gate stack and three-layer structure are unaffected).

## Scope

**Governed:**

- All `.sql` files under `product/seed-graph/migrations/`, including schema migrations and seed-data migrations.
- New `.sql` files authored under that path from the moment this contract accepts.

**Exempt:**

- One-shot SQL queries authored explicitly as throwaway in a session (recorded in `outcome_summary` as exempt-by-judgment) — the cost of contract authoring exceeds the script's lifespan. Three or more uses retire the throwaway exemption.
- SQL embedded in Python source (e.g., `psycopg` query strings) — governed by the Python pattern row, not this row.
- Generated SQL artifacts — the Layer 2 gates skip generated files based on a header marker (`-- GENERATED — DO NOT EDIT`).

**Future:**

- SQL outside `product/seed-graph/migrations/` (e.g., admin scripts, ad-hoc analyses) — this contract's gates do not currently scope outside the migrations directory. Adding a row to [`expression-contract-instantiation.md`](expression-contract-instantiation.md) is the discipline path if such a pattern emerges.

## Amendment discipline

This contract's load-bearing surface is the three-layer commitment for SQL migrations under `product/seed-graph/migrations/`. Refinements within each layer are cheap; restructuring the layers themselves is expensive.

**Refinements (ENGINE_LOG-tracked, no new ADR):**

- Adding a tool to the Layer 2 gate stack (sqlfluff configuration, schema-diff tool, RLS policy linter).
- Sharpening the contract-block authoring guidance (better worked examples, clarified rollback authorship).
- Refining the Layer 3 cold-review prompt template.
- Adjusting the enum-modeled TEXT column list as the schema evolves.
- Updating the `auth.users` vs local-`users`-mirror cascade syntax expectations as Supabase's behavior or the project's auth model evolves.

**Posture changes (require superseding ADR — likely amends [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) for SQL-row-specific changes, or supersedes if the universal-contract framing is what changes):**

- Removing or restructuring any of the three layers for SQL migrations.
- Dropping the CASCADE presence gate as a category.
- Abandoning the cold-review pass at shutdown for SQL.
- Replacing the contract-block prose with a different auditable layer (e.g., per-migration JSON manifest instead of comment header).

The asymmetry holds because what the contract protects is the three-layer compensation for the weak human-audit channel on SQL. Refinements preserve that compensation; posture changes alter what the compensation is calibrated to.

The same amendment-asymmetry pattern [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) and [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) carry: refinement is cheap because it preserves the discipline; posture change is expensive because it is what the discipline binds.

## See also

- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — the citable contract this document operationalizes (universal expression contract).
- [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) — sibling pattern's contract; structural template for the three-layer model.
- [ADR 0031](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) — cascade discipline; the FK-CASCADE gate enforces this ADR's commitment at the syntactic level.
- [ADR 0026](../../product/adr/0026-persistent-learner-storage-structural-not-substantive.md) — structured-columns discipline; informs JSONB constraint shape.
- [`expression-contract-instantiation.md`](expression-contract-instantiation.md) — the per-pattern table; the SQL/migrations row points here.
- [`code-discipline.md`](code-discipline.md) — sibling Layer 1 source-of-truth (Python/engine pattern).
- [`document-voice.md`](document-voice.md) — sibling Layer 1 source-of-truth (prose/inward pattern).
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — carries the Layer 3 cold-review pass step (extended to SQL in this commit).
- [`build-readiness-gate.md`](build-readiness-gate.md) — the gate that enforces "no row, no authoring" before substantive build sessions.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — hard-fail vs soft-warn semantics; the gate stack uses hard-fails uniformly.
- [`adr-authoring.md`](adr-authoring.md) — when an ADR is warranted (cross-cutting cascade graph, RLS posture).
