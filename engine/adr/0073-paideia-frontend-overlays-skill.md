# ADR 0073 — Project-wired `/paideia-frontend-overlays` skill (project tailoring)

- **Status:** Accepted
- **Date:** 2026-05-12
- **Deciders:** S-0135

## Context

The project-tailoring half of the [Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) split. The invariant-core half is [ADR 0072](0072-frontend-discipline-skill.md); read that first for the full Issue #75 split rationale and the *core-invariant-plus-project-tailoring* architectural principle the user surfaced during S-0135 planning.

Paideia carries seven product-side contracts that govern how the frontend may render and interact:

- **[ADR 0034 (product)](../../product/adr/0034-discovery-planning-engagement-triad.md)** — Discovery / Planning / Engagement triad as the only primary surfaces. New primary surfaces require superseding.
- **[ADR 0027 (product)](../../product/adr/0027-rendering-policy-prompt-layer-contract.md)** — Forbidden-token rules for AI-instructor voice (no mastery-state labels, prerequisite-framing prose, scaffolding-distance mentions, graph-version references, sphere/world/map/trophy metaphors).
- **[ADR 0028 (product)](../../product/adr/0028-input-side-scope-structural-not-prompt.md)** — Three bounded engagement contexts (concept engagement, diagnostic, BYOB close reading); no general chat surface.
- **[ADR 0013 (product)](../../product/adr/0013-mastery-verification-organic-escalation.md)** — Mastery rendered quietly in syllabus context; never celebrated, never separate trophy surface.
- **[ADR 0033 (product)](../../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md)** — Mission realignment foreclosing decoration / spectacle / engagement-loop framing.
- **[ADR 0032 (product)](../../product/adr/0032-personal-project-disposition.md)** — Corruption-vector identification: retention/conversion mechanics pull pedagogy off-mission.
- **[ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md)** — Apple-platform product distribution (SwiftUI; iPhone + iPad first-class; Mac via Designed-for-iPad). Commitment 1 preserves ADR 0035's platform language verbatim; the S-0154 scope clarification (resolving [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106)) scopes "no web app" to the consumer product distribution channel — marketing-site + graph-viz web surfaces are operational not product and are not foreclosed.

A universal frontend-engineering skill ([ADR 0072](0072-frontend-discipline-skill.md)) does not know any of these. Without a project-tailoring overlay, a generic frontend pass:

- Would not flag a new "Library" or "Trophy" primary surface as a contract violation against ADR 0034.
- Would not catch forbidden tokens in AI-instructor copy per ADR 0027.
- Would not flag a streak counter / leaderboard / "X-day streak broken" surface as a mission-realignment violation per ADR 0033 + ADR 0032.
- Would not catch "mastery achieved" celebration surfaces violating ADR 0013.

The project-tailoring overlay is where these project-specific findings live. Per the user's standing architectural principle, the overlay is a **separate skill**, not a section inside the universal skill — modularity makes expansion/retraction possible without rebuilding.

**Visual-identity context (working direction, not yet ADR-locked):** The user shared frontend prototypes at S-0135 — a logo banner and an Apple-style app icon, both establishing a classical-scholarly aesthetic with a gold-on-dark palette (gold with material-suggesting tonal variation; near-black navy ground), Greek-pedagogical iconography (Ionic column supporting an abstract knowledge-graph lattice), restrained ornamentation, thin-line geometric treatment, and classical serif wordmark with Greek-letter allusions. **This is prototype-stage**, not an authored visual-identity ADR. The skill references the direction as load-bearing context for finding-discussions but does NOT lock the direction in as Critical-tier contract; deviations are findings-to-discuss until/unless a product-side visual-identity ADR commits the palette and motifs. When that ADR lands, this skill cross-references it and severity tightens.

Pattern source: same as [ADR 0072](0072-frontend-discipline-skill.md) (`addyosmani/agent-skills`); project-specific overlays authored entirely from Paideia's product ADRs.

## Decision

A new project Skill at `.claude/skills/paideia-frontend-overlays/SKILL.md` carries the recipe for Paideia-specific frontend overlays. The doctrine is the SKILL.md body — no separate Layer 1 ops-doc, no reference cards (kept tight; if a section grows large enough to warrant extraction, split then per the precedent at [ADR 0071](0071-project-wired-security-review-skill.md)).

