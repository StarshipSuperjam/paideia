# ADR 0081 — `/ship` multi-model orchestration skill

- **Status:** Accepted
- **Date:** 2026-05-13
- **Deciders:** S-0148

## Context

[Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) (surfaced by the SWE-hardening audit per [ADR 0065](0065-engine-ci-mirror-validate-py.md) Tier 3) names a composition gap. Paideia gained [`/review`](../../.claude/skills/review/SKILL.md) at S-0134 per [ADR 0070](0070-project-wired-review-skill.md) (five-axis writer-side review), [`/security-review`](../../.claude/skills/security-review/SKILL.md) at S-0134 per [ADR 0071](0071-project-wired-security-review-skill.md) (OWASP depth + Paideia overlays), and the pytest-cov coverage floor at S-0136 per [ADR 0074](0074-pytest-cov-coverage-floor.md) (78% floor). Each of the three reviews substantive change from a distinct angle. None composes with the others.

Running a thorough pre-merge review today requires manually invoking `/review`, then `/security-review`, then mentally synthesizing — and remembering to also check coverage delta, scope_lock, ADR-citation, MemPalace decision-drawer presence, and first-exercise-readiness-note presence (per [ADR 0053](0053-mechanism-first-exercise-gate.md)). The serial-manual flow has three failure modes:

1. **Latency.** Three sequential passes take 3× the wall time of three parallel passes.
2. **Synthesis drift.** Mental synthesis lacks a structured verdict shape; "looks fine" becomes the substitute for a calibrated GO / GO-WITH-CAVEATS / NO-GO.
3. **Overlay skip.** The Paideia overlays (scope_lock, ADR-touch, MemPalace, first-exercise) live nowhere in `/review` or `/security-review` alone — both Skills mention them in passing but neither owns the verification. Result: silent skips when the author forgets.

The composition layer is the missing piece. `addyosmani/agent-skills/commands/ship.md` (the pattern source) ships a `/ship` slash command that runs three specialist agents in parallel and synthesizes verdict — novel coordination pattern, rare in Claude tooling repos. Paideia adapts it with the project-specific overlays as parent-level checks.

The blockers cleared in sequence: #73 closed at S-0134 (ADR 0070), #74 closed at S-0134 (ADR 0071), #71 closed at S-0136 (ADR 0074). S-0148 is the first session where all three substrates exist, making composition feasible. STATE.md listed `/ship` as a ready-to-execute alternative for S-0148; user picked it over OQ-DEC1 tension settlement and the validator-regression Issue #116.

## Decision

S-0148 lands [`.claude/skills/ship/SKILL.md`](../../.claude/skills/ship/SKILL.md) + the companion reference card [`.claude/skills/ship/synthesis-template.md`](../../.claude/skills/ship/synthesis-template.md). The Skill operationalizes the composition contract:

1. **Three-sub-agent parallel composition.** `/ship` launches three sub-agents in a single assistant message via three concurrent `Agent` tool calls: a code-review agent invoking the `/review` recipe verbatim, a security-review agent invoking the `/security-review` recipe verbatim, and a coverage-delta agent running the coverage check. The parallel-Agent-invocation pattern is precedented by [`build-readiness-gate/SKILL.md`](../../.claude/skills/build-readiness-gate/SKILL.md) (its step 2 launches up to three Explore agents concurrently) and called out in CLAUDE.md's "Using your tools" guidance.

2. **Coverage source-of-truth priority.** The coverage-delta sub-agent prefers `gh run view --json jobs,conclusion --branch <current>` against the latest CI run (fast — seconds; reads the pytest-with-coverage step output from the [`validate.yml`](../../.github/workflows/validate.yml) workflow per ADR 0074). It falls back to in-process `uv run pytest engine/tools --cov=engine/tools --cov-report=term-missing --cov-fail-under=78` (slow — ~3.5 minutes) only when no CI run exists for the current branch (the dominant pre-push case). The slow path is flagged explicitly in the report header so the user knows the latency was warranted.

