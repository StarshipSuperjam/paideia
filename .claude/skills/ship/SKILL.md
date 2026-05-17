---
name: ship
description: Multi-model pre-merge orchestration for Paideia. Runs `/review` (writer-side five-axis), `/security-review` (OWASP + Paideia overlays), and a coverage-delta check in parallel as three sub-agents, then synthesizes findings into a GO / GO-WITH-CAVEATS / NO-GO verdict with anti-rationalization rebuttal on override attempts. Recommendation gate, not a merge gate — CI per ADR 0066 remains the hard merge gate. Invoke deliberately on a branch before pushing for review.
disable-model-invocation: true
---

# ship

> Project-wired `/ship` for Paideia per [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md). The doctrine is this SKILL.md — no separate Layer 1 ops-doc. The output shape lives in the companion reference card [`synthesis-template.md`](synthesis-template.md). The anti-rationalization table is shared with [`/review`](../review/SKILL.md) and [`/security-review`](../security-review/SKILL.md) at [`../review/anti-rationalization.md`](../review/anti-rationalization.md).

## When to invoke

A `/ship` pass is warranted on any non-trivial change before merge. It composes [`/review`](../review/SKILL.md) (writer-side five-axis) + [`/security-review`](../security-review/SKILL.md) (OWASP depth) + a coverage-delta check, runs them as three parallel sub-agents, and synthesizes a verdict.

Trivial changes that do NOT warrant `/ship`:

- Typo fixes, comment-only edits, whitespace cleanup
- ENGINE_LOG.md entries authored at session close
- STATE.md row updates
- Auto-generated lockfile regenerations (`uv.lock` after a `pyproject.toml` floor bump)
- ADR-only edits with no other artifact touch (status flips, typo fixes within an ADR body, supersession-marker updates)

Substantive changes that DO warrant `/ship` (same set as `/review`):

- New or modified Python under `engine/tools/`
- New or modified SQL migrations under `product/seed-graph/migrations/`
- New or modified Skills under `.claude/skills/`
- New or substantively-revised ADRs
- New or modified hooks under `engine/tools/hooks/`
- New or modified validators (additions to `validate.py`)
- Phase 6+ frontend or backend code (future)

**Inclusion-list precedence rule.** If a diff matches both an exclusion and an inclusion (e.g., a Skill+ADR landing where a new Skill ships alongside its citable ADR — the S-0148 shape), the inclusion list wins. The exclusion list covers diffs that are *purely* trivial; a substantive Skill/validator/migration change that happens to also touch an ADR is substantive overall.

The skill is **not** a merge gate. CI per [ADR 0066](../../../engine/adr/0066-pr-template-and-branch-protection.md) (branch protection on `main`) + [ADR 0065](../../../engine/adr/0065-engine-ci-mirror-validate-py.md) (validate.py mirror) is the hard merge gate. `/ship` adds the judgment-level layer that CI doesn't — anti-rationalization, per-axis triage, scope/ADR/engine_memory integrity. A `/ship` `NO-GO` produces friction (anti-rationalization rebuttal on override attempts) but does not block merge mechanically.

## Procedure

Run in order. Steps 2's sub-agents are parallel; everything else is sequential.

### 1. Load context

Read:

- The branch diff: `git diff origin/main...HEAD --stat` (file list + line counts) and `git diff origin/main...HEAD` (full diff). For very large diffs, also pull the commit messages: `git log origin/main..HEAD --pretty=format:'%h %s%n%b'`.
- The session's plan file (if any) — path is in `engine/session/current.json`'s `approved_plan` field.
- `engine/session/current.json` for `scope_lock` (routine-mode only) and `working_on`.

These inputs are passed verbatim to each sub-agent in step 2.

### 2. Launch three sub-agents in parallel

