---
name: review
description: Run a Paideia five-axis code review — Correctness, Readability & Simplicity, Architecture, Security, Performance — with severity tiers (Critical / Required / Nit / Optional / FYI), change-size triage, Paideia overlays (scope_lock awareness, ADR-citation requirement, engine_memory decisions-room drawer check), and a structured Markdown report. Adapted from `addyosmani/agent-skills/skills/code-review-and-quality` per ADR 0070. Invoke deliberately on a branch, commit range, or PR.
disable-model-invocation: true
---

# review

> Project-wired `/review` for Paideia. The doctrine is this SKILL.md per [ADR 0070](../../../engine/adr/0070-project-wired-review-skill.md) — no separate Layer 1 ops-doc, because the skill body IS the review doctrine. Updates land here. The companion reference card [`anti-rationalization.md`](anti-rationalization.md) is shared with [`/security-review`](../security-review/SKILL.md).

## When to invoke

A `/review` pass is warranted on any non-trivial change before merge — the writer's pre-merge self-review and the reviewer's PR-time pass. "Non-trivial" is judgment-bound; the change-size discipline below gives the operational test. The skill composes with [`/ship`](../ship/SKILL.md) per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md) (landed at S-0148) as `/ship`'s code-review sub-agent; use `/review` directly for narrow writer-side passes, or `/ship` for the full pre-merge composition with `/security-review` and coverage-delta.

Trivial changes that do NOT warrant `/review`:

- Typo fixes, comment-only edits, whitespace cleanup
- ENGINE_LOG.md entries authored at session close (their content is the artifact, not subject to code-review)
- STATE.md row updates
- Auto-generated lockfile regenerations (`uv.lock` after a `pyproject.toml` floor bump)

Substantive changes that DO warrant `/review`:

- New or modified Python under `engine/tools/`
- New or modified SQL migrations under `product/seed-graph/migrations/`
- New or modified Skills under `.claude/skills/`
- New or substantively-revised ADRs
- New or modified hooks under `engine/tools/hooks/`
- New or modified validators (additions to `validate.py`)
- Phase 6+ frontend or backend code (future)

The Paideia-specific overlays below name when `/review` finds an *out-of-scope* fix or a *contract change* — both surface specific routing actions rather than inline edits.

## The five axes

Walk every change against all five axes, in order. Each axis produces zero or more findings.

### 1. Correctness

