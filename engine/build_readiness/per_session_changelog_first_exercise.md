# First-exercise readiness note — Per-session changelog directory (ADR 0092)

- **Mechanism:** Per-session changelog directory at `engine/changelog/<YYYY>/<S-NNNN>-<slug>.md` with schema-validated frontmatter, 50/70-line cap, aggregator-driven `[Unreleased]` synthesis.
- **Authored at:** S-0198, 2026-05-17.
- **ADR:** [ADR 0092](../adr/0092-per-session-changelog-directory.md). Cross-cutting mechanism authoring per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) trigger criterion #4 (Consequences span 25+ surfaces).

## Tier 1 (close before unattended use)

### T1-A — The S-0198 close itself writes a valid per-session entry

- **Closes when:** S-0198's close commit lands `engine/changelog/2026/0.1.0-foundation-close-S-0198.md` AND `validate.py` exits 0 against the entry's schema + line-cap checks.
- **Closure exercise IS the S-0198 close.** The 0.1.0 release synthesis entry exercises the directory pattern + schema + line-cap discipline against the live validate.py at the close commit. Hard-fails block the close.
- **Status: CLOSED in-session.** Verified at the close commit.

### T1-B — Next session writes a valid per-session entry (non-release)

- **Closes when:** the first post-S-0198 build session that produces material engine-change content writes an entry to `engine/changelog/2026/<S-NNNN>-<slug>.md` AND `validate.py` exits 0.
- **Exercise:** the next interactive build session that produces a material change. Routine sessions also exercise the pattern (the shutdown step is mode-agnostic per the rewired step 7).
- **Status: OPEN** as of S-0198 close.

### T1-C — Aggregator runs cleanly against ≥2 entries

- **Closes when:** `python3 engine/tools/changelog_aggregate.py` runs against `engine/changelog/2026/` containing the 0.1.0 entry + at least 1 post-0.1.0 entry, emits a valid Keep-a-Changelog markdown block, and `--format json` produces schema-conformant output.
- **Exercise:** after T1-B closes (next session's entry exists), invoke the aggregator manually OR wait for a future session that uses the aggregator naturally (e.g., a release-prep session, or a session that wants the `[Unreleased]` view).
- **Status: OPEN** as of S-0198 close. The aggregator can run against the 0.1.0 entry alone at session close (validates the path-walking + frontmatter-parsing); the ≥2-entry exercise validates grouping + filtering + sorting.

## Tier 2 (close after first natural exercise)

### T2-A — `--since <git-tag>` filter behaves correctly

- **Closes when:** a future session runs `python3 engine/tools/changelog_aggregate.py --since engine-v0.1.0` and the output excludes the 0.1.0 entry while including all post-tag entries.
- **Exercise:** natural exercise at the next release-prep session OR explicit invocation.
- **Status: OPEN** as of S-0198 close.

### T2-B — `--module <name>` filter behaves correctly across multiple entries

- **Closes when:** a future session runs `python3 engine/tools/changelog_aggregate.py --module <name>` and the output includes only entries with the matching frontmatter `module` field.
- **Exercise:** natural exercise.
- **Status: OPEN** as of S-0198 close.

### T2-C — Validator hard-fails block a malformed entry from landing

- **Closes when:** an attempted commit with a malformed changelog entry (missing required frontmatter field, line-cap breach above 70, schema-invalid `material_change_class`) is mechanically blocked by `validate.py` at the pre-commit hook.
- **Exercise:** natural exercise (a session accidentally exceeds the cap) OR explicit dry-run test.
- **Status: OPEN** as of S-0198 close.

## Tier 3 (deferred or trigger-gated)

### T3-A — Annual rollover firing

- **Closes when:** the first January 1 (or first session of a new year) moves `2026/` content into `_history/2026/` AND establishes `2027/`.
- **Trigger:** new year boundary. No automation; manual procedure documented in `engine/changelog/README.md`.
- **Status: TRIGGER-GATED** until 2027-01-01.

### T3-B — Aggregator scaling at 20+ entries

- **Closes when:** the aggregator runs cleanly with the `2026/` directory carrying 20+ entries (stress test for sort stability, frontmatter parsing throughput, output formatting).
- **Trigger:** entry count threshold reached naturally.
- **Status: TRIGGER-GATED** until 20+ entries accumulate.

## Verification (run at S-0198 close)

1. `python3 -c "import json, jsonschema; jsonschema.Draft202012Validator.check_schema(json.load(open('engine/schemas/changelog-entry.schema.json')))"` exits 0.
2. `python3 engine/tools/changelog_aggregate.py` against `engine/changelog/` containing the 0.1.0 entry — emits markdown block; exits 0.
3. `python3 engine/tools/changelog_aggregate.py --validate-only` — schema validation passes for the 0.1.0 entry.
4. `python3 engine/tools/validate.py` exits 0 — no `changelog_entry_schema_violation`, `changelog_entry_hard_cap`, `changelog_entry_no_frontmatter`, or `changelog_entry_filename_mismatch` fires. `engine_log_format` no longer registered.
5. `git tag` lists `engine-v0.1.0`.
6. `pytest engine/tests/test_changelog_aggregate.py` all green.
7. `pytest engine/tests/test_validate.py -k changelog` all green.
8. Skill ↔ Layer-1 parity: validate.py's `validate_skill_layer1_parity` passes (no `skill_layer1_parity_drift`).

## Cross-references

- [ADR 0092](../adr/0092-per-session-changelog-directory.md) — substrate decision.
- [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) — superseded in part.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — trigger criterion #4 (≥5 surface span) fires.
- [ADR 0084](../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — extraction step exercised in ADR 0092 Context.
- `engine/changelog/2026/0.1.0-foundation-close-S-0198.md` — first per-session entry; T1-A closure exercise.
- `engine/tools/changelog_aggregate.py` — aggregator under exercise.
- `engine/tools/validate.py` `check_changelog_entries` + `check_changelog_readme_governance` — gate enforcing T1-A.