3. **Paideia overlays at synthesis-time, not delegated.** The four overlays — scope_lock verification (per [ADR 0051](0051-routine-mode-and-engine-loop.md)), ADR-touch verification (touched contract surface ⇒ ADR amendment in same session), MemPalace decision-drawer check (new ADR ⇒ `decision`-tagged drawer exists per [ADR 0056](0056-mempalace-mechanical-adoption-checks.md)), and first-exercise readiness note check (new cross-cutting mechanism ⇒ note per ADR 0053) — run in the parent `/ship` invocation. The parent owns project-awareness context (session state, ADR corpus, MemPalace, `build_readiness/`) that sub-agents would otherwise re-derive at sub-agent-startup cost.

4. **Verdict vocabulary.** `GO` (clean) / `GO-WITH-CAVEATS` (1-2 Required findings, no Critical, clean overlays, coverage ≥ floor) / `NO-GO` (any Critical, ≥3 Required cluster, coverage drop below floor, scope-lock breach in routine-mode, ADR-citation gap, readiness-note gap, or sub-agent error). NO-GO is judgment-bound friction, not a mechanical block — CI per [ADR 0066](0066-pr-template-and-branch-protection.md) (branch protection on `main`) remains the hard merge gate.

5. **Sub-agent failure mode is explicit gap-pending NO-GO; never silent proceed.** If any of the three sub-agents errors (timeout, crash, unparseable output, refused tool, or returns without the expected structured shape), the synthesis labels the gap (`SUB-AGENT GAP: <which-agent>: <error>`) and treats the unknown axis as a blocker. Empty sub-agent reports are also treated as gaps — honest clean-goes include a structured report with empty Findings tables.

6. **Anti-rationalization rebuttal on override attempts.** When the user attempts to override a NO-GO ("ship it anyway", "the finding is wrong"), the Skill cites the row of [`.claude/skills/review/anti-rationalization.md`](../../.claude/skills/review/anti-rationalization.md) (the shared table) that addresses the specific rationalization pattern. The rebuttal is friction, not refusal — the override is the user's call, made visible.

## Alternatives Considered

Per [ADR 0077](0077-adr-template-alternatives-considered-section.md).

### Sequential invocation (run `/review`, then `/security-review`, then coverage)

- **What:** Author `/ship` as a top-down recipe that runs each sub-agent serially, each waiting on the previous to complete.
- **Pros:** Simpler control flow; easier to debug; reduced peak token cost (only one sub-agent's report in context at a time).
- **Cons:** 3× the wall time of parallel invocation. Loses the parallel-Agent-invocation pattern that [`build-readiness-gate/SKILL.md`](../../.claude/skills/build-readiness-gate/SKILL.md) and CLAUDE.md's "Using your tools" guidance both establish. Synthesis quality is identical (the three reports are orthogonal — `/review` does not condition on `/security-review`'s output, etc.), so the serial coupling adds latency without adding signal.
- **Rejected because:** the latency cost of sequential dominates the simplicity benefit, and the parallel pattern is a project-established idiom worth reinforcing rather than diverging from.

### Single-agent self-review (one general-purpose agent does all three passes)

- **What:** Author `/ship` to invoke a single Agent with a composite brief: "Run `/review` + `/security-review` + coverage, return one synthesized report."
- **Pros:** Simpler implementation; one report rather than three; lower peak context cost; no synthesis step needed in parent.
- **Cons:** Loses the separate `/review` and `/security-review` doctrines that S-0134 invested in (the two skills are independently versioned and have their own anti-rationalization framings). Loses anti-rationalization-by-perspective-separation: a single agent reviewing through both lenses simultaneously is more susceptible to consistency bias (one finding's framing constrains the other's framing). Composes orthogonality into a single context that doesn't structurally enforce it.
- **Rejected because:** the doctrine separation is load-bearing; collapsing it re-couples concerns that S-0134 deliberately split. Three separate sub-agents each operating from a fresh context is the right shape for anti-rationalization purposes.

