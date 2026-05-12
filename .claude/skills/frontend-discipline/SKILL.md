---
name: frontend-discipline
description: Run a project-agnostic frontend UI engineering review — seven invariant concerns (AI visual smell, accessibility invariants, design-token integrity, state-flow hierarchy, composition, adaptive layout, performance posture). Severity tiers, change-size discipline, and structured Markdown report shared with `/review`. Stack-agnostic — composes with project-tailoring skills (e.g., `/paideia-frontend-overlays`) and future stack-specific skills (`frontend-swiftui`, `frontend-web`) as those open. Invoke deliberately on any frontend change.
disable-model-invocation: true
---

# frontend-discipline

> Project-agnostic frontend UI engineering discipline. The doctrine is this SKILL.md per [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md) — no separate Layer 1 ops-doc, because the skill body IS the discipline. Reference cards [`ai-smell-rejection.md`](ai-smell-rejection.md) and [`accessibility-invariants.md`](accessibility-invariants.md) carry the expanded rubrics for concerns 1 and 2. The anti-rationalization table is shared with [`/review`](../review/anti-rationalization.md) and [`/security-review`](../security-review/SKILL.md).
>
> **Composition.** This skill is the **invariant core** of the *core-invariant-plus-project-tailoring* architectural pattern. Project-specific findings (triad shape, rendering policy, visual-identity direction, pedagogical-graph rendering norms) live in [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md). Stack-specific verification surfaces (VoiceOver vs. screen-readers vs. TalkBack; SwiftUI size classes vs. CSS media queries; SF Symbols vs. Lucide vs. Material) live in future sibling skills (`frontend-swiftui`, `frontend-web`, etc.) that dock alongside this one as each stack actually opens. Until those open, the invariants in this skill are sufficient — they name *principles*, not *implementations*.

## When to invoke

A `frontend-discipline` pass is warranted on any non-trivial frontend change before merge. Compose with [`/review`](../review/SKILL.md) (which handles correctness / readability / architecture / depth-0 security / depth-0 performance for ALL code) and [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md) (project-specific). The three together cover the surface; this skill alone covers stack-agnostic UI judgment.

Trivial frontend changes that do NOT warrant this pass:

- Copy-only text edits with no markup/layout change
- Color-token value tweak inside the existing theme module (the change is one line in tokens, not a hundred-line component refactor)
- Asset-only updates (image, font, icon swap with no markup change)

Substantive frontend changes that DO warrant this pass:

- New components / views / screens
- Component/view substantial refactors (composition shift, prop signature change, state-flow rework)
- Theme / token system additions or restructuring
- New interaction surfaces (modals, drawers, popovers, sheets, forms)
- New accessibility-relevant primitives (focus management, keyboard handlers, assistive-input surfaces)
- New adaptive-layout treatments (compact vs. regular, responsive breakpoints, multitasking widths)
- Animation/motion authored or restructured
- Pre-Phase-6 surfaces (marketing site, knowledge-graph visualizer) when their authoring begins
- Phase 6 SwiftUI surfaces when that phase opens

## The seven invariant concerns

Walk every change against all seven concerns, in order. Each surfaces zero or more findings.

### 1. AI visual smell rejection

Default-AI aesthetics are recognizable across stacks and projects. Specifically named patterns to flag:

- Default purple/violet color schemes presented as "modern" without intentional brand justification
- Decorative gradient washes (full-page or per-card) used without purpose
- AI-sparkle/star/glow motifs absent integral product identity reasons
- Generic "centered hero with two CTAs and decorative background" landing patterns
- Emoji-as-icon under any condition (use the platform's icon system or custom iconography matching the brand)
- "AI-modern" mixed-display-font pairings without intentional brand register
- Tokens copied from generic design-system templates ("Tailwind defaults", "Material defaults") absent project-identity reasoning

The rubric is **intentional alternative or default** — when the choice was not intentional against a project visual identity, it defaults, and the default is recognizable. Defaults are findings.

Expanded catalog and frontend-specific anti-rationalization table: [`ai-smell-rejection.md`](ai-smell-rejection.md).

### 2. Accessibility (invariants)

Stack-agnostic accessibility requirements. The *verification surface* (VoiceOver, screen readers, TalkBack, Switch Control, browser DevTools) is stack-specific and lives in future stack-skills; the invariants don't.

- **Reachability.** Every interactive element reachable via the platform's assistive-input modalities (keyboard, switch, voice, alternative pointer). No focus traps.
- **Semantic clarity.** Each interactive element has an accessible name + role conveyed to assistive technology. Decorative content is marked as such. Reading/traversal order matches visual order or is explicitly authored.
- **No-color-alone.** State (selected, error, disabled, mastered, completed) is never communicated by color alone. Pair with shape, weight, symbol, label, or position.
- **Motion respect.** Animations gated behind the platform's reduce-motion preference. Auto-play, parallax, and decorative motion disable when the preference is set.
- **Contrast minima.** WCAG 2.1 AA equivalent: 4.5:1 for body text, 3:1 for large text and meaningful non-text content. Verified against the actual rendered context (background, overlay, hover/focus state).
- **Scaling.** Content reflows correctly when the user enlarges the system text size. No truncation at maximum scale that loses meaning.
- **Logical ordering.** Tab/swipe traversal order matches reading order. Custom focus management is explicit, not accidental.

Expanded rubric and stack-appendix docking convention: [`accessibility-invariants.md`](accessibility-invariants.md).

### 3. Design-token integrity

- No inline colors, spacing, typography, or radii in component code. Values resolve through a central theme/tokens module.
- Adding a value extends the tokens module first; using a new value requires it to exist in the module.
- Token names describe **role** (`color.surface.elevated`, `spacing.section`), not value (`color.gold-300`, `spacing.16`). Roles survive aesthetic revisions; values do not.
- "It's just one inline color" is a finding — token-discipline is binary. Once inlines proliferate, the theme becomes vestigial.

### 4. State-flow hierarchy

Choose the lowest level that works. Higher levels couple more components and harden change cost.

1. **Local** — within one component/view.
2. **Lifted** — held by the nearest common parent of components that share the state.
3. **Shared / observed** — a stateful object explicitly observed by consuming components (React's `useState`+context, SwiftUI's `@Observable`/`@ObservableObject`, etc.).
4. **Contextual / environmental** — passed through the platform's environment/context primitive when many distant consumers need read access.
5. **URL / persisted** — when state must survive navigation, deep-link, or session reload.
6. **Server / async** — fetched, cached, invalidated as a separate concern from client-rendering state.
7. **App-wide / singleton** — last resort, requires justification.

The named primitives differ per stack; the order does not. A component reaching for level 7 when level 1 would work is a `Required` finding.

### 5. Composition

- Component/view bodies under a size threshold appropriate to the stack (rule of thumb: ~150 lines of rendering logic; split before this). Larger bodies are split-before-merge.
- Single responsibility. A component that renders a list, fetches the list's data, and handles selection state is doing three jobs — split.
- Narrow props/initializers. Many props (>~6 unless wrapping one model object) signal the component is doing too much.
- Prefer children/slot composition over render-prop equivalents where the language supports both.

### 6. Adaptive layout

- Designed at the smallest target first; verified across each surface the product claims to target.
- "Looks fine on my screen" is a finding without verification at the boundary cases.
- Size-class / breakpoint logic explicit, not accidental. Conditional rendering for adaptation reads at the same level of clarity as the layout itself.
- Multitasking / split-screen / window-resize edge cases verified for the platforms that offer them.

### 7. Performance posture

- No jank during interaction. Frame budget respected at the platform's expected refresh rate.
- Assets sized appropriately. No 4096×4096 PNG used at 64×64 display size.
- Profile-before-claiming-fast. "I think it's fast" without measurement is a finding for any change to a hot path.
- N+1 fetches, unbounded loops, synchronous I/O on the rendering thread are `Critical`.

## Severity tiers

Reuse the [`/review`](../review/SKILL.md) tier rubric verbatim — same vocabulary across reviewing skills prevents calibration drift.

| Tier | Action |
|---|---|
| **Critical** | Blocks merge. Accessibility blocker (focus trap, missing label on primary action), data loss in UI state, broken interaction surface. |
| **Required** | Address before merge. Real UI/accessibility/architecture problem. (Default tier — no prefix.) |
| **Nit** | Optional. Spacing tweak, minor naming, micro-interaction polish. Author chooses. |
| **Optional** | Worth considering. A suggested alternative composition or token addition. |
| **FYI** | Informational. A pattern observation, a downstream-implication note. No action required. |

Tier inflation (everything is `Required`) and tier deflation (everything is `Nit`) are both failure modes. The honest read is the calibration.

## Change-size discipline

Reuse the [`/review`](../review/SKILL.md) thresholds (lines changed, additions + deletions, excluding rename diffs).

| Size | Action |
|---|---|
| **~100 lines** | Target. |
| **~300 lines** | Acceptable if logically unified. |
| **~1000 lines** | Too large. Split before merge. Strategies: by component-tree subtree, by horizontal slice (theme tokens before consumers), by vertical slice (data layer before render layer). |

## Process sequence

1. **Load context.** Read the plan file (if any), the touched ADRs (product-side visual-identity, triad, rendering-policy ADRs if Paideia), the touched theme/tokens module, the relevant component-tree neighborhood. Identify which stack-skills should also be invoked (`frontend-swiftui`, `frontend-web`) — if a stack-skill exists for the relevant stack, invoke it for the stack-specific verification surface.
2. **Walk the seven invariant concerns** in the order above. Each surfaces zero or more findings.
3. **Apply project-tailoring overlays.** Invoke [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md) (or whatever the project's tailoring skill is) for project-specific overlay findings. Do not duplicate the project-overlay findings here — keep the invariant pass and the overlay pass distinct so the modular partition stays clean.
4. **Categorize every finding by severity tier.**
5. **Verify the verification story.** Did the relevant platform-accessibility-check pass? Did manual testing happen across the target surface set? Were the size-class / breakpoint variants actually exercised?
6. **Emit the structured Markdown report** (next section). Self-check against [`../review/anti-rationalization.md`](../review/anti-rationalization.md).

## Output shape

A structured Markdown report. Sample:

```markdown
## `frontend-discipline` — <branch-name> @ <SHA-short>

**Change size:** N lines (M files). **Tier:** target / acceptable / too-large.

**Stack(s):** <SwiftUI / Web / Mixed>. **Stack-skill invoked:** <name or N/A>.

**Verification story:** platform-a11y-check <pass/fail>; manual cross-surface testing <list of surfaces verified>; reduce-motion / large-text / high-contrast preferences <tested?>.

### Findings (invariant concerns)

| Severity | Concern | Finding | File:Line | Suggested action |
|---|---|---|---|---|
| Critical | Accessibility | Primary CTA has no accessible name (icon-only) | path/to/file:42 | Add aria-label / accessibilityLabel |
| Required | AI visual smell | Default purple gradient on hero with no brand-identity justification | path/to/file:117 | Replace with token-based palette per project visual identity |
| Required | Design tokens | Inline `#FFD700` color value | path/to/file:88 | Lift to `color.accent.brand` token |
| Nit | Composition | Component body at 187 lines | path/to/file | Split or extract |

### Project-overlay pass

Run separately via the project's overlay skill. Findings recorded in that report; cross-referenced here:
- [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md) report: PASS / N findings

### Anti-rationalization self-check

- Reviewed against [`../review/anti-rationalization.md`](../review/anti-rationalization.md) + [`ai-smell-rejection.md`](ai-smell-rejection.md): no rationalizations applied.
```

Empty rows are fine. Do not invent findings.

## Failure modes this skill prevents

- **Defaults-as-design.** Components shipping with default purple, default gradient washes, default icon-set inclusions — invisible until measured against a deliberate alternative. The intentional-alternative-or-default rubric forces the measurement.
- **Accessibility-as-afterthought.** Authoring keyboard / screen-reader / contrast support after the visual design is locked, when retrofits cost 5–10x. The invariant pass surfaces missing accessibility at the same time as missing tokens, not later.
- **Token vestigialization.** A theme module exists; components inline values around it. The discipline check is binary — one inline value is a finding because tolerated inlines proliferate.
- **State-flow over-reach.** Reaching for app-wide state when local would suffice, hardening change cost. The hierarchy enforces lowest-level-that-works.
- **Composition bloat.** Component bodies that grew incrementally past the threshold, each commit a few lines, no single commit triggering the split. The size threshold catches the accumulated condition.
- **Stack-creep into the invariant.** Editing this skill to add SwiftUI-specific or web-specific patterns. Those belong in stack-specific sibling skills; the invariant stays universal.

## Failure modes this skill does NOT prevent

- **Wrong visual-identity choice.** The skill flags drift from an *authored* visual identity. If the visual identity itself is wrong, this is a product-side concern (visual-identity ADR), not a frontend-discipline concern.
- **Wrong product surface.** Adding a primary surface outside the product's surface contract (e.g., Paideia's triad). The project-tailoring skill catches this — [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md) for Paideia.
- **Stack-specific verification.** VoiceOver rotor-navigation, browser screen-reader simulation, platform-specific gesture conventions. Each stack-skill addresses its own verification surface.
- **Specification errors.** If the design or product spec is wrong, the review verifies against a wrong spec.

## See also

- [`ai-smell-rejection.md`](ai-smell-rejection.md) — companion reference card; expanded catalog of AI visual smell + frontend-specific anti-rationalization table.
- [`accessibility-invariants.md`](accessibility-invariants.md) — companion reference card; expanded accessibility invariants + stack-appendix docking convention.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared severity-rubric false-claim table.
- [`/paideia-frontend-overlays`](../paideia-frontend-overlays/SKILL.md) — project-tailoring sibling for Paideia. Always run alongside this skill on Paideia changes.
- [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md) — the citable contract this skill operationalizes.
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition; this skill is a recipe.
- [`/review`](../review/SKILL.md) — five-axis review skill; composes with this one (`/review` covers code; `frontend-discipline` covers UI judgment).
- [`/security-review`](../security-review/SKILL.md) — depth-N security review; composes for security-sensitive frontend surfaces (auth screens, form handling, content rendering with untrusted input).
- Pattern source: `addyosmani/agent-skills/skills/frontend-ui-engineering/SKILL.md` (adapted, not cloned — invariant-only body; stack-specifics and project-specifics deliberately omitted per the modular-architecture principle).
