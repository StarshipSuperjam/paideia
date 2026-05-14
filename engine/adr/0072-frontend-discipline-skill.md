# ADR 0072 — Project-wired `/frontend-discipline` skill (invariant core)

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0135

## Context

Pre-S-0135, Paideia has no frontend authoring posture. The Discovery / Planning / Engagement triad per [ADR 0034 (product)](../../product/adr/0034-discovery-planning-engagement-triad.md) is committed; the platform-target via SwiftUI per [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 1 is committed (ADR 0065 supersedes [ADR 0035](../../product/adr/0035-multi-platform-apple-expansion.md) — commitment 1's platform language is preserved verbatim); Phase 6 (frontend implementation) is gated behind OQ-DEC1 settlement per [`engine/STATE.md`](../STATE.md). Beyond a planned light web presence for the marketing site + a knowledge-graph visualizer (user-disclosed at S-0135 planning), no frontend code has been authored.

[Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) (Tier 2 of the SWE-hardening rollout, `priority:urgent`) argues that AI-visual-smell defaults harden fast once Phase 6 UI authoring begins. The remediation cost (retrofitting visual identity, accessibility, design tokens, composition discipline after the fact) is asymmetric vs. the prevention cost (a project-wired discipline skill authored before any Phase 6 frontend code lands). The Issue body proposed a single `frontend-ui-engineering` skill adapted from [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/frontend-ui-engineering` — generically authored from a web-stack assumption (Lucide/Heroicons, 320–1440px responsive breakpoints, React state libs).

Planning at S-0135 surfaced two scope corrections that shape this ADR:

1. **Stack-coupling correction.** Issue body assumed a web stack; [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 1 commits Paideia to SwiftUI. The user's correction during planning — "no web app" forecloses the consumer product distribution channel, *not* every web surface (marketing site + graph visualizer are different categories) — is now explicit in ADR 0065 commitment 1's scope clarification (resolved at S-0154 per [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106)). Either way, the practical state is **dual-surface (Swift app + light web presence)** with stack-specific implementations differing in idioms. A skill authored against a single stack would either be wrong-for-the-other-surface or carry baked-in stack assumptions for one when both are in scope.

2. **Architectural correction (user-directed principle, broader than this skill).** *"Everything built by us should have core invariant structures applicable to any project and then modules that tailor that systems use for the specific project needs."* This is a standing architectural posture, not just guidance for this Issue. It applies to all future skill / tool / ops authoring. Per the principle, **partition into an invariant core that names principles without baking in project-specific or stack-specific assumptions + project-tailoring modules that compose with the core + stack-specific modules that dock when each stack opens**. The invariant core is hypothetically reusable in another project; the tailoring modules are not.

The two corrections together: Issue #75 closes via **two ADRs** (this ADR adopts the invariant core; [ADR 0073](0073-paideia-frontend-overlays-skill.md) adopts the project-tailoring module) plus an explicit deferral of stack-specific implementation skills until each stack actually opens (Phase 6 for SwiftUI; whenever web work starts for web).

Pattern source: [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) `skills/frontend-ui-engineering/SKILL.md` + `references/accessibility-checklist.md`. Adapted, not cloned — stack-specifics and project-specifics deliberately omitted from this skill per the modular-architecture principle.

Authoring precedent: mirrors S-0134 Pairing C ([ADR 0070](0070-project-wired-review-skill.md) `/review` + [ADR 0071](0071-project-wired-security-review-skill.md) `/security-review`) — same Issue-body-overridden-by-rubric pattern, same `disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md), same two-ADR-in-one-session shape with shared anti-rationalization table consumption.

## Decision

A new project Skill at `.claude/skills/frontend-discipline/SKILL.md` carries the recipe for the universal frontend-engineering discipline. The doctrine is the SKILL.md body — no separate Layer 1 ops-doc, because the skill body IS the discipline (per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) recipe form). Two companion reference cards: `.claude/skills/frontend-discipline/ai-smell-rejection.md` (expanded catalog for concern 1 + frontend-specific anti-rationalization table) and `.claude/skills/frontend-discipline/accessibility-invariants.md` (expanded rubric for concern 2 + stack-appendix docking convention).

The shared severity-rubric anti-rationalization table at `.claude/skills/review/anti-rationalization.md` (canonical per [ADR 0070](0070-project-wired-review-skill.md)) is *also* consumed; this skill cross-references it without duplication. The new `ai-smell-rejection.md` carries UI-specific rationalizations distinct from the shared table — the partition is modular: shared rationalizations apply to all reviewing skills; UI-specific rationalizations colocate with this skill.

`disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — invocation is deliberate, never auto-fired on description match.

### 1. The seven invariant concerns (stack-agnostic body)

The SKILL.md walks every change against seven concerns: AI visual smell rejection, accessibility invariants, design-token integrity, state-flow hierarchy, composition, adaptive layout, performance posture. The concerns name *principles*, not *implementations* — implementation-level guidance (SwiftUI property wrappers, CSS framework conventions, specific icon-library choices) is deferred to stack-specific sibling skills.

### 2. Severity tiers + change-size discipline reused from `/review`

Same Critical / Required / Nit / Optional / FYI rubric per [ADR 0070](0070-project-wired-review-skill.md). Same 100/300/1000-line change-size thresholds. Reuse prevents calibration drift across reviewing skills.

### 3. Composition with project-tailoring and stack-specific skills

The skill's "When to invoke" rubric names that invocation is alongside the project-tailoring skill (`/paideia-frontend-overlays` per [ADR 0073](0073-paideia-frontend-overlays-skill.md)). When stack-specific skills land (e.g., a future `frontend-swiftui` for Phase 6 entry), the SKILL.md cross-references them; the invariant-core stays stack-agnostic.

### 4. Stack-appendix docking convention

`accessibility-invariants.md` explicitly names the convention for future stack-specific verification appendices: a new stack-skill authors its own verification reference card; this card's docking section cross-references rather than absorbing. The convention preserves the invariant/stack-specific partition this skill depends on.

### 5. AI visual smell catalog and frontend-specific anti-rationalization table

`ai-smell-rejection.md` catalogues the recognizable patterns of default-AI aesthetics (purple/violet defaults, decorative gradient washes, AI-sparkle/star motifs, generic centered-hero-with-two-CTAs, emoji-as-icon, AI-modern type pairings, generic design-system template tokens) — all stack-agnostic. Examples reach for *principle* (intentional alternative or default), not *implementation* (specific token names that lock to a stack). The colocated anti-rationalization table carries UI-specific rationalizations distinct from the shared severity-rubric table at `.claude/skills/review/anti-rationalization.md`.

### 6. Structured Markdown report output

A Markdown table with severity / concern / finding / file:line / suggested-action columns, plus an invocation grid (which related skills were composed), the project-overlay pass cross-reference, and an anti-rationalization self-check section consulting both the shared and the UI-specific tables.

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

The `/frontend-discipline` skill adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.** `/frontend-discipline` is invoked from inside any existing session mode at the user's discretion.
- ❌ Criterion 2 — new validator soft-warn category. **No.** This adoption introduces no `validate.py` soft-warns; the skill is invoked by the user, not by an automated gate.
- ❌ Criterion 3 — new state file the boot procedure reads. **No.** No new file under `engine/session/` or anywhere the boot procedure reads.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches `.claude/skills/frontend-discipline/SKILL.md` + `.claude/skills/frontend-discipline/ai-smell-rejection.md` + `.claude/skills/frontend-discipline/accessibility-invariants.md` + this ADR + `engine/adr/README.md` row + `engine/STATE.md` row + `engine/ENGINE_LOG.md` entry. Seven surfaces; one Skill (recipe), two reference cards, this ADR, three index/state entries. Zero ops-doc files; zero tooling files. Under the threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md) (S-0133), [ADR 0070](0070-project-wired-review-skill.md), and [ADR 0071](0071-project-wired-security-review-skill.md) (S-0134 sibling) precedents. The Issue #75 body's pre-S-0135 assertion "First-exercise readiness note per ADR 0053. Cross-cutting (introduces a new posture surface for the whole frontend stack)" was authored generically at rollout time before the rubric was being strictly applied per Issue; the rubric evaluation here is the binding judgment.

First real invocation of `/frontend-discipline` against a substantive change is the empirical verification. Captured in the invoking session's `outcome_summary` per `engine/operations/session-shutdown-sequence.md`, or as a follow-up to this ADR's "Empirical record (pending)" subsection. Natural near-term occasions: marketing-site authoring, knowledge-graph visualizer authoring (web stack, likely before Phase 6 SwiftUI opens), or Phase 6 SwiftUI authoring once OQ-DEC1 settles.

### Other consequences

- **Positive — modular shape enables expansion or retraction without rebuilding.** Per the user's standing architectural principle. Stack-specific skills (`frontend-swiftui`, `frontend-web`) dock alongside this one when their stacks open; retracting a stack = delete its sibling skill; the invariant core stays intact. Adding the project-tailoring overlay (per [ADR 0073](0073-paideia-frontend-overlays-skill.md)) does not modify this skill; the partition is structural.
- **Positive — universal severity calibration.** Reusing `/review`'s tier rubric prevents drift across reviewing skills. A `Required` here means the same thing as a `Required` in `/review`.
- **Positive — AI visual smell catalog reusable beyond Paideia.** The seven invariants and ai-smell-rejection.md catalog are project-agnostic; if extracted as `addyosmani/agent-skills`-style upstream, they'd contribute back as the invariant layer the upstream skill currently mixes with web-specific implementation details.
- **Positive — stack-appendix docking convention pre-empts future fragmentation.** Without the convention, the first stack-skill author would face the temptation to absorb stack-specific patterns into this card; with the convention, the partition is contract.
- **Positive — `/paideia-frontend-overlays` cross-reference acknowledges the load-bearing composition.** Per [ADR 0073](0073-paideia-frontend-overlays-skill.md), every Paideia frontend pass runs both skills. The composition is explicit, not implicit.
- **Cost — manual invocation only.** Per `disable-model-invocation: true`. Mirrors [ADR 0070](0070-project-wired-review-skill.md)'s acknowledgement; same mitigation (AI may surface as a suggestion on frontend changes; user confirms).
- **Cost — three-skill invocation surface for full Paideia review.** A complete Paideia frontend review invokes `/frontend-discipline` + `/paideia-frontend-overlays` + `/review` (and `/security-review` for security-sensitive surfaces). Acceptable: each addresses an orthogonal concern; the modular partition is the point.
- **Cost — empty until stack-skills land for full verification.** Some invariant findings (especially accessibility) want stack-specific verification recipes. Until stack-skills exist, the reviewer applies invariants using available platform tools; the gap is honest, not silent — `accessibility-invariants.md` names it explicitly.
- **Cost — future stack-skills are work this skill doesn't do.** `frontend-swiftui` for Apple platforms; `frontend-web` for the marketing site + graph visualizer; both are deliberately deferred to when their stacks open. The decision is "land the invariants now, defer the stack-specifics" — not "skip the stack-specifics permanently".
- **Out-of-scope — visual-identity content commitment.** This skill enforces *discipline against an authored visual identity* (when one exists). The *content* (palette specs, type system, motif catalog) is a future product-side ADR. Per [ADR 0073](0073-paideia-frontend-overlays-skill.md), the overlay skill references prototype-stage direction; the universal skill stays content-agnostic.
- **Out-of-scope — performance budget catalogs.** Concern 7 (performance) names *principles* (no jank, profile-before-claiming); concrete budgets (Core Web Vitals thresholds, SwiftUI frame-budget specifics) live in [Issue #79](https://github.com/StarshipSuperjam/paideia/issues/79)'s `performance-optimization` skill (trigger-gated: deployable surface exists).
- **Out-of-scope — stack-specific accessibility tooling.** Xcode Accessibility Inspector workflow, browser DevTools Lighthouse runs, axe-core integration — all stack-specific; live in future stack-skills per the docking convention.

### Interaction with existing layers

- **vs. `/review` ([ADR 0070](0070-project-wired-review-skill.md)):** `/review` covers code-quality across all code (five axes: correctness, readability, architecture, depth-0 security, depth-0 performance). `/frontend-discipline` covers UI-engineering-specific judgments orthogonal to code-quality (visual smell, accessibility invariants, token integrity, etc.). Both compose on frontend changes; neither substitutes for the other.
- **vs. `/security-review` ([ADR 0071](0071-project-wired-security-review-skill.md)):** Orthogonal. `/security-review` covers OWASP-style security. Some frontend surfaces (auth screens, form handling, content rendering with untrusted input) benefit from both; the OWASP walk and the UI-engineering walk produce different findings.
- **vs. `/paideia-frontend-overlays` ([ADR 0073](0073-paideia-frontend-overlays-skill.md)):** Composition partner — invariant core (this skill) + project-tailoring (overlays). Authored as a pair in this session; expected to be invoked as a pair on every Paideia frontend pass.
- **vs. `validate.py`:** No interaction. The validator gates Python + SQL + structural-shape concerns; the frontend discipline is human-invoked.
- **vs. future stack-skills (`frontend-swiftui`, `frontend-web`):** Dock alongside via the docking convention named in `accessibility-invariants.md`. The invariant core stays universal; stack-skills carry stack-specific verification recipes. No skill modifies another; addition is sibling-creation, not core-extension.
- **vs. future `/ship` ([Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76)):** This skill is one of the skills `/ship` will compose for frontend changes. The composition surface is the same as for `/review` + `/security-review`.

### Empirical record

**S-0135 (authoring):** `.claude/skills/frontend-discipline/SKILL.md` + `ai-smell-rejection.md` + `accessibility-invariants.md` committed at HEAD. The skill has not yet been invoked against a real change in this session.

**First-invocation verification (pending).** The first `/frontend-discipline` invocation against substantive frontend code is the empirical exercise. Expected: structured Markdown report walking the seven invariants, severity tiers, project-overlay cross-reference, anti-rationalization self-check. Verification recorded as a follow-up commit to this ADR's "Empirical record" subsection, or in the invoking session's `outcome_summary`. Mirrors [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md)'s "First-PR-arrival verification (pending)" pattern.

Natural near-term occasions per the plan ([`~/.claude/plans/zippy-discovering-dewdrop.md`](#)): marketing-site authoring sessions (web stack); knowledge-graph visualizer authoring sessions (web stack); Phase 6 SwiftUI entry (Apple stack; gated behind OQ-DEC1).

## See also

- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; this skill is a recipe.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise gate; trigger-criterion evaluation above (zero criteria; no readiness note required).
- [ADR 0070](0070-project-wired-review-skill.md) — `/review` skill; severity-tier and change-size rubrics reused; shared anti-rationalization table cross-referenced.
- [ADR 0071](0071-project-wired-security-review-skill.md) — `/security-review` skill; orthogonal but composable.
- [ADR 0073](0073-paideia-frontend-overlays-skill.md) — `/paideia-frontend-overlays` companion (project-tailoring module); same Issue #75 split.
- [ADR 0034 (product)](../../product/adr/0034-discovery-planning-engagement-triad.md) — triad shape; consumed by ADR 0073 overlay 1.
- [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) — platform commitment (SwiftUI primary; commitment 1 preserves ADR 0035's platform language verbatim and, per the S-0154 scope clarification resolving [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106), explicitly scopes "no web app" to the consumer product distribution channel — marketing-site + graph-viz web surfaces are operational not product and are not foreclosed).
- [`.claude/skills/frontend-discipline/SKILL.md`](../../.claude/skills/frontend-discipline/SKILL.md) — the skill itself.
- [`.claude/skills/frontend-discipline/ai-smell-rejection.md`](../../.claude/skills/frontend-discipline/ai-smell-rejection.md) — companion card; AI visual smell catalog.
- [`.claude/skills/frontend-discipline/accessibility-invariants.md`](../../.claude/skills/frontend-discipline/accessibility-invariants.md) — companion card; accessibility invariants + stack-appendix docking convention.
- [`.claude/skills/review/anti-rationalization.md`](../../.claude/skills/review/anti-rationalization.md) — shared severity-rubric false-claim table.
- [Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) — closes this ADR (jointly with ADR 0073).
- [Issue #76](https://github.com/StarshipSuperjam/paideia/issues/76) — future `/ship` orchestrator that will compose this skill.
- [Issue #79](https://github.com/StarshipSuperjam/paideia/issues/79) — future `performance-optimization` skill (trigger-gated); concern 7 of this skill defers concrete budgets there.
- Pattern source: `addyosmani/agent-skills/skills/frontend-ui-engineering/SKILL.md` + `references/accessibility-checklist.md` (adapted — invariant-only body; stack-specifics deliberately omitted per the modular-architecture principle).
