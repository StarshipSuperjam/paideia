# apply_migration.py Layer 2.5 postcondition verification — mechanism-first-exercise gate report

> Authored by S-0094 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first interactive exercise of the Layer 2.5 empirical postcondition verification step that [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) Consequences amendment + [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Consequences amendment introduce. Required because the change qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥ 5 surfaces — the change touches the wrapper code + tests + 2 ADRs + 2 ops docs + CLAUDE.md + 15 seed annotations + this readiness file = 23+ surfaces). Sibling to [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md) (the wrapper-itself first exercise from S-0064).

## Mechanism summary

`engine/tools/apply_migration.py` (S-0094 extension) parses an inline `-- Postcondition-Assertions:` block from each migration's contract header and runs every assertion against the live DB after body apply + `schema_migrations` record. Each assertion line is `--   <SELECT returning one integer> :: <expected integer>`. Mismatches surface new exit code 8 with all failures listed (not just the first), explicit MANUAL ADJUDICATION guidance, and a cross-reference to [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md) "Layer 2.5". Schema_migrations is recorded regardless of assertion outcome — the body has committed; mismatch is contract drift, not a recording fault. Distinct in kind from exit 7 (recording fault).

The Layer 2.5 step closes the silent-row-skip gap [Issue #23](https://github.com/StarshipSuperjam/paideia/issues/23) named: a migration body that says `INSERT 28 rows` is signed off by Layer 1 (prose), Layer 2 (mechanical pre-commit), and Layer 3 (cold-review at shutdown) if all three describe an INSERT of 28 rows; the DB might have 27 due to an FK violation rolled back inside `DO $$`, ON CONFLICT DO NOTHING swallowing duplicates, or trigger logic mutating row counts. Layer 2.5 is the only layer that observes post-deployment state.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | No (the new exit code 8 surfaces directly via apply_migration; no validator addition) |
| #3 — introduces a new state file the boot procedure reads | No |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | **Yes** (23+ surfaces) |

**Qualifies; gate session needed before unattended use.** This report IS the gate report; the gate session is S-0094 (build session is also the first-exercise session per the same compression precedent set in `apply_migration_first_exercise.md` at S-0064 and `routine_lifecycle_push_first_exercise.md` at S-0060).

## Phase 0 empirical findings

The load-bearing question: does the Layer 2.5 verifier correctly distinguish (a) all-pass, (b) all-fail, (c) partial-fail, (d) zero-row, (e) non-integer, (f) connection-failure, (g) SQL-error-in-assertion-query, AND (h) does it preserve the schema_migrations record on failure (so re-fire does not silently re-apply)?

### Run 0 — pytest stub coverage (S-0094, in-session)

23 new tests in `engine/tools/test_apply_migration.py` exercise every documented behavior against psycopg-stub fixtures:

- 7 parser tests (header absent / empty block / well-formed / prose-skipping / next-section-header termination / non-integer rejected / empty-SELECT rejected)
- 8 verifier tests (empty list / all-pass / one-fail / multi-fail-all-reported / zero-rows / non-integer / SQL-error-propagates / connection-error-propagates)
- 8 main() integration tests (warn-on-missing / pass-full-success / fail-still-records / multi-failure-stderr / SQL-error-during-assertion → exit 3 / shape-time-rejection-for-malformed-block / scope_lock-unaffected)

**Result.** 47 tests green; full test_apply_migration.py suite passes. Pre-merge gate satisfied.

### Run 1 — live exercise on dev DB (deferred to first post-S-0094 routine fire OR next interactive Phase 5 apply)

The wrapper's `--dry-run` mode is exercised at S-0094 against all 15 annotated seed migrations (every seed parses cleanly, every shape check passes). Full end-to-end apply against `paideia-dev` happens at:

- The next routine-mode migration apply (Phase 5 audit work or Phase 6 onward) — observes either exit 0 with `postconditions verified: N assertion(s) passed.` in stderr OR exit 8 with assertion-failure detail.
- Alternatively, the next interactive `/start-engine` session that re-applies an annotated seed via `--force` (e.g., for verification or recovery) — observes the same.

**Why no in-session live run against dev DB.** Firing an intentionally-failing test migration (e.g., `9999_test_postcondition_fail.sql` with `SELECT 1 :: 2`) against `paideia-dev` would leave a real `schema_migrations` row that contaminates the audit trail validators read. Pure pytest-stub coverage in Run 0 covers the failure-mode discrimination at the API level deterministically. The live exercise comes from natural next-routine-fire or next-interactive-apply work — same precedent as S-0064's wrapper-itself first-exercise (Run 1 deferred to first post-session routine fire).

### Run 2 — failure-mode probe against `0060` cross-bridges (deferred indefinitely)

A failure-mode probe could intentionally annotate `0060_seed_crossbridges_part1.sql` with one wrong integer (e.g., `:: 70` when the real count is 71), re-apply on a Supabase branch via `mcp__supabase__create_branch` (cost-confirmed), observe exit 8, then delete the branch. Defer until needed. The verifier's multi-failure-all-reported test covers the diagnostic shape; the parser's well-formed-on-real-corpus check (all 15 seeds dry-run cleanly at S-0094) covers the syntax fit.

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | Layer 2.5 verifier correctly returns exit 0 (assertions pass) OR exit 8 (assertions fail) on a real annotated migration applied against `paideia-dev` from routine context | **Pending the user's first routine fire post-S-0094 OR first `--force` re-apply of an annotated seed.** If the wrapper exits 0 with `postconditions verified: N assertion(s) passed.` for a successful apply, T1-A closes for the pass path. The fail path is deferred to either Run 2 (designed-to-fail probe on a branch, optional) or natural-occurrence in production work. |
| T1-B | Parser correctly handles every grammar variant the corpus exercises | **Resolved at S-0094.** All 15 seed migrations dry-run cleanly via `python3 engine/tools/apply_migration.py --migration-file <path> --dry-run`. The shape-time grammar check rejects malformed blocks (non-integer expected, empty SELECT) at exit 2. The next-section-header terminator (added during the in-session 0060 first-exercise) prevents the parser from reading past the assertions block into prose containing PostgreSQL `::` casts. |
| T1-C | Failure-mode discrimination distinguishes assertion-fail (exit 8) vs SQL-error-in-assertion-query (exit 3) vs connection-fail-during-assertion (exit 4) vs body-fail-before-assertion (exit 3) vs schema_migrations-INSERT-fail (exit 7) | **Resolved at S-0094.** Per-failure-mode test coverage in `TestPostconditionVerification`. Exit-code precedence documented: exit 8 wins over exit 7 when both happen because schema state is more diagnostic than recording state. |
| T1-D | The schema_migrations row IS recorded on assertion failure (so re-fire does not FK-collide) | **Resolved at S-0094.** `test_main_assertions_fail_returns_8_and_records_in_schema_migrations` verifies the INSERT call happens before the exit 8 path. Documented in module docstring + ADR 0055 amendment + migration-discipline.md Layer 2.5. |
| T1-E | Cold-review prompt template (Layer 3) acknowledges Layer 2.5 verification so the cold-review pass focuses on premise drift Layer 2.5 cannot catch (e.g., structural claims like "all edges within-domain") | **Resolved at S-0094.** `engine/operations/migration-discipline.md` cold-review prompt step 3 added. |

## Tier 2 findings (settle in advance, document)

- **T2-A — Block terminator added during 0060 first-annotation.** The original parser only terminated at the first non-`--` line. Real-world contract blocks have multiple `-- <Header>:` sections (Invariants, Non-responsibilities, Cross-cutting decisions, Rollback, See also) — all `--`-prefixed. The first-annotation against `0060_seed_crossbridges_part1.sql` exposed this gap (the parser read into prose containing `'15'::jsonb`). New `NEXT_SECTION_HEADER_RE` pattern terminates at any `^-- <CapitalLetter><identifier>:$` line. Test added: `test_parse_assertions_block_terminates_at_next_section_header`. The fix lands as part of the same in-session work, not a follow-up.

- **T2-B — Inline `::` in PostgreSQL casts is normal.** The parser must distinguish `<SELECT>::<int>` (assertion grammar) from `<expression>::<typename>` (PostgreSQL cast). The terminator rule (T2-A) is the structural defense; the in-block grammar additionally requires the right side of the rightmost `::` to parse as `int()` (PostgreSQL typenames are not integers). Documented in the parser docstring.

- **T2-C — `record_in_schema_migrations` runs before `verify_postconditions`.** Decision rationale (per the design discussion): the body has committed atomically; the schema state is post-apply regardless of assertion outcome. Skipping the record means re-fire either refuses with exit 6 ("already applied") OR re-executes the body and FK-collides on now-existing rows. Documented in module docstring, ADR 0055 amendment, and migration-discipline.md Layer 2.5.

- **T2-D — Soft-warn on missing block, not hard-fail.** Decision rationale: hard-fail blocks all 15 unannotated seeds in-flight. Soft-warn surfaces the missing block in routine logs, monotonic pressure to annotate without breaking work. Combined with the in-session annotation strategy (all 15 seeds annotated in S-0094 per `feedback_no_pilot_wait_and_see.md`), the soft-warn is transient. Documented in apply_migration.py docstring + migration-discipline.md Layer 2.5.

- **T2-E — Retroactive annotation of all 15 seeds.** Per the CLAUDE.md `feedback_no_pilot_wait_and_see.md` rule (annotate-only-future migrations is a pilot — the mechanism never exercises against the real corpus until net-new authoring occurs). `0060_seed_crossbridges_part1.sql` annotated first as the highest-risk file (71 cross-domain edges depending on 14 prior-migration FKs, no ON CONFLICT — exactly the silent-skip class Issue #23 names). Other 14 annotated via `/tmp/annotate_seeds.py` one-shot script (deleted post-run); each migration's existing prose `-- Postconditions:` field already named the integers in machine-readable form modulo grammar.

## Tier 3 forward pointers (named-and-deferred)

- **T3-A — Sidecar assertion file format.** The Issue #23 design discussion considered Option 2 (sidecar `<NNNN>_<purpose>.assertions.sql` co-authored with the migration) for assertion shapes more expressive than `<SELECT>::<int>` — multi-row checks, set-equality assertions, joins. Defer to a concrete need; the inline grammar covers the seed-graph corpus uniformly.

- **T3-B — Layer 2.5 for other patterns.** If a future authoring pattern introduces side-effecting deployment (e.g., infrastructure-as-code that deploys Supabase config or Edge Functions), the session that lands its row in `expression-contract-instantiation.md` carries the responsibility of declaring whether Layer 2.5 applies and authoring the post-deployment verifier if so. The pattern-agnostic Layer 2.5 framing is in [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) Consequences amendment.

- **T3-C — Live designed-to-fail probe on a Supabase branch.** Run 2 above. Optional; the test suite covers the failure-mode discrimination deterministically.

- **T3-D — Postcondition-assertion linting in `validate_sql_gates()`.** A future enhancement could add a Layer 2 check that warns when a migration has `-- Postconditions:` prose declaring an integer (e.g., "28 nodes") but no matching `-- Postcondition-Assertions:` line for that integer. Defer; current soft-warn at apply time covers the missing-block case, and the cold-review prompt asks the reviewer to verify assertion-vs-prose drift.

- **T3-E — Postcondition-assertion expressiveness for non-integer claims.** Some prose postconditions are structural (e.g., "all edges within-domain", "every (source, target) pair has source.domain[] disjoint from target.domain[]"). Integer assertions can approximate these as boolean-via-int `SELECT count(*) WHERE NOT (...) :: 0`, but the grammar feels strained. Defer; current cold-review pass (Layer 3) is the channel for these claims.

## Cold-review pass

Run after S-0094 closes. Inspect:

- Parser's grammar — does it cleanly handle the 15 real seed annotations? Does the section-header terminator correctly isolate the assertions block from subsequent contract sections?
- Verifier's failure-mode discrimination — does each exit code map to the documented recovery action? Are all failures (not just first) reported?
- ADR 0055 + ADR 0039 amendments — do they cross-reference each other and migration-discipline.md Layer 2.5? Do their `decision`-tagged MemPalace drawers capture the structural choice (Layer 2.5 as new structural layer, not Layer 2 extension)?
- This report — does Run 0's pytest evidence (47 tests green) get captured before S-0094 closes?

## Cross-references

- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the gate's authoring contract.
- [ADR 0055](../adr/0055-apply-migration-wrapping-against-production-reads-gate.md) — the wrapper's authoring ADR; Consequences amendment introduces exit code 8.
- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — the universal expression contract; Consequences amendment introduces Layer 2.5 as a structural new layer.
- [`apply_migration_first_exercise.md`](apply_migration_first_exercise.md) — the wrapper-itself first-exercise note (S-0064); this report is the sibling for the Layer 2.5 extension.
- [`engine/tools/apply_migration.py`](../tools/apply_migration.py) — the wrapper, with Layer 2.5 surfaces.
- [`engine/tools/test_apply_migration.py`](../tools/test_apply_migration.py) — test suite (47 tests).
- [`engine/operations/migration-discipline.md`](../operations/migration-discipline.md) — Layer 2.5 source-of-truth.
- [`engine/operations/expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md) — Layer model + SQL row updated.
- [`product/seed-graph/migrations/0060_seed_crossbridges_part1.sql`](../../product/seed-graph/migrations/0060_seed_crossbridges_part1.sql) — first-annotated migration (highest silent-skip risk).
- S-0094 plan: `~/.claude/plans/hashed-crunching-pnueli.md` (approved at S-0094 boot).
- [Issue #23](https://github.com/StarshipSuperjam/paideia/issues/23) — the gap report this work closes.
