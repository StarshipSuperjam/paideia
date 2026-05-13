# ADR 0070 — Project-wired `/review` skill (five-axis + Paideia overlays)

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0134

## Context

Pre-S-0134, Paideia's code-quality posture has two mechanical layers: [ADR 0038](0038-expression-contract-for-ai-authored-code.md) + [ADR 0039](0039-universal-expression-contract-across-ai-authoring-patterns.md)'s Layer 2 gates (ruff / mypy / pytest in pre-commit and CI per [ADR 0083 (engine)](0083-validate-py-mirror-to-ci.md)) and Layer 3 cold-context review pass at session shutdown for modified Python under `engine/` and SQL under `product/seed-graph/migrations/`. Neither layer walks a *five-axis* review (Correctness, Readability & Simplicity, Architecture, Security, Performance) on the writer's pre-merge self-review or a PR-time reviewer pass. The global `/review` skill (Claude Code's default) is available but project-unaware — it does not understand Paideia's scope_lock posture (per [ADR 0051](0051-routine-mode-and-engine-loop.md)), the ADR-citation requirement for contract changes (per [ADR 0036](0036-expression-contract-for-inward-documents.md) + [ADR 0037](0037-engine-product-wall-and-changelog-rename.md)), or the MemPalace decision-drawer companion-to-ADR pattern (per [ADR 0043](0043-hook-architecture.md) PostToolUse hook).