### CI-only enforcement (skip the Skill; rely on CI + manual review)

- **What:** Close Issue #76 as `wontfix`; treat CI per ADR 0066 + manual `/review` and `/security-review` invocations as the complete pre-merge story.
- **Pros:** Zero new authoring surface; smaller corpus.
- **Cons:** CI is mechanical-only — it runs `validate.py`, `pytest`, `bandit`, `gitleaks`. It does not run `/review` or `/security-review` (those require a model). The judgment-level layer does not exist in CI; it exists in the manual flow that Issue #76 names as failure-prone (sequential latency + synthesis drift + overlay skip). Saying "use the manual flow" is saying "live with the failure modes."
- **Rejected because:** Issue #76's whole point is that the judgment-level layer doesn't exist in CI and that the current manual composition has three named failure modes. The Skill exists to address those.

### Fourth synthesis sub-agent (parent invokes four agents: three reviewers + one synthesizer)

- **What:** Parent `/ship` invocation spawns the three reviewer sub-agents in parallel; on completion, spawns a fourth synthesizer sub-agent given the three reports + project context, asks it to emit the verdict.
- **Pros:** Cleaner separation between gathering and synthesis; the synthesizer could be a different model with explicit judgment-calibration tuning; parent stays small.
- **Cons:** The synthesizer has no native model of project conventions, scope_lock state, ADR corpus, MemPalace, or session context — the parent IS the project-aware layer. The synthesizer would need all of that context briefed cold at startup, paying tokens to re-establish what the parent already has. The Paideia overlays (scope_lock, ADR-touch, MemPalace, first-exercise) are exactly the parent-context-dependent checks that delegating to a fresh agent fights against.
- **Rejected because:** the parent's project-awareness is the whole reason synthesis lives there. The three sub-agents are properly stateless (they only need the diff + the recipe to invoke); the parent is properly stateful (it owns session context); synthesis belongs where the state is.

## Consequences

