# Code discipline — expression contract for AI-authored code

> An expression contract is a tool that constrains how the AI expresses itself for a specific surface. This document is the expression contract governing AI-authored code under [`../`](../) (the engine subtree). The project's other expression contracts — [`AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md) for learner-facing prose per [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md), and [`document-voice.md`](document-voice.md) for inward-facing project documentation per [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — govern prose surfaces; this one governs code. They are kindred tools, separately scoped.

## Posture

Code under [`../`](../) is authored under three discipline layers that compose. Each layer targets a different failure mode.

The compound-drift mode is the named target. Compound drift is the failure pattern where a small wrong premise about an invariant, a return shape, a precondition is built upon consistently across many lines, producing internally coherent code that passes tests authored against the same wrong premise. Reading line-by-line does not reveal it; the code is consistent against itself, only inconsistent against the world. The user cannot reliably audit code at scale, and the prose-style discipline that catches voice drift in [`document-voice.md`](document-voice.md) does not transfer to code.

The three layers compensate. **Layer 1** forces the auditable layer up into prose — a contract block per artifact, in form the user reads as readily as a doc. **Layer 2** mechanizes the drift mechanization can catch — type, format, lint, test execution. **Layer 3** introduces fresh eyes — a sub-agent with no session context reads the diff against the contract blocks at session shutdown, the analog to the human spot-check [`document-voice.md`](document-voice.md) relies on.

## Layer 1 — Contract-first prose

Before non-trivial code is authored, the AI writes a contract block. The block names what the code is for, what it requires, what it produces, what invariants it maintains, what edge cases it handles, and — crucially — what it does NOT do. The block is the auditable surface; code is judged against it.

The form depends on scope:

- **Function and class scope** — docstring contract in the file's existing docstring style. The body of the docstring opens with a one-sentence purpose, then enumerates inputs (with types and any preconditions), outputs (with types and any postconditions), invariants the function preserves about external state (file system, database, module-level mutables), edge cases the function handles by design, and explicit non-responsibilities (failures the caller is expected to handle).

- **Module-level decisions** — an ADR. Data structure choices, public API shapes, integration boundaries, dependency choices, file layout decisions all warrant ADR-level deliberation under [`adr-authoring.md`](adr-authoring.md). The ADR is the contract; the module's docstring summarizes and links.

- **Cross-cutting design choices** — an ADR. Choices that affect multiple modules (e.g., the gate-stack composition, the pre-commit invocation pattern) warrant ADR-level commitment.

What "non-trivial" means: any function that is not a one-line wrapper, any class with state, any module that exists for a reason that is not obvious from its filename and one-sentence summary. When in doubt, write the contract block — the marginal cost is low and the failure mode it forbids is expensive.

## Layer 2 — Mechanical gates

The pre-commit hook gates any modified Python file under [`../`](../) on:

- `ruff check` — lint cleanliness across the configured rule set.
- `ruff format --check` — format cleanliness against the project style.
- `mypy --strict` — strict type-check cleanliness (no `Any` leakage, all functions annotated, all returns explicit).
- `pytest` against the file's associated test module — at least one test exists per public function or class, and all tests pass.

The gates do not validate the meaning of the code. They make the category of low-level drift that mechanization catches visible cheaply, freeing Layer 1 and Layer 3 to focus on the harder modes.

The gate stack is enumerated here, not in [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md), so that adding a tool to the stack — a security scanner, a complexity check, a coverage threshold — is a refinement under the contract rather than a posture change. Removing a tool category (e.g., abandoning type-checking entirely) is a posture change requiring superseding ADR.

### Gate-stack invocation

The stack runs in pre-commit and on demand. Local invocation:

```bash
# Lint and format
ruff check engine/
ruff format --check engine/

# Strict type-check
mypy --strict engine/tools/

# Tests
pytest engine/tools/
```

Pre-commit invokes these via `validate.py`'s `validate_code_gates()` function, which is called from [`../tools/hooks/pre-commit`](../tools/hooks/pre-commit) when the staged diff includes any `engine/**/*.py` file. Soft-warns are not used for code gates — type errors, lint violations, format failures, and test failures are all hard-fails. The gates are calibrated to be high-signal; a soft-warn gate would erode the discipline.

### Tool installation

Engine-tool dependencies are declared in [`../tools/requirements.txt`](../tools/requirements.txt). Install with:

```bash
pip install -r engine/tools/requirements.txt
```

The S-0026 session that authored this contract installs the stack and verifies it runs.