- Does the code do what its contract block (per [ADR 0039](../../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md)) declares?
- Are edge cases handled? (Empty inputs, boundary values, error paths, concurrent access.)
- Is error handling appropriate? (Internal code: trust framework guarantees. System boundaries: validate.) Per CLAUDE.md "Don't add error handling, fallbacks, or validation for scenarios that can't happen."
- Do tests cover the change? Are the assertions meaningful (vs. testing-the-mock)?
- Are postconditions verified where the contract names them? (For migrations: per [ADR 0055](../../../engine/adr/0055-apply-migration-wrapping-against-production-reads-gate.md) Layer 2.5, the `-- Postcondition-Assertions:` block should be present and the assertions should sensibly verify the body's effect.)

### 2. Readability & Simplicity

- Names match what they do? (Variables, functions, classes, file names.)
- Control flow is followable cold? (Nesting depth, early-return discipline, naming of intermediate values.)
- Is abstraction justified? Per CLAUDE.md: "Three similar lines is better than a premature abstraction. No half-finished implementations either."
- Are comments necessary, or is the code already clear? Per CLAUDE.md: "Default to writing no comments. Only add one when the WHY is non-obvious."

### 3. Architecture

- Does the change respect the engine/product wall (per [ADR 0037](../../../engine/adr/0037-engine-product-wall-and-changelog-rename.md))? Engine-side code under `engine/`; product-side code/content under `product/`. No imports across.
- Does the change respect the expression-contract instantiation table (per [`engine/operations/expression-contract-instantiation.md`](../../../engine/operations/expression-contract-instantiation.md))? A new AI authoring pattern needs a row before authoring begins ("no row, no authoring").
- Are module boundaries clean? Coupling minimized?
- Does the change introduce a new session mode, a new state file, or a new cross-cutting mechanism? If so: per [ADR 0053](../../../engine/adr/0053-mechanism-first-exercise-gate.md), a first-exercise readiness note is required — verify the trigger-criterion evaluation block is in the authoring ADR.

### 4. Security

Surface-level; depth pass deferred to [`/security-review`](../security-review/SKILL.md).

- Any user-input flowing into SQL, shell, eval, or filesystem operations? Flag as `Critical` if string-concat'd; refer to `/security-review` for parameterized-query and OWASP-walk verification.
- Any new dependencies introduced? Cross-reference Dependabot per [ADR 0069](../../../engine/adr/0069-dependabot-pip-and-actions-ecosystems.md); flag if floor-pin is missing.
- Any secrets, tokens, or credentials in code or config? Flag as `Critical`; gitleaks (per [ADR 0067](../../../engine/adr/0067-gitleaks-pre-commit-secret-scanning.md)) is the pre-commit gate but review is the human catch.
- Any `# noqa`, `# nosec`, `# type: ignore` introduced? Flag unless the suppression comment names the specific reason.

For the full OWASP Top 10 walk, hand off to `/security-review`.

### 5. Performance

Surface-level; deep perf passes are gated by [Issue #79](https://github.com/StarshipSuperjam/paideia/issues/79) once a deployable surface exists.

- Any N+1 queries? Unbounded loops? Synchronous I/O on a hot path?
- Allocations inside tight loops?
- Any new `validate.py` check that pushes a phase budget over its tiered target (per [ADR 0063](../../../engine/adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md))? Subprocess to external system → belongs in `health_probe` phase, not `structural`.

## Severity tiers

Every finding lands in exactly one tier. Use the tier label in the structured report (next section).

| Tier | Action |
|---|---|
| **Critical** | Blocks merge. Security, data loss, broken functionality, contract violation. |
| **Required** | Address before merge. Real correctness or readability problem. (Default tier — no prefix.) |
| **Nit** | Optional. Style, formatting, minor naming. Author chooses. |
| **Optional** | Worth considering, not mandatory. A suggested refactor or alternate approach. |
| **FYI** | Informational. A pattern observation, a downstream-implication note. No action required. |

Tier inflation (everything is `Required`) and tier deflation (everything is `Nit`) are both failure modes. The honest read is the calibration.

## Change-size discipline

Size measured by lines changed (additions + deletions, excluding pure rename diffs).

| Size | Action |
|---|---|
| **~100 lines** | Target. Single-sitting review possible; reviewer can hold the whole change in head. |
| **~300 lines** | Acceptable if logically unified (one feature, one refactor, one migration). Review takes longer; reviewer should chunk. |
| **~1000 lines** | Too large to review well. Split before merge. Strategies: by file group, by horizontal slice (auth before authz), by vertical slice (schema before API before UI), or by stack (foundation commit + feature commit). |

A `/review` pass on a 1000+ line change that finds nothing actionable should be re-run after the split — fresh-eyes after the split surface findings the cold-read on the bundled change missed.

## Paideia-specific overlays

These run in addition to the five axes; they don't substitute for any of them.

### Scope_lock awareness

If the session is in routine-mode (per [ADR 0051](../../../engine/adr/0051-routine-mode-and-engine-loop.md)), check `engine/session/current.json`'s `scope_lock.allowed_paths`. A review finding that suggests an out-of-scope fix (e.g., "rename this helper to be clearer" when the helper is outside `allowed_paths`) is NOT inline-fixable in this session — the appropriate routing is:

- File a GitHub Issue (`bug` / `tech-debt` / `cleanup` / `enhancement` label) per [`issue-discipline.md`](../../../engine/operations/issue-discipline.md).
- Surface the Issue number in the review finding.
- Do NOT pressure the reviewee to expand scope.

If the session is build-mode (interactive `/start-engine`), scope_lock does not apply mechanically — the reviewee can absorb the fix in-session per CLAUDE.md "Default to fix-in-context."

### ADR-citation requirement

If the change touches a contract surface — any file under `engine/adr/` or `product/adr/`, or modifying a function/migration that an existing ADR explicitly references by name — verify:

- The ADR was amended (or a new ADR authored) in the same commit or session.
- The ENGINE_LOG.md `[Unreleased]` section reflects the change.
- The engine_memory `decisions`-room drawer was authored if the change is a settled decision (the `PostToolUse` hook on ADR writes per [ADR 0043](../../../engine/adr/0043-hook-architecture.md) reminds, but the reminder is non-blocking).

Missing any of these is a `Required` finding.

### engine_memory decisions-room drawer check

If a new ADR was authored in this session: confirm a matching `decision`-tagged drawer in engine_memory via `engine_memory_search`. The post-adr-write hook reminds, but the reminder is non-blocking; the review verifies.

### Multi-model writer/reviewer pattern (landed at S-0148 per ADR 0081)

This skill is the writer-side. [`/ship`](../ship/SKILL.md) per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md) composes this skill as its code-review sub-agent alongside [`/security-review`](../security-review/SKILL.md) (security depth) and a coverage-delta check, runs all three as parallel sub-agents, and synthesizes a GO / GO-WITH-CAVEATS / NO-GO verdict. The multi-model framing remains aspirational — all three sub-agents currently run on the parent's model — but the perspective-separation (three independent sub-agents from fresh context) provides the anti-rationalization-by-perspective-separation property even without per-Agent model heterogeneity. Use `/review` directly for narrow writer-side passes; use `/ship` for the full pre-merge composition.

## Review process sequence

Run in order. Each step's output is input to the next.

1. **Load context.** Read the relevant plan file (if any), the session's eager-claim commit message, the load-bearing ADRs the change touches (per the change's commit message + STATE.md `next_session_work_item`), and `engine/session/current.json` (if mid-session) for `scope_lock` and `working_on`.
2. **Examine tests first.** What does the test suite say about intent? Where are the gaps? Are the assertions meaningful or testing-the-mock?
3. **Walk the implementation against the five axes** in the order above. Each axis surfaces zero or more findings.
4. **Apply Paideia overlays.** Scope_lock awareness, ADR-citation check, engine_memory decisions-room drawer check.
5. **Categorize every finding by severity tier.** Critical / Required / Nit / Optional / FYI. Calibrate the tier — neither inflate nor deflate.
6. **Verify the verification story.** Did `validate.py` pass? Did pytest pass? Did manual testing happen for any UI surface? Are the verification claims in the PR description honest?
7. **Emit the structured Markdown report** (next section). Self-check against the anti-rationalization table ([`anti-rationalization.md`](anti-rationalization.md)).