[Issue #73](https://github.com/StarshipSuperjam/paideia/issues/73) named the adoption as Tier 2 of the SWE-hardening rollout, paired with [Issue #74](https://github.com/StarshipSuperjam/paideia/issues/74) (Pairing C in `engine/STATE.md`'s SWE-hardening table) — both adapt from `addyosmani/agent-skills` (the `code-review-and-quality` and `security-and-hardening` skills) with identical authoring shape and `disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md).

Pattern source: [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/code-review-and-quality/SKILL.md`. Adapted, not cloned — Paideia-specific overlays (scope_lock, ADR-citation, MemPalace decision-drawer, multi-model writer/reviewer pattern for future `/ship` per [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)) are project-specific additions.

## Decision

A new project Skill at `.claude/skills/review/SKILL.md` carries the recipe for Paideia's five-axis code review. The doctrine is the SKILL.md body — no separate Layer 1 ops-doc, because the skill body IS the review doctrine. A companion reference card at `.claude/skills/review/anti-rationalization.md` carries the rationalization → reality-check table; the same card is reused by [`/security-review`](.claude/skills/security-review/SKILL.md) per [ADR 0071](0071-project-wired-security-review-skill.md). Both skills carry `disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — invocation is deliberate, never auto-fired on description match.

### 1. Five-axis review structure

Every `/review` pass walks the change against five axes in order: Correctness, Readability & Simplicity, Architecture, Security (depth-0; depth-N pass deferred to `/security-review`), Performance (depth-0). Each axis produces zero or more findings. Surface-only-on-one-axis review is the failure mode; the structure forces the breadth.

### 2. Five severity tiers

Critical / Required / Nit / Optional / FYI. Critical blocks merge; Required must be addressed before merge; Nit / Optional / FYI are author-discretion. Tier inflation (everything Required) and tier deflation (everything Nit) are both failure modes; the table makes the calibration explicit.

### 3. Change-size discipline

Target ~100 lines; acceptable ~300 lines if logically unified; ~1000+ lines is too large — split before merge. The thresholds match the agent-skills source. Reviewers may decline to review changes that exceed the threshold without a split plan; the threshold is operational, not aspirational.

### 4. Paideia-specific overlays

Three project-specific overlays run alongside the five axes:

- **Scope_lock awareness:** in routine-mode (per [ADR 0051](0051-routine-mode-and-engine-loop.md)), an out-of-scope review finding routes to a GitHub Issue rather than an inline fix. In build-mode, the default-to-fix-in-context rule from `CLAUDE.md` applies.
- **ADR-citation requirement:** a change touching a contract surface (any ADR file, or modifying a function/migration that an existing ADR explicitly names) must amend the ADR and update ENGINE_LOG.md. The PostToolUse hook on ADR writes (per [ADR 0043](0043-hook-architecture.md)) reminds non-blockingly; `/review` verifies.
- **MemPalace decision-drawer check:** new ADRs trigger a companion `decision`-tagged drawer per the two-layer decision-recording rule from `CLAUDE.md`. `/review` verifies via `mempalace_search`.

### 5. Multi-model writer/reviewer pattern (forward-pointer to `/ship`)

This skill is the writer-side of the eventual `/ship` orchestration ([Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)). When `/ship` lands, it will compose: writer-side (this skill) → reviewer-side (a second model running `/review`) → response-side (back to writer) → human decision. Pre-`/ship`, `/review` runs as a single-model self-review or human-PR review.

### 6. Output as structured Markdown report

A Markdown table with severity / axis / finding / file:line / suggested-action columns, plus a Paideia overlay grid (scope_lock, ADR-citation, MemPalace decision drawer) and an anti-rationalization self-check section. Empty rows are fine; reviews that find nothing are real results. Inventing findings to fill the table is the failure mode.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

The `/review` skill adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.** `/review` is invoked from inside any existing session mode (build, routine, or exploration) at the user's discretion.
- ❌ Criterion 2 — new validator soft-warn category. **No.** This adoption introduces no `validate.py` soft-warns; the skill is invoked by the user, not by an automated gate.
- ❌ Criterion 3 — new state file the boot procedure reads. **No.** No new file under `engine/session/` or anywhere the boot procedure reads.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches `.claude/skills/review/SKILL.md` + `.claude/skills/review/anti-rationalization.md` + this ADR + `engine/adr/README.md` row + `engine/STATE.md` row + `engine/ENGINE_LOG.md` entry. Six surfaces; one is a Skill (recipe form), one is a reference card, one is this ADR, three are index/state-tracking entries. Zero ops-doc files; zero tooling files. Well under the threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Mirrors the precedent set by [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (Dependabot adoption, S-0133) and [ADR 0053](0053-mechanism-first-exercise-gate.md) itself ("silent omission is the failure mode this ADR exists to prevent"). The Issue #73 body's pre-S-0134 assertion "First-exercise readiness note per ADR 0053. Cross-cutting" was authored at rollout time before the rubric was being strictly applied per Issue; the rubric evaluation here is the binding judgment.

First real invocation of `/review` against a substantive change is the empirical verification. Captured as a follow-up to this ADR's "Empirical record" subsection or in the next session's `outcome_summary`, mirroring [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)'s "First-PR-arrival verification (pending)" pattern.

### Other consequences

- **Positive — severity-tier discipline.** Critical / Required / Nit / Optional / FYI gives a five-level vocabulary that prevents both inflation (everything Required) and deflation (everything Nit). The anti-rationalization table catches dismissal-by-rationalization.
- **Positive — change-size discipline.** The 100 / 300 / 1000 thresholds force splits before they cost. Per ADR 0040's spirit (build-readiness gate's discipline), upstream constraints reduce downstream review cost.
- **Positive — scope_lock-aware overlay.** Routine-mode sessions per [ADR 0051](0051-routine-mode-and-engine-loop.md) have a path-level safety surface (`scope_lock`); `/review` now respects it — out-of-scope findings route to Issues per [`issue-discipline.md`](../operations/issue-discipline.md), not to inline pressure on the routine.
- **Positive — ADR-citation overlay.** Contract changes (any ADR-touched function/migration) get verified for ADR amendment at review time, defending against the silent-drift failure mode the PostToolUse hook's non-blocking reminder can't always catch.
- **Positive — writer-side groundwork for `/ship`.** This skill is the writer-side of the eventual multi-model writer/reviewer pattern from [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76). Landing it now means `/ship` has an immediate writer-side to compose; the reviewer-side and orchestration ship in `/ship`'s own session.
- **Cost — manual invocation only.** Per `disable-model-invocation: true`, the AI does not auto-fire `/review` on description match. The user (or the AI on explicit user instruction) invokes deliberately. This is the cost named in [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — deliberate-invocation Skills risk under-use if the user forgets. Mitigation: the AI may surface `/review` as a suggestion when authoring substantial changes (the skill is then human-confirmed).
- **Cost — review surface latency.** A `/review` pass on a 300-line change is not instant; the reviewer reads the diff, the relevant context (plan file, ADRs, tests), then walks the axes. Acceptable cost at solo-maintainer scale; at ≥2 collaborators per [Issue #80](https://github.com/StarshipSuperjam/paideia/issues/80), the latency-per-PR will affect throughput — re-evaluate then.
- **Cost — global `/review` skill conflict potential.** The global `/review` and this project-wired `/review` share a name. Claude Code's skill resolution gives project-wired precedence for project repos; outside the Paideia repo the global `/review` is unaffected. No mechanical conflict.
- **Out-of-scope — `/ship` multi-model orchestration.** Per [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76); blocked by this skill + `/security-review` + [Issue #71](https://github.com/StarshipSuperjam/paideia/issues/71) pytest-cov. `/ship` is a future Tier 3 adoption.
- **Out-of-scope — review metrics dashboard.** Tracking review-finding rates over time, per-axis distribution, severity-tier calibration drift. Deferred until ≥2 collaborators per [Issue #84](https://github.com/StarshipSuperjam/paideia/issues/84) (monthly repo-health metrics workflow).
- **Out-of-scope — trunk-based-default variant.** The agent-skills source includes a trunk-based-default review pattern; Paideia's session-lifecycle ritual is not trunk-based at the session-commit level, so the variant doesn't apply. No active import.
- **Out-of-scope — auto-merge gating on review verdict.** Branch protection per [ADR 0066](0066-pr-template-and-branch-protection.md) gates on required status checks (CI mirror per [ADR 0083 (engine)](0083-validate-py-mirror-to-ci.md)); the `/review` verdict is not a required status check (the skill is human-invoked, not CI-runnable). Deferred until `/ship` lands.

### Interaction with existing layers

- **vs. `validate.py` (Layer 2 mechanical gates):** `validate.py` enforces contract shape (soft-warns + hard-fails for known structural failure modes). `/review` enforces semantic correctness — five axes including correctness vs. contract, readability, architecture, surface security, surface performance. Both passes are load-bearing. The anti-rationalization table explicitly names "validate.py passed, ship it" as a false-claim row.
- **vs. cold-review (Layer 3 pass at shutdown):** Cold-review per [ADR 0038](0038-expression-contract-for-ai-authored-code.md) / [ADR 0039](0039-universal-expression-contract-across-ai-authoring-patterns.md) is a session-end pass that checks "did the code drift from its contract block?" against a fresh sub-agent. `/review` is a pre-merge pass that checks "is the implementation actually correct, given the contract?" The two are orthogonal — cold-review catches contract-vs-code drift; `/review` catches contract-or-code wrongness. The anti-rationalization table names this distinction.
- **vs. global `/review` skill:** The project-wired version supersedes the global default for work in this repo. The global remains available as a fallback for non-Paideia work. No active dependency on the global.
- **vs. `/security-review`:** Orthogonal. `/review`'s axis 4 (Security) is depth-0 — flag obvious patterns, surface secrets-in-code, defer the OWASP walk to `/security-review`. `/security-review` is the depth-N pass for security; the two compose, neither substitutes for the other.
- **vs. future `/ship` ([Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)):** This skill is the writer-side. `/ship` will orchestrate writer-side (this skill) + reviewer-side (`/review` on a different model) + response cycle + human adjudication.

### Empirical record

**S-0134 (authoring):** `.claude/skills/review/SKILL.md` + `.claude/skills/review/anti-rationalization.md` committed at HEAD. The skill has not yet been invoked against a real change in this session (manual deliberate-invocation; no auto-fire).

**First-invocation verification (pending).** The first `/review` invocation against a substantive change in a future session is the empirical exercise. Expected: structured Markdown report with five-axis walk, severity tiers, Paideia overlay grid, anti-rationalization self-check. Verification recorded as a follow-up commit to this ADR's "Empirical record" subsection, or in the invoking session's `outcome_summary` per `engine/operations/session-shutdown-sequence.md`. Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)'s "First-PR-arrival verification (pending)" pattern.

## See also

- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; `/review` is recipe (read top-to-bottom at invocation), `anti-rationalization.md` is reference (consulted at multiple junctures within one review).
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — scope-lock posture; the `/review` Paideia overlay extends.
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — routine-mode scope_lock; routes out-of-scope findings to Issues.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise gate; trigger-criterion evaluation above (zero criteria; no readiness note required).
- [ADR 0083 (engine)](0083-validate-py-mirror-to-ci.md) — CI mirror; the validate.py / pytest gates are orthogonal to `/review`.
- [ADR 0066](0066-pr-template-and-branch-protection.md) — branch protection; `/review` verdict is not a required status check (deferred to `/ship`).
- [ADR 0071](0071-project-wired-security-review-skill.md) — `/security-review` companion; same Pairing C session.
- [`.claude/skills/review/SKILL.md`](../../.claude/skills/review/SKILL.md) — the skill itself.
- [`.claude/skills/review/anti-rationalization.md`](../../.claude/skills/review/anti-rationalization.md) — companion reference card; shared with `/security-review`.
- [`engine/operations/code-discipline.md`](../operations/code-discipline.md) — Layer 3 cold-review pass; orthogonal.
- [`engine/operations/issue-discipline.md`](../operations/issue-discipline.md) — where out-of-scope findings route.
- [Issue #73](https://github.com/StarshipSuperjam/paideia/issues/73) — closes this ADR.
- [Issue #74](https://github.com/StarshipSuperjam/paideia/issues/74) — Pairing C sibling (ADR 0071).
- [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) — `/ship` orchestrator that will compose this skill.
- Pattern source: `addyosmani/agent-skills/skills/code-review-and-quality/SKILL.md` + `references/anti-rationalization.md` (adapted, not cloned).