`disable-model-invocation: true` per [ADR 0044](0044-skill-conversion-recipe-vs-reference.md). Composes with [`/frontend-discipline`](0072-frontend-discipline-skill.md) — both should be invoked on Paideia frontend changes; the invariant-core surfaces universal findings, this skill surfaces project-specific findings.

### 1. Ten overlays

The SKILL.md walks every change against ten overlays in order: triad-only primary surfaces, rendering-policy compliance, no engagement-loop dark patterns, quiet mastery rendering, visual-identity working direction (prototype-stage), iconography discipline, pedagogical-graph rendering norms, scope_lock awareness (inherited from [`/review`](0070-project-wired-review-skill.md) overlay), ADR-citation requirement (inherited), MemPalace decision-drawer check (inherited).

The first seven are project-specific. The last three are inherited from the existing `/review` overlay set, restated here because invocation context may differ (the invoker may run `/paideia-frontend-overlays` without invoking `/review`).

### 2. Visual-identity working direction is prototype-stage

Overlay 5 explicitly carries provisional contract scope. Findings against the working direction (palette, iconography motif, typography register) are `FYI` until a visual-identity ADR lands; only direct misuse of the brand mark at component-decoration scale is `Required` pre-ADR. When the ADR lands, the overlay updates: references move from prose-description to ADR-citations; severities tighten; the working-direction text is replaced with ADR-cited specs.

The design choice is honest about the provisional layer. Pre-S-0135, no visual identity was authored at all; a skill that flagged every default-palette use as `Critical` would block all frontend work before the visual identity itself settled. Conversely, a skill that ignored visual identity entirely would let AI-default purple gradients ship. The `FYI`-pre-ADR / `Required`-post-ADR calibration threads the gap.

### 3. Naming convention for project-tailoring modules

The `paideia-` prefix on this skill's directory name signals the project-tailoring layer of an invariant-plus-tailoring pair. No existing skill uses this convention; this ADR names it so future project-tailoring modules follow consistently. Future Paideia-specific overlay skills (e.g., a `paideia-pedagogy-overlays` if pedagogy-specific patterns warrant their own surface beyond the seven overlays here) would use the same prefix.

Stack-specific sibling skills (e.g., a future `frontend-swiftui`, `frontend-web`) do *not* use a project prefix — they are stack-specific, not project-specific. The prefix discipline keeps the partition (invariant / project / stack) legible at the filename level.

### 4. Composition contract explicit in SKILL.md body

The SKILL.md opens with a "Composition contract" section naming that this skill assumes [`/frontend-discipline`](0072-frontend-discipline-skill.md) is also invoked (or the user is taking responsibility for the universal layer separately). The composition is structural, not advisory — the project-overlay skill does not duplicate invariant-pass findings.

### 5. Structured Markdown report output

Same shape as [ADR 0072](0072-frontend-discipline-skill.md)'s report — severity tier / overlay number / finding / file:line / suggested-action columns. Plus an inherited-overlay grid (scope_lock, ADR-citation, MemPalace decision drawer) and an anti-rationalization self-check against the shared severity table plus the UI-specific table at [`.claude/skills/frontend-discipline/ai-smell-rejection.md`](../../.claude/skills/frontend-discipline/ai-smell-rejection.md).

## Consequences

### Trigger criterion evaluation (per [ADR 0053](0053-mechanism-first-exercise-gate.md))

The `/paideia-frontend-overlays` skill adoption is evaluated against the four cross-cutting criteria from [ADR 0053](0053-mechanism-first-exercise-gate.md):

- ❌ Criterion 1 — new session mode. **No.** Invoked from any existing session mode at the user's discretion.
- ❌ Criterion 2 — new validator soft-warn category. **No.** No `validate.py` soft-warns introduced.
- ❌ Criterion 3 — new state file the boot procedure reads. **No.** No new file under `engine/session/` or anywhere the boot procedure reads.
- ❌ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **No.** This adoption touches `.claude/skills/paideia-frontend-overlays/SKILL.md` + this ADR + `engine/adr/README.md` row + `engine/STATE.md` row + `engine/ENGINE_LOG.md` entry. Five surfaces; one Skill file, this ADR, three index/state entries. Zero ops-doc files; zero tooling files. Under the threshold.