## Output shape

A structured Markdown report. Sample:

```markdown
## `/review` — <branch-name> @ <SHA-short>

**Change size:** N lines (M files). **Tier:** target / acceptable / too-large.

**Verification story:** validate.py <pass/fail>; pytest <pass/fail/N tests/M%>; manual testing <yes/no/N/A>.

### Findings

| Severity | Axis | Finding | File:Line | Suggested action |
|---|---|---|---|---|
| Critical | Correctness | <one-line> | path/to/file.py:42 | <action> |
| Required | Readability | <one-line> | path/to/file.py:117 | <action> |
| Nit | Readability | <one-line> | path/to/file.py:5 | <action> |
| Optional | Architecture | <one-line> | path/to/file.py | Consider <alternative> |
| FYI | Performance | <one-line> | path/to/file.py | <observation> |

### Paideia overlay checks

- **Scope_lock:** PASS (or: `<finding>`)
- **ADR-citation:** PASS (or: `<finding>` — Issue filed/needed)
- **engine_memory decisions-room drawer:** PASS (or: `<finding>` — drawer missing for ADR NNNN)

### Anti-rationalization self-check

- Reviewed against [`anti-rationalization.md`](anti-rationalization.md): no rationalizations applied.
```

Empty findings rows are fine — a clean review is a real result. Do not invent findings to fill the table.

## Failure modes this skill prevents

- **Tier inflation.** Every finding marked `Required` because "everything matters" — the result is no signal, just noise. The five-tier calibration forces honest grading.
- **Surface-only review.** Reading the diff but not the context (plan file, ADRs, tests). The "Load context" step is sequence-first for this reason.
- **Scope-creep absorption.** A reviewer suggests a fix that's outside the change's scope, the reviewee accepts under pressure, the PR balloons. The scope_lock overlay routes out-of-scope fixes to Issues.
- **Contract drift.** A function with an existing ADR reference gets modified without amending the ADR. The ADR-citation overlay catches this.
- **Rationalization-as-review.** "Author says it's fine" / "validate.py passed" / "tests pass" treated as substitutes for review. The anti-rationalization table is the catch.

## Failure modes this skill does NOT prevent

- **Specification errors.** If the contract is wrong, the review verifies against a wrong contract. (Build-readiness gate per [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md) addresses this for substantive build sessions.)
- **Runtime errors.** Surfaced by the next session's audit, ADR 0022 health checks, or live testing.
- **Inter-session drift.** A change merges that conflicts with a future change's premises. Cascade-discipline per [ADR 0041](../../../engine/adr/0041-cascade-analysis-discipline.md) addresses this on next-touch.

## See also

- [`anti-rationalization.md`](anti-rationalization.md) — companion reference card; shared with [`/security-review`](../security-review/SKILL.md).
- [ADR 0070](../../../engine/adr/0070-project-wired-review-skill.md) — the citable contract this skill operationalizes.
- [`/security-review`](../security-review/SKILL.md) — depth pass for security findings.
- [`/ship`](../ship/SKILL.md) — multi-model orchestrator composing this skill (landed at S-0148 per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md)).
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition this skill instantiates.
- [`engine/operations/code-discipline.md`](../../../engine/operations/code-discipline.md) — Layer 3 cold-review pass for Python; this skill overlaps but is not redundant (cold-review is shutdown-time on engine/Python; `/review` is anytime on any change).
- [`engine/operations/issue-discipline.md`](../../../engine/operations/issue-discipline.md) — where out-of-scope findings route.
- Pattern source: `addyosmani/agent-skills/skills/code-review-and-quality/SKILL.md` (adapted, not cloned).