- New Skill at [`.claude/skills/ship/SKILL.md`](../../.claude/skills/ship/SKILL.md) + companion reference card [`.claude/skills/ship/synthesis-template.md`](../../.claude/skills/ship/synthesis-template.md). The Skill carries `disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — the AI invokes deliberately rather than auto-firing on description match. The synthesis-template card is a recipe-vs-reference partition: SKILL.md is recipe (read top-to-bottom at one moment); synthesis-template.md is reference (consulted at step 5 for output shape).
- **Cascade per [ADR 0041](0041-cascade-discipline-three-validator-checks-plus-manual-procedures.md):** the "Multi-model writer/reviewer pattern (forward-pointer)" subsections in [`.claude/skills/review/SKILL.md`](../../.claude/skills/review/SKILL.md) and [`.claude/skills/security-review/SKILL.md`](../../.claude/skills/security-review/SKILL.md) update from "pending" to "landed at S-0148 per ADR 0081" in the same commit.
- **Per-invocation cost is non-trivial.** Three parallel sub-agents each running through a substantial recipe (`/review` is 206 lines; `/security-review` is 194 lines) plus the coverage check. Expect 3–10× the cost of a single `/review` pass in tokens; wall time depends on whether coverage takes the `gh run view` fast path (seconds) or the `pytest --cov` slow path (~3.5 min). The cost is justified for the substantive-change scope where the Skill warrants invocation; trivial changes route around per the "When to invoke" section.
- **`/ship` is a recommendation gate, not a merge gate.** CI per ADR 0066 remains the hard merge gate. NO-GO produces friction (anti-rationalization rebuttal); override is the user's call. This posture is named explicitly in the Skill body's "When to invoke" section and in the failure-modes section.
- **First-exercise readiness note required per [ADR 0053](0053-mechanism-first-exercise-gate.md).** Criterion-4 evaluation: surfaces touched = SKILL.md + synthesis-template.md + ADR + readiness-note + STATE.md row + ENGINE_LOG entry + cascade updates to two existing Skills = ~8 surfaces. Cross-cutting (the Skill invokes other Skills and reads `engine/session/current.json` + ADR corpus + MemPalace + `build_readiness/`). Issue #76's body explicitly names a first-exercise readiness note as a requirement. **Verdict: note required.** Tier-1 closes in-session at S-0148 via dogfood (invoking `/ship` on S-0148's own deliverable). Mirrors the affirmative-finding pattern from ADRs 0054, 0055, 0060, 0076, 0080 (vs. the negative-finding precedent from ADRs 0069, 0070, 0071, 0072, 0073, 0075, 0077, 0078, 0079).
- **No new row in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md).** `/ship` is not a `validate.py` check; it does not emit soft-warns. The validator-soft-warn-table convention does not apply.
- **No new authoring pattern row in [`engine/operations/expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md).** Per ADR 0044 Consequences, Skills fit under the existing Prose/inward contract; no contract extension required.
- **MemPalace `decision` drawer required at session shutdown** per [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) hook reminder. The drawer captures: the parallel three-sub-agent decision; the coverage source-of-truth priority; the recommendation-gate-not-merge-gate posture; the four Alternatives Considered with brief rejection rationale; the dogfood outcome.
- **Cascade additions to [`engine/operations/cross-references.md`](../operations/cross-references.md):** new rows under "Engine ADRs → consumers" (this ADR's consumers are the two child Skills + the synthesis-template + the readiness note), under ".claude/skills/ → consumers" (ship/SKILL.md consumed by interactive user invocation), and updates to the existing rows for `/review` and `/security-review` (each now consumed by `/ship`).
- **Future hardening pathway: multi-model heterogeneity.** All three sub-agents currently run on the same parent model (no harness mechanism to route sub-agents to different models). The "multi-model" framing is aspirational — when sub-agent model selection becomes available, route the three sub-agents to three different model families to gain genuine anti-rationalization-by-model-perspective. Documented as a Tier-3 forward-pointer in the readiness note.
- **Cascade-discipline reminder:** any future change to `/review`'s or `/security-review`'s output shape (their Findings table columns, their overlay shape) requires updating `/ship`'s synthesis-template and parent-synthesis logic in the same session.

## See also

- [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) — the surfacing Issue from the SWE-hardening audit; closes at S-0148.
- [`.claude/skills/ship/SKILL.md`](../../.claude/skills/ship/SKILL.md) — the skill body this ADR operationalizes.
- [`.claude/skills/ship/synthesis-template.md`](../../.claude/skills/ship/synthesis-template.md) — output shape reference card.
- [`engine/build_readiness/ship_skill_first_exercise.md`](../build_readiness/ship_skill_first_exercise.md) — first-exercise readiness note per ADR 0053.
- [ADR 0070](0070-project-wired-review-skill.md) — `/review` (sub-agent 1).
- [ADR 0071](0071-project-wired-security-review-skill.md) — `/security-review` (sub-agent 2).
- [ADR 0074](0074-pytest-cov-coverage-floor.md) — pytest-cov coverage floor (78%) (sub-agent 3 source-of-truth).
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; SKILL.md is recipe, synthesis-template.md is reference.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness note discipline.
- [ADR 0066](0066-pr-template-and-branch-protection.md) — branch protection (the hard merge gate `/ship` is advisory to).
- [ADR 0077](0077-adr-template-alternatives-considered-section.md) — Alternatives Considered section convention dogfooded above.
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — Layer 3 cold-review pass for Python; `/ship`'s `/review` sub-agent overlaps but is not redundant (cold-review is shutdown-time on engine/Python; `/ship` is pre-merge on any change).
- Pattern source: `addyosmani/agent-skills/commands/ship.md` (adapted, not cloned).