Zero criteria satisfied → **no first-exercise readiness note required.** Same precedent as [ADR 0069](0069-dependabot-pip-and-actions-ecosystems.md), [ADR 0070](0070-project-wired-review-skill.md), [ADR 0071](0071-project-wired-security-review-skill.md), and [ADR 0072](0072-frontend-discipline-skill.md). The Issue #75 body's pre-S-0135 readiness-note assertion is overridden by the explicit rubric evaluation here and in ADR 0072.

First real invocation of `/paideia-frontend-overlays` against substantive Paideia frontend code is the empirical verification. Same pending pattern as the sibling skills.

### Other consequences

- **Positive — project tailoring is separately invocable and removable.** Per the user's standing architectural principle. If product surface scope changes (e.g., a future supersession of ADR 0034 introduces a fourth primary surface), the change lives in this skill, not in `/frontend-discipline`. If the entire project pivots, this skill could be deleted without touching the invariant core.
- **Positive — visual-identity provisional contract layer is honest.** Pre-ADR, overlay 5 carries `FYI` severities so it doesn't block work; the contract layer is provisional and named as such. Post-ADR (when visual identity is committed), the layer tightens. No false-precision in the interim, no blanket-pass in the interim — the calibration is explicit.
- **Positive — `paideia-` naming convention preserves modular legibility.** Future authors see the prefix and understand the partition without needing to read every skill's body. Three-tier legibility: no-prefix = invariant; `paideia-` prefix = project tailoring; stack-suffix (`-swiftui`, `-web`) = stack-specific.
- **Positive — engagement-loop dark patterns flagged at proposal point.** Overlay 3 catches "let's add a streak counter" before authoring begins. Per the user feedback memory "no preemptive deferral without a concrete blocker": the catch is at proposal time, not at retrofit time.
- **Positive — inheritance from `/review` overlay grid reused, not duplicated.** Overlays 8–10 (scope_lock, ADR-citation, MemPalace decision drawer) restate the `/review` overlay set for skill-context completeness. A reviewer using only this skill (without `/review`) still gets the inherited surface.
- **Cost — manual invocation only.** Per `disable-model-invocation: true`. Same cost as siblings.
- **Cost — composition pair coordination.** A reviewer must invoke both `/frontend-discipline` and `/paideia-frontend-overlays`; missing one is a partial review. Mitigation: AI surfaces the pair as a suggestion on Paideia frontend changes (user confirms).
- **Cost — visual-identity provisional layer requires future tightening.** When the visual-identity ADR lands, this skill needs an update (references move, severities tighten). The update is small and explicitly named here; the cost is the maintenance discipline.
- **Cost — overlay surface may grow.** If a future pedagogy concern doesn't fit the existing ten overlays, this skill grows or a new sibling skill (`paideia-pedagogy-overlays`) is authored. The prefix discipline accommodates either.
- **Out-of-scope — backend / API / data-layer concerns.** Those use [`/review`](0070-project-wired-review-skill.md) + [`/security-review`](0071-project-wired-security-review-skill.md). This skill is frontend-overlay-only.
- **Out-of-scope — stack-specific patterns.** Per [ADR 0072](0072-frontend-discipline-skill.md)'s docking convention.
- **Out-of-scope — content commitments.** The skill enforces discipline against authored contracts (ADRs). The contracts themselves are product-side ADR work, not engine-side.

### Interaction with existing layers

- **vs. [`/frontend-discipline`](0072-frontend-discipline-skill.md):** Always invoked alongside. Invariant pass (that) + project pass (this) compose for full coverage. The skills do NOT duplicate findings — a universal finding stays in the invariant pass; a project-specific finding stays here.
- **vs. [`/review`](0070-project-wired-review-skill.md):** Orthogonal. `/review`'s Paideia overlays (scope_lock, ADR-citation, MemPalace) overlap with overlays 8–10 here; this is intentional restatement for skill-context completeness. A reviewer using only this skill (without `/review`) still gets the inherited overlays applied.
- **vs. [`/security-review`](0071-project-wired-security-review-skill.md):** Orthogonal. Frontend security concerns route to `/security-review`'s OWASP walk; project-specific frontend concerns route here.
- **vs. future stack-skills (`frontend-swiftui`, `frontend-web`):** Stack-skills carry stack-specific verification; this skill carries project-specific overlays. Composition: all three (universal + project + stack) on full frontend reviews.
- **vs. product ADRs (0013, 0027, 0028, 0032, 0033, 0034, 0065):** This skill operationalizes the contracts. ADR amendments propagate here; when a product ADR is superseded or amended, this skill's relevant overlay updates in the same session (per [ADR 0041](0041-cascade-analysis-discipline.md) cascade discipline).