**Single assistant message, three `Agent` tool calls.** The dispatch primitive is the harness-provided `Agent` tool (top-level tool name `Agent`, parameter `subagent_type: general-purpose`). This is the parallel-Agent-invocation pattern established by [`build-readiness-gate/SKILL.md`](../build-readiness-gate/SKILL.md) (its step 2 launches up to three Explore agents concurrently) and called out in CLAUDE.md's "Using your tools" guidance ("If you intend to call multiple tools and there are no dependencies between them, make all independent tool calls in parallel"). Empirically verified at the S-0148 dogfood — see [`engine/build_readiness/ship_skill_first_exercise.md`](../../../engine/build_readiness/ship_skill_first_exercise.md) Empirical record.

Each sub-agent gets the branch + change context from step 1 plus a self-contained brief. The three perspectives:

#### Sub-agent 1 — code-review

- `subagent_type: general-purpose`
- Brief: "Run the [`/review`](../review/SKILL.md) recipe verbatim against the branch diff below. Return the full structured Markdown report — Findings table + Paideia overlay checks + Anti-rationalization self-check. Do not summarize; return the report as `/review` would emit it."
- Returns: the `/review` structured report verbatim.

#### Sub-agent 2 — security-review

- `subagent_type: general-purpose`
- Brief: "Run the [`/security-review`](../security-review/SKILL.md) recipe verbatim against the branch diff below. Return the full structured Markdown report — OWASP Top 10 grid + Paideia overlay grid + Findings table + Defense-in-depth cross-check + Anti-rationalization self-check. Do not summarize; return the report as `/security-review` would emit it."
- Returns: the `/security-review` structured report verbatim.

#### Sub-agent 3 — coverage-delta

- `subagent_type: general-purpose`
- Brief: "Compute the coverage delta for the current branch against the floor (78% per [ADR 0074](../../../engine/adr/0074-pytest-cov-coverage-floor.md)). **Preferred path**: run `gh run view --json jobs,conclusion --branch $(git rev-parse --abbrev-ref HEAD)` to fetch the latest CI run's coverage line from the `validate.yml` workflow's pytest-with-coverage step. Parse the `TOTAL` line to extract overall percentage + per-file movement vs. baseline. **Fallback path**: if no CI run exists for the current branch (e.g., pre-push invocation), run `uv run pytest engine/tools --cov=engine/tools --cov-report=term-missing --cov-fail-under=78`. This takes ~3.5 minutes — flag the slow path explicitly in the report header. Return: overall coverage %, delta vs. baseline (80% per S-0136), per-file coverage changes touching the diff's modified files, and PASS / FAIL vs. the 78% floor."
- Returns: coverage report with overall %, delta vs. baseline, per-file movement on diff-modified files, and PASS/FAIL.

**Failure handling per sub-agent.** If any sub-agent errors (timeout, crash, unparseable output, refused tool, or returns without the expected structured shape), the synthesis explicitly names the gap (`SUB-AGENT GAP: <which-agent>: <error>`) and treats the unknown axis as a blocker (`NO-GO` with `gap-pending` qualifier). No silent proceed.

### 3. Apply Paideia overlays (synthesis-side)

These run in the parent `/ship` invocation, NOT delegated to sub-agents — the parent owns project-awareness context (scope_lock, ADR corpus, engine_memory, build_readiness/) that sub-agents would otherwise re-derive.

#### Scope_lock verification

If the session is routine-mode (per [ADR 0051](../../../engine/adr/0051-routine-mode-and-engine-loop.md)):

- Read `engine/session/current.json`'s `scope_lock.allowed_paths`.
- Read the diff's modified file list (from step 1).
- If any modified file is outside `allowed_paths` ∪ the operational allowlist, flag `Scope-lock breach` and set verdict to NO-GO.

If the session is build-mode (interactive `/start-engine`), scope_lock does not apply mechanically; this overlay PASSES by default.

#### ADR-touch verification

If the diff touches any file under `engine/adr/` or `product/adr/`, OR touches a function/migration explicitly named in an existing ADR (grep ADR corpus for the modified function names):