## Layer 3 — Cold-context review pass

At session shutdown, if the session modified tracked Python code under [`../`](../), the shutdown sequence launches a sub-agent review pass with no session context. The agent reads each modified file's contract block, then reads the code, then reports whether the code matches its contract. Findings land in [`../session/current.json`](../session/current.json)'s `outcome_summary` before archive.

Fresh eyes that do not share the authoring AI's premises catch what the authoring AI missed. The cold-review pass is the analog to the human spot-check [`document-voice.md`](document-voice.md) relies on — the closest available channel for catching premise drift the authoring session did not surface.

### Cold-review prompt template

The shutdown sequence dispatches an Explore-type sub-agent with this brief:

```
You are reviewing AI-authored Python code for compound drift between contract
and implementation. You have no context for this session — that is the point.
Your premises are not the authoring agent's premises.

For each file in the diff:

1. Read the file's contract blocks: the module docstring (if any) and each
   function or class docstring. Treat the contract block as the truth — it
   names purpose, inputs, outputs, invariants, edge cases, and explicit
   non-responsibilities.

2. Read the implementation. For each contract claim, ask: does the code
   actually do this? Does it preserve the invariant the contract names? Does
   it handle the edge cases the contract enumerates? Does it leak behavior
   the contract says it does not do?

3. Report per-file. For each file, either: "matches contract" with one
   sentence summarizing the match, or a list of specific contract-vs-code
   mismatches. Cite contract claim and code line for each mismatch.

You are not reviewing for general code quality — lint, format, types, and
tests are gated separately. You are reviewing for premise drift.

Files in this session's diff:
<list of modified .py files under engine/>

Report under 500 words.
```

The findings the sub-agent returns get appended to `outcome_summary` verbatim, with a one-line authoring-session-author response noting which findings were addressed in-session and which (if any) defer to a follow-up. The follow-up artifact is a new `outcome_summary` task or, for material drift, a HANDOFF.md entry.

The cold-review pass runs on Python under engine/ only. Sessions that authored prose only, or modified only shell scripts, skip the step.

## Worked examples

### Good function-scope contract block

```python
def parse_register_state(path: Path) -> RegisterState:
    """Parse the session counter state file.

    Reads ``engine/session/register_state.json`` and returns the parsed
    counter. The function is pure with respect to file-system state — it
    reads the path argument and returns the value; it does not write,
    update, or otherwise mutate.

    Inputs:
        path: Absolute path to ``register_state.json``. The file must
            exist and contain valid JSON; the caller is responsible for
            existence and locking. Relative paths are not supported.

    Returns:
        ``RegisterState`` dataclass with ``next_id``, ``last_claimed``,
        and ``current_status`` fields parsed from the JSON. The function
        does not validate that ``next_id`` is monotonic or that
        ``current_status`` matches ``last_claimed``'s archive state —
        those checks belong to ``validate_register_consistency()``.

    Raises:
        FileNotFoundError: The path does not exist.
        json.JSONDecodeError: The file is not valid JSON.
        KeyError: The JSON parses but lacks a required field.

    Edge cases handled:
        - JSON files with trailing whitespace or BOM (handled by the
          standard library parser).
        - Counter values larger than four digits (parsed; not rejected
          here; the validation rule lives in the caller).

    Non-responsibilities:
        - Concurrent-read safety. The caller arranges file locking if
          two sessions could read simultaneously.
        - Atomic-update semantics. The caller arranges write atomicity.
        - Format version handling. The schema is single-version at the
          time of authoring; if a version field is added, that contract
          extension lives in this docstring at the same authoring moment.
    """
```

The contract names purpose, inputs (with preconditions), outputs (with explicit non-claims), exceptions, edge cases handled, and non-responsibilities. A reader can tell from the contract alone what the function does and does not do; the implementation is judged against this surface.

### Bad function-scope contract block

```python
def parse_register_state(path):
    """Parse the register state file."""
```

The block is too thin to audit. The reader cannot tell whether the function is pure, what it raises, what edge cases it handles, what it explicitly does not do. Compound drift in the implementation has nothing to drift against in the contract; review is a no-op.

### Module-level contract via ADR

A new module under [`../tools/`](../tools/) — say, a graph-loader for the Phase 4 graph audit — has its module-level contract in an ADR (analogous to how [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) names the graph-validation contract). The module's docstring summarizes the ADR and links:

```python
"""Graph loader — builds the in-memory graph from the live Supabase tables.

Module contract: ADR 0016 (graph-construction live-validation contract).
This module's responsibility is the load step: querying tables, materializing
nodes and edges, returning a populated ``Graph`` instance. Validation,
audit, and consistency checks are handled by ``validate_graph()`` per the
ADR's split.
"""
```

The ADR carries the durable contract; the docstring is the in-code pointer. Posture changes to the loader's contract require updating the ADR (not a posture change to ADR 0038 itself — the gate stack and three-layer structure are unaffected; only the loader-specific contract changes).

## Scope

**Governed:**

- All `*.py` files under [`../`](../), including [`../tools/`](../tools/), [`../tools/hooks/`](../tools/hooks/) (Python only — shell scripts in this directory are exempt), and any future Python authored under engine/.
- New Python files authored under engine/ from the moment this contract accepts.

**Exempt:**

- Shell scripts under [`../tools/`](../tools/) and [`../tools/hooks/`](../tools/hooks/) (`*.sh`, `pre-commit`, etc.) — short wrappers whose risk surface is bounded by their existing line count. The gate stack does not yet include shell linting; adding a shell-lint gate (e.g., `shellcheck`) is a future ENGINE_LOG-tracked refinement.
- Generated artifacts: [`../tools/validate-history.jsonl`](../tools/validate-history.jsonl) and any future generated files.
- One-shot scripts authored explicitly as throwaway in a session (recorded in `outcome_summary` as exempt-by-judgment) — the cost of contract authoring exceeds the script's lifespan. Three or more uses retire the throwaway exemption.

**Future:**

- Product code under [`../../product/`](../../product/) when it lands (likely Deno/TypeScript Supabase edge functions per [ADR 0029](../../product/adr/0029-personal-financial-cost-ceiling.md) and [`../../product/docs/architecture.md`](../../product/docs/architecture.md)) — governed by the same three-layer posture; the language-specific gate stack adapts at the session that lands the first product code. The adaptation is a refinement (ENGINE_LOG-tracked); the posture is unchanged.

## Amendment discipline

This contract's load-bearing surface is the three-layer commitment. Refinements within each layer are cheap; restructuring the layers themselves is expensive.

**Refinements (ENGINE_LOG-tracked, no new ADR):**

- Adding a tool to the gate stack (security scanner, complexity check, coverage threshold) — refinement of Layer 2.
- Sharpening the contract-block authoring guidance (better worked examples, clarified edge-case handling) — refinement of Layer 1.
- Refining the cold-review prompt template (clearer output format, additional review categories) — refinement of Layer 3.
- Adding a per-language gate appendix when product code lands (e.g., Deno-specific gate stack) — refinement of Layer 2 scope.
- Tightening contract-block requirements (e.g., requiring a "Concurrency:" section for any function that touches shared state) — refinement of Layer 1.

**Posture changes (require superseding ADR):**

- Removing or restructuring any of the three layers.
- Dropping the type-check gate as a category — `mypy` to `pyright` is a refinement; `mypy` to nothing is a posture change.
- Abandoning the cold-review pass at shutdown.
- Replacing contract-first prose with a different auditable layer (e.g., property-based tests instead of contract blocks).

The asymmetry holds because what the contract protects is the three-layer compensation for the weak human-audit channel. Refinements preserve that compensation; posture changes alter what the compensation is calibrated to.

The same amendment-asymmetry pattern [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) carries: refinement is cheap because it preserves the discipline; posture change is expensive because it is what the discipline binds.

## See also

- [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) — the citable contract this document operationalizes.
- [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — sibling expression contract; structural analog for prose surfaces.
- [`document-voice.md`](document-voice.md) — operational surface for [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md); structural sibling.
- [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — sibling expression contract for learner-facing prose.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — carries the cold-review pass step (Layer 3).
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure; build-mode-only gate execution context.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — hard-fail vs soft-warn semantics; the gate stack uses hard-fails uniformly.
- [`adr-authoring.md`](adr-authoring.md) — when an ADR is warranted (module-level and cross-cutting decisions).
- [`cascade-discipline.md`](cascade-discipline.md) — sibling sub-discipline within Python/engine: cascade-analysis pattern + manual procedures.
- [`timestamp-discipline.md`](timestamp-discipline.md) — sibling sub-discipline within Python/engine per [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md): canonical timestamp format and `engine/tools/timestamps.py` helper-routing for emission and parsing.
- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — `decision` drawer conventions for the deliberation behind contract blocks.