### Empirical record

**S-0135 (authoring):** `.claude/skills/paideia-frontend-overlays/SKILL.md` committed at HEAD. The skill has not yet been invoked against a real change in this session.

**First-invocation verification (pending).** First `/paideia-frontend-overlays` invocation against substantive Paideia frontend code is the empirical exercise. Expected: structured Markdown report walking the ten overlays, severity tiers (with overlay 5 producing `FYI` findings pre-visual-identity-ADR), inherited-overlay grid, anti-rationalization self-check. Natural near-term occasions: marketing-site authoring sessions (web stack — particularly overlay-5 visual-identity discussion findings expected); knowledge-graph visualizer authoring sessions (overlay 7 pedagogical-graph rendering norms exercised); Phase 6 SwiftUI entry (full overlay walk; expected to surface many overlay 1 / 2 / 3 / 4 findings as the first frontend code lands).

Visual-identity ADR (when authored, future product session): triggers a cascade per [ADR 0041](0041-cascade-analysis-discipline.md) — this skill's overlay 5 updates to reference the ADR; severities tighten. The update is small and bounded; this ADR explicitly anticipates it.

## See also

- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; this skill is a recipe.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise gate; trigger-criterion evaluation above (zero criteria; no readiness note required).
- [ADR 0070](0070-project-wired-review-skill.md) — `/review` skill; overlay set partially inherited (scope_lock, ADR-citation, MemPalace decision drawer).
- [ADR 0071](0071-project-wired-security-review-skill.md) — `/security-review` skill; orthogonal but composable; sibling-pattern source for two-ADR-one-session.
- [ADR 0072](0072-frontend-discipline-skill.md) — `/frontend-discipline` companion (invariant core); same Issue #75 split; always invoked alongside.
- [ADR 0041](0041-cascade-analysis-discipline.md) — cascade discipline that governs how product-ADR changes propagate into this skill.
- [ADR 0013 (product)](../../product/adr/0013-mastery-verification-organic-escalation.md) — quiet mastery rendering (overlay 4).
- [ADR 0027 (product)](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — rendering policy (overlay 2).
- [ADR 0028 (product)](../../product/adr/0028-input-side-scope-structural-not-prompt.md) — bounded engagement contexts.
- [ADR 0032 (product)](../../product/adr/0032-personal-project-disposition.md) — corruption-vector identification underlying overlay 3.
- [ADR 0033 (product)](../../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md) — mission realignment underlying overlay 3.
- [ADR 0034 (product)](../../product/adr/0034-discovery-planning-engagement-triad.md) — triad shape (overlay 1).
- [ADR 0065 (product)](../../product/adr/0065-oss-pivot-and-byok-disposition.md) — platform commitment (Apple SwiftUI primary; commitment 1 preserves ADR 0035's platform language verbatim). Commitment 1's S-0154 scope clarification (resolving [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106)) settles "no web app" as scoped to the consumer product distribution channel — marketing-site + graph-viz web surfaces are operational not product and are not foreclosed.
- Future visual-identity product ADR — overlay 5 cross-references when authored.
- [`.claude/skills/paideia-frontend-overlays/SKILL.md`](../../.claude/skills/paideia-frontend-overlays/SKILL.md) — the skill itself.
- [`.claude/skills/frontend-discipline/SKILL.md`](../../.claude/skills/frontend-discipline/SKILL.md) — composition partner.
- [Issue #75](https://github.com/StarshipSuperjam/paideia/issues/75) — closes this ADR (jointly with ADR 0072).
- Pattern source: `addyosmani/agent-skills/skills/frontend-ui-engineering/SKILL.md` (adapted — project tailoring authored entirely from Paideia's product ADRs).