- Verify an ADR was amended or authored in this same session (check the diff's commit messages for ADR file additions/modifications).
- Verify the `engine/ENGINE_LOG.md` `[Unreleased]` section reflects the change.
- If either is missing, flag `ADR-citation gap` and set verdict to NO-GO.

#### engine_memory decisions-room drawer check

If a new ADR was authored this session:

- Run `engine_memory_search` with the ADR's title or decision keywords.
- If no `decision`-tagged drawer matches, flag `engine_memory drawer gap`. Severity: `Required` (NOT NO-GO — the post-ADR-write hook reminds, but the drawer is sometimes deferred to session shutdown).

#### First-exercise readiness note check (ADR 0053)

If the diff introduces a new cross-cutting mechanism (evaluate against ADR 0053 criterion-4: consequences span ≥3 ops docs OR ≥5 tooling files, OR explicit Issue/ADR ask for a readiness note):

- Verify `engine/build_readiness/<mechanism>_first_exercise.md` exists in the diff.
- If missing, flag `Readiness-note gap` and set verdict to NO-GO.

### 4. Synthesize verdict

Apply the verdict matrix:

| Trigger | Verdict |
|---|---|
| Any sub-agent error (gap) | **NO-GO** (gap-pending) |
| Any `Critical` finding (from `/review` or `/security-review`) | **NO-GO** |
| Coverage drops below floor (78%) | **NO-GO** |
| ≥3 `Required` findings (cluster signal across reviewers) | **NO-GO** |
| Scope-lock breach (routine-mode only) | **NO-GO** |
| ADR-citation gap | **NO-GO** |
| Readiness-note gap (new cross-cutting mechanism) | **NO-GO** |
| 1-2 `Required` findings + clean overlays + coverage ≥ floor | **GO-WITH-CAVEATS** (list required actions) |
| Zero `Critical`/`Required` + clean overlays + coverage ≥ floor | **GO** |

The engine_memory drawer gap is `Required`-tier but does NOT escalate to NO-GO; it appears in the required-actions list.

### 5. Emit the structured report

Output per [`synthesis-template.md`](synthesis-template.md). Sample structure:

```markdown
## `/ship` — <branch-name> @ <SHA-short> — VERDICT: <GO|GO-WITH-CAVEATS|NO-GO>

**Change size:** N lines (M files). **Coverage:** P% (floor: 78%, baseline: 80%; Δ: ±X.Xpp).
**Coverage source:** `gh run view` (CI run <ID>) | `pytest --cov` fallback (slow path).
**Sub-agents:** code-review ✓ | security-review ✓ | coverage ✓.

### Verdict rationale

The matrix row(s) that fired. One sentence each.

### Per-axis summary

| Axis | Verdict | One-line |
|---|---|---|
| Correctness | <PASS / FAIL> | <one-line> |
| Readability | <PASS / FAIL> | <one-line> |
| Architecture | <PASS / FAIL> | <one-line> |
| Security | <PASS / FAIL> | <one-line> |
| Performance | <PASS / FAIL> | <one-line> |
| Coverage | <PASS / FAIL> | <P% vs. 78% floor> |
| Scope-lock | <PASS / N-A> | <one-line> |
| ADR-citation | <PASS / FAIL / N-A> | <one-line> |
| engine_memory decisions-room drawer | <PASS / Required / N-A> | <one-line> |
| First-exercise readiness | <PASS / FAIL / N-A> | <one-line> |

### Required actions (NO-GO and GO-WITH-CAVEATS only)

- Per the matrix, what specifically blocks merge or warrants attention before merge.

### Sub-agent reports

#### `/review` report
[verbatim from sub-agent 1]

#### `/security-review` report
[verbatim from sub-agent 2]

#### Coverage report
[verbatim from sub-agent 3]

### Anti-rationalization self-check

Reviewed against [`../review/anti-rationalization.md`](../review/anti-rationalization.md): no rationalizations applied at synthesis time.
```

### 6. Anti-rationalization rebuttal (on user override attempt)

If the user attempts to override a NO-GO verdict ("ship it anyway", "the finding is wrong", "we don't have time"):

- Read [`../review/anti-rationalization.md`](../review/anti-rationalization.md).
- Identify the specific rationalization pattern the user is applying (e.g., "It works, that's sufficient"; "validate.py passed, ship it"; "AI code is probably fine"; "the test is wrong, not the code").
- Cite the row of the anti-rationalization table that addresses the pattern.
- State the reality check the rationalization sidesteps.
- Do NOT block — the override is the user's call. The rebuttal is friction, not refusal.

Example: *"Override noted. The anti-rationalization table row 'validate.py passed, ship it' addresses this: validate.py is structural/mechanical; the `/security-review` Critical you're overriding is semantic. They're orthogonal — passing one is not evidence about the other. Proceeding under your direction."*

## Failure modes this skill prevents

- **Silent override of Critical findings.** The verdict matrix forces NO-GO on any Critical; the anti-rationalization rebuttal adds friction to override attempts. Combined, the path of least resistance is to address the finding, not to ship around it.
- **Coverage-drop drift.** Floor enforcement is CI-gated per ADR 0074, but CI fires after push. `/ship` runs the coverage check pre-push, surfacing drops before they cost a CI cycle.
- **Cluster-signal blindness.** Three separate `Required` findings might each look acceptable individually; the cluster (≥3) is a signal that the change is under-baked. Verdict matrix catches this.
- **Scope-creep absorption.** In routine-mode, the scope_lock overlay forces NO-GO on out-of-bounds edits — the routine-mode-lifecycle's pre-commit hook also catches this, but `/ship` surfaces it before the close commit, when the routine can still file an Issue and proceed.
- **ADR-citation drift.** A contract surface modified without an ADR amendment NO-GOs at synthesis time, catching the case where the developer forgot the ADR amendment.
- **Readiness-note skip on cross-cutting mechanisms.** ADR 0053 requires the note; the overlay enforces. Without `/ship`, only the post-merge audit catches the skip.
- **Sub-agent failure masquerading as clean-go.** A timed-out `/security-review` sub-agent returning empty would otherwise look like "no findings = ship it". The gap-pending NO-GO forces explicit handling.

## Failure modes this skill does NOT prevent

- **Specification errors.** If the underlying contract is wrong, all three sub-agents verify against the wrong contract. The build-readiness gate per [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md) addresses this for substantive build sessions.
- **Runtime errors.** Surfaced by the next session's audit, [ADR 0022](../../../engine/adr/0022-project-health-checks.md) health checks, or live testing.
- **Inter-session drift.** A change merges that conflicts with a future change's premises. Cascade-discipline per [ADR 0041](../../../engine/adr/0041-cascade-analysis-discipline.md) addresses this on next-touch.
- **CI breakage.** `/ship` is advisory; CI per ADR 0066 is the hard gate. A change that `/ship` GOs but CI fails on still cannot merge.
- **Multi-model drift.** All three sub-agents run on the same parent model in the current iteration; future hardening could route each to a different model family, but until then the multi-model framing is aspirational.

## See also

- [`synthesis-template.md`](synthesis-template.md) — companion reference card; consulted at step 5 for output shape.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared with `/review` and `/security-review`; consulted at step 6 for rebuttals.
- [ADR 0081](../../../engine/adr/0081-ship-multi-model-orchestration-skill.md) — the citable contract this skill operationalizes.
- [`/review`](../review/SKILL.md) — sub-agent 1.
- [`/security-review`](../security-review/SKILL.md) — sub-agent 2.
- [`build-readiness-gate`](../build-readiness-gate/SKILL.md) — parallel-Agent-invocation pattern precedent (its step 2 launches up to three Explore agents concurrently).
- [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) — the surfacing Issue.
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition.
- [ADR 0053](../../../engine/adr/0053-mechanism-first-exercise-gate.md) — first-exercise readiness note discipline (the overlay enforces).
- [ADR 0066](../../../engine/adr/0066-pr-template-and-branch-protection.md) — branch protection (the hard merge gate `/ship` is advisory to).
- [ADR 0074](../../../engine/adr/0074-pytest-cov-coverage-floor.md) — pytest-cov coverage floor (78%).
- [`engine/operations/issue-discipline.md`](../../../engine/operations/issue-discipline.md) — where override-recorded findings route as Issues.
- Pattern source: `addyosmani/agent-skills/commands/ship.md` (adapted, not cloned).
