# Expression contract instantiation

> The working surface for [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Per-pattern table of which expression-contract layers each AI authoring pattern in the project carries, with pointers to each layer's source-of-truth document, gate, and review trigger.
>
> Adding a new pattern adds a row before authoring begins. "No row, no authoring" — the build-readiness gate ([ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)) enforces this structurally.

## Layer model

Three layers compose. Each pattern carries Layer 1 plus at least one of Layer 2 or Layer 3.

- **Layer 1 — Contract-first authoring rules.** A prose document the AI reads before authoring an artifact under the pattern. Form depends on the pattern: a forbidden-token enumeration, a positive voice characterization, a per-function docstring contract, a per-migration discipline checklist. Universal across all patterns; without Layer 1 there is no auditable surface for the other layers to bind to.

- **Layer 2 — Mechanical gates.** A toolchain run by the pre-commit hook (or equivalent) that checks the artifact against the Layer 1 contract mechanically. Examples: ruff/mypy/pytest for Python, sqlfluff or hand-rolled grep for SQL, eslint/tsc for TypeScript. Catches low-level drift cheaply; does not catch premise drift.

- **Layer 3 — Cold-context review pass.** A sub-agent with no session memory reads the diff against the Layer 1 contract and reports premise-vs-implementation mismatches. Triggered at session shutdown when the session modified tracked artifacts under the pattern. Catches compound drift the authoring agent cannot see.

The choice of layers per pattern reflects the pattern's audit channel:

- Prose surfaces with reliable human-eye spot-check at authoring + shutdown can carry Layer 1 only.
- Surfaces with hidden-machinery exposure (the rendering policy: Sonnet's prose ships to learners verbatim) need Layer 3 even if Layer 2 detection is unreliable.
- Surfaces with compound-drift exposure (code, schema) need both Layer 2 and Layer 3.

## Pattern instantiation table

| Pattern | Scope path | Layer 1 source-of-truth | Layer 2 gate | Layer 3 review trigger | Citing ADR |
|---|---|---|---|---|---|
| Prose / learner-facing | [`product/AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md) (the surface itself) | [`product/AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md) | N/A — forbidden-token regex unreliable for compound drift | Authoring-session + shutdown spot-check (the Sonnet teaching prompt is the artifact; runtime drift surfaces in Phase 8 evaluation) | [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) |
| Prose / inward | governed inward-facing project documentation; see [`document-voice.md`](document-voice.md) "Scope" section | [`document-voice.md`](document-voice.md) | N/A — voice violations against a positive characterization not mechanically detectable | N/A — authoring-session + shutdown spot-check (the human eye reads the document directly; that is its primary value) | [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) |
| Python / engine | `engine/**/*.py` (excluding shell scripts and generated artifacts; see [`code-discipline.md`](code-discipline.md) "Scope") | [`code-discipline.md`](code-discipline.md) | `ruff check` + `ruff format --check` + `mypy --strict` + test-presence + `pytest`, invoked by `validate.py`'s `validate_code_gates()` from the pre-commit hook | Cold-review pass on `engine/**/*.py` diff at session shutdown; sub-agent reads contract blocks and diff, reports mismatches | [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) |
| SQL / migrations | `product/seed-graph/migrations/**/*.sql` | [`migration-discipline.md`](migration-discipline.md) | hand-rolled grep checks (transaction wrap, CASCADE on FKs targeting `users.id`, RLS-enable on `public.*` tables, CHECK constraint shape on enum-modeled TEXT columns) invoked by `validate.py`'s `validate_sql_gates()` from the pre-commit hook; `sqlfluff lint --dialect postgres` when available as a graceful enhancement | Cold-review pass on `product/seed-graph/migrations/**/*.sql` diff at session shutdown; sub-agent reads migration-discipline.md and diff, reports premise-vs-implementation mismatches | [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) (this session) |
| TypeScript / teaching layer | `product/teaching/**/*.ts` (path placeholder; settles when first artifact lands) | TBD — author at the session that opens the pattern; expected sibling to [`code-discipline.md`](code-discipline.md) | TBD — likely `eslint` + `tsc --strict` + `vitest` or equivalent | TBD — likely cold-review pass on diff at shutdown | TBD — Phase 7 ADR |
| YAML / config | `**/*.yml`, `**/*.yaml` (Supabase config, future CI) — path placeholder | TBD — author at the session that opens the pattern | TBD — likely `yamllint` + schema validation against known config schemas | N/A or TBD — config drift typically Layer 2-detectable | TBD — Phase TBD ADR |
| Shell / tooling | `engine/tools/**/*.sh`, `engine/tools/hooks/pre-commit` and similar — currently exempt under [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) by line-count bound | TBD if scope expands; current exemption is under [`code-discipline.md`](code-discipline.md) "Exempt" section | TBD — `shellcheck` if scope expands | N/A or TBD | TBD — refinement of [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) when shell scope expands |
| Outward / UI text | learner-facing UI labels, error messages, button text, public README, App Store description, learner-visible CHANGELOG entries — currently named in OQ-OUTWARD-VOICE in [`../../product/docs/tensions.md`](../../product/docs/tensions.md) | TBD — open question; decide-before Phase 7 | TBD | TBD — likely Layer 3 since the surface ships to humans verbatim | TBD — resolves OQ-OUTWARD-VOICE |

## How to read a row

A row's load-bearing claim is that the named pattern's authoring is bounded by the named layers and only the named layers. A pattern with "N/A" in Layer 2 explicitly accepts no mechanical detection; a pattern with "TBD" has a row but its instantiation is not yet decided — the build-readiness gate halts authoring under such a pattern until TBDs become concrete.

Worked example: an authoring session about to write `engine/tools/foo.py` reads the Python/engine row, follows it to [`code-discipline.md`](code-discipline.md) for Layer 1, knows the pre-commit hook will run Layer 2 mechanically, and knows that at session shutdown the Layer 3 cold-review pass will fire. The session writes its docstring contract block before the body, expects the pre-commit hook to gate, and expects shutdown to dispatch a sub-agent against the .py diff.

Worked example: an authoring session about to write `product/seed-graph/migrations/0001_nodes.sql` reads the SQL/migrations row, follows it to [`migration-discipline.md`](migration-discipline.md) for Layer 1, knows the pre-commit hook will run hand-rolled grep checks plus optional sqlfluff, and knows shutdown's cold-review pass will read the .sql diff against migration-discipline.md.

Counter-example: an authoring session about to write its first TypeScript edge function under `product/teaching/` reads the TS/teaching-layer row, sees TBDs across all three layers, and halts. The session that opens the pattern is responsible for filling the TBDs (authoring the equivalent of code-discipline.md, wiring the equivalent of validate_code_gates, extending the cold-review trigger) before its first .ts file lands. The build-readiness gate ([ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)) is where this "fill TBDs first" check happens explicitly.

## Adding a new pattern

When a session opens a new authoring pattern (a pattern not yet in the table above):

1. The session pauses authoring of the pattern's first artifact.
2. The session's build-readiness gate exercise authors the pattern's row, choosing layers based on the pattern's audit channel and drift mode.
3. The session authors (or stubs) the Layer 1 source-of-truth document, the Layer 2 gate (if applicable, including pre-commit-hook wiring and validate.py extension if applicable), and the Layer 3 review trigger (if applicable, extending session-shutdown-sequence.md).
4. The session adds an ENGINE_LOG entry naming the new pattern and its layer instantiation.
5. The session may then author the pattern's first artifact under the freshly-landed contract.

The order is load-bearing: a pattern's first artifact never lands before the pattern's row exists. This is what [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s halting discipline enforces.

## Modifying an existing row

Refinements to an existing row are ENGINE_LOG-tracked under [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md)'s amendment discipline:

- Changing the Layer 1 source-of-truth document path (e.g., file renamed or split).
- Adding a tool to the Layer 2 gate stack (e.g., adding a complexity check to the Python/engine row).
- Tightening the Layer 3 cold-review prompt template.
- Adjusting scope-path globs to reflect a directory restructure.

Posture changes — removing a layer the row currently carries, replacing the layer model itself, abandoning the universal-contract framing — require superseding [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md).

## See also

- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — the citable contract this document operationalizes.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the build-readiness gate that enforces "no row, no authoring."
- [`code-discipline.md`](code-discipline.md) — Python/engine row's Layer 1 source-of-truth.
- [`migration-discipline.md`](migration-discipline.md) — SQL/migrations row's Layer 1 source-of-truth.
- [`document-voice.md`](document-voice.md) — Prose/inward row's Layer 1 source-of-truth.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — carries the Layer 3 cold-review pass step (extended to SQL in this commit).
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure; build sessions read this table before authoring.
