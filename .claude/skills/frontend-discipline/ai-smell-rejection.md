# AI visual smell rejection — reference card

> Companion reference for [`/frontend-discipline`](SKILL.md). Expands concern 1 from the SKILL.md body with the recognizable patterns of default-AI aesthetics + a frontend-specific anti-rationalization table.
>
> **Scope.** This card carries *UI-specific* rationalizations distinct from the shared severity-rubric table at [`../review/anti-rationalization.md`](../review/anti-rationalization.md). Both are consulted on every frontend review pass: the shared table for general review claims; this table for UI-specific dismissals.

## The catalog of recognizable AI visual smell

AI defaults are recognizable across stacks. They surface when the visual choice was not *intentional* against an authored brand identity. The patterns below are the most reliable surface markers — flag any that appear without a project-specific reason.

### 1. Default purple/violet schemes

The signature AI default. Recognizable as:

- A primary action color in the `#6B46C1`–`#7C3AED`–`#A855F7` band (Tailwind's `purple-700`/`violet-600`/`purple-500` family)
- Gradients in the `purple→pink`, `violet→indigo`, or `purple→blue` registers
- "Modern" framing — purple positioned as "the current/trendy choice"

**Finding tier:** `Required` when used without a project visual-identity ADR justification; `Critical` when used in product surfaces marketed as having a distinct visual identity that doesn't include purple.

The pattern surfaces because frontier-AI training data over-represents recent SaaS landing pages that converged on this palette. The same training data is the source of the visual-default. Recognizing it is the first defense.

### 2. Decorative gradient washes

Any gradient where the *purpose* is "looks modern" rather than serving a specific visual function (focal hierarchy, surface elevation, semantic meaning):

- Full-page background gradients with no content-relationship
- Gradient on every card, every button, every hero
- Gradient text headers with no contrast verification against the background gradient
- "Animated mesh" gradients in landing-page hero sections

A gradient can be intentional (a single product surface uses a subtle background gradient to signal "this is the welcome screen, not the working screen"). Decorative gradients fail the intentionality test.

**Finding tier:** `Required` for decorative; allowed for purposeful with named reason.

### 3. AI-sparkle / AI-star / AI-glow motifs

The visual shorthand for "this is an AI feature":

- Sparkle/star icons attached to AI-feature CTAs ("Generate", "Suggest")
- Glow effects on AI-affordance surfaces
- Animated shimmer on AI-loading states (specifically the "iridescent shimmer" rather than a project-designed loader)
- Particle effects accompanying AI outputs

Two issues compound: (a) these are AI defaults; (b) they signal "AI feature" which prejudices the user against the surface as "the AI is doing it" rather than "this is the product". Flag absent a deliberate product decision to brand AI features visually (rare and dangerous — usually wrong).

**Finding tier:** `Critical` for surfaces where AI involvement should not be visually marked; `Required` for surfaces where it should but the marking matches generic AI-default rather than project identity.

### 4. Generic "centered hero with two CTAs and decorative background"

The landing-page archetype that frontier-AI defaults toward:

- Centered headline + subtitle + two CTA buttons (primary + secondary) + decorative gradient/illustration
- The headline pattern: "The [adjective] way to [verb] your [noun]" or "[Verb] better [noun]"
- Subtitle as one-sentence expansion of headline
- Buttons: "Get Started" + "Learn More" (or close variants)
- Decorative element: abstract gradient mesh, generic illustration of "people using device", or stock pattern

Recognizable as a Bootcamp Landing Page Template. The pattern is so dominant in training data that frontier AI proposes it for any "landing page" prompt unless the alternative is explicitly authored.

**Finding tier:** `Required`. The fix is not "tweak the hero"; it's "author a project-specific landing pattern from the brand identity outward."

### 5. Emoji-as-icon

Using Unicode emoji glyphs where a true icon (platform icon system, custom iconography matching brand) belongs:

- Section markers (🎯 for "goals", 🚀 for "launch", 📊 for "data")
- Status indicators (✅ for done, ❌ for error, ⚠️ for warning, in UI chrome)
- Inline button glyphs

Issues: (a) emoji rendering varies wildly across platforms (Apple's 🎯 differs from Google's, Microsoft's, Twitter's); (b) emoji set is uncurated — a thirty-emoji UI looks chaotic; (c) emoji semantic meaning drifts (🚀 in a serious educational product reads juvenile); (d) accessibility for screen readers depends on emoji-to-name mapping which is inconsistent.

**Finding tier:** `Required` always. The remediation is the platform icon system (SF Symbols on Apple, Material Symbols on Android, Lucide/Heroicons/etc. on web) OR custom iconography matching the brand.

Exception: emoji *in user-authored content* (chat messages, comments, learner-authored notes) is content, not chrome — different concern. This card targets chrome only.

### 6. "AI-modern" mixed display fonts

The pattern of pairing a "modern" geometric sans (Inter, Geist, Manrope, DM Sans) as a body font with a "display" treatment that's either: a heavier weight of the same family, OR a script/serif "accent" font with no brand register justification:

- Display font chosen for "looks AI-modern" rather than authored brand
- Multiple display fonts in one product surface with no role-based reason
- Display font tracking/spacing copied from generic SaaS template defaults

**Finding tier:** `Required` when the type pairing was not authored against a brand register.

### 7. Generic design-system template tokens

Component libraries ship with default themes (Tailwind's default colors, Material's default theme, shadcn/ui's default tokens, SwiftUI's default colors). Using the defaults *verbatim* signals the project did not author its own palette:

- `theme.colors.primary = #6B46C1` (Tailwind violet-700 default)
- `Color.accentColor` left at SwiftUI's system default
- shadcn/ui's `.css` palette unchanged

**Finding tier:** `Required` until a project visual-identity ADR commits the palette.

## Frontend-specific anti-rationalization table

UI-specific rationalizations that aren't covered by the shared severity-rubric table at [`../review/anti-rationalization.md`](../review/anti-rationalization.md). Consulted during finding-downgrade temptations specifically for UI judgment.

| False claim | Reality check |
|---|---|
| "Looks fine on my screen." | Test the actual target surfaces (size classes, breakpoints, devices) before claiming fine. The phrase is the most common cover for unverified single-context rendering. |
| "I'll add accessibility later." | Retrofit costs 5–10x author-time. The keyboard/screen-reader/contrast/scaling concerns are authored first, not last. "Later" is structurally a deferral that doesn't ship. |
| "Tab order doesn't matter for this surface." | Half of platform-accessibility audits fail on traversal-order alone. Tab order matters everywhere the user can reach via assistive input. |
| "Default purple is modern." | Default purple is AI-smell, not modern. "Modern" is a rationalization for "defaulted." If the palette was authored, name the ADR; otherwise, the choice is a finding. |
| "One inline color won't matter." | One inline color leads to ten. Token discipline is binary — once tolerated, inlines proliferate. The theme becomes vestigial. |
| "Animation makes it feel polished." | Animation that ignores reduce-motion preferences fails accessibility. Animation that ignores the platform's frame budget creates jank. Polish is restraint, not motion. |
| "I'll test on a real device later." | "Later" means "never" for non-development surfaces (large text size, high contrast, switch-control). The boundary cases discover problems the developer device doesn't. |
| "The dark-mode variant works the same way." | Color contrast requirements verify against the *rendered context*. Body text against `surface.elevated` in light mode and `surface.elevated` in dark mode are different pairings; both verify. |
| "Component looks fine in isolation." | Composition reveals layout problems isolation hides — neighbor spacing, alignment with sibling components, focus-ring overlap. Test in the actual composition. |
| "AI-generated UI is usually fine." | AI-generated UI carries *every* default visual smell because the training data does. AI-generated UI requires *more* scrutiny, not less. The author and the AI share the defaults. |
| "Sparkle/star icon is just the AI affordance convention." | A "convention" used by every recent AI product is a default, not a convention. Either the product has a distinct identity (use it) or it doesn't (build one). |
| "It works on iPad / it works on desktop, that's the primary surface." | Compact size class / mobile breakpoints aren't optional verifications even when the "primary" surface is larger — they catch composition problems the larger surface masks. |
| "The framework default is the standard." | Framework defaults are starting points, not standards. Every shipped product authors its palette, type, spacing, and motion away from framework defaults. Defaults shipped untouched are findings. |
| "Lighter font weight reads more elegant." | Below 14pt regular weight or 16pt light weight, contrast and scaling fail at large-text accessibility settings. Elegance is calibrated against legibility, not extracted from it. |
| "Emoji is universal." | Emoji is universally inconsistent across platforms, fonts, accessibility-tool readings, and cultural-meaning drift. Use the platform's icon system. |

## How to use this card

1. On every finding tempted toward downgrade or dismissal where the reason involves visual-judgment or AI-output dismissal, consult this card.
2. Consult the shared table at [`../review/anti-rationalization.md`](../review/anti-rationalization.md) for general review-finding rationalizations (severity-tier inflation/deflation, validate-passed-ship-it, etc.).
3. If neither table has the rationalization, **write the exception into the review report's anti-rationalization self-check section explicitly**. The act of writing the exception is the calibration.

## Why this card is separate from the shared table

The shared table at [`../review/anti-rationalization.md`](../review/anti-rationalization.md) is consumed by [`/review`](../review/SKILL.md), [`/security-review`](../security-review/SKILL.md), and this skill — adding frontend-specific rows there would expand a surface used by reviewers who never invoke this skill. The modular partition (per [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md)) keeps frontend-specific rationalizations colocated with the frontend skill. When `/security-review`-style sibling skills emerge for other concerns (e.g., a future API-discipline skill), they author their own rationalization cards rather than expanding the shared one.

## See also

- [`SKILL.md`](SKILL.md) — `/frontend-discipline` recipe; concern 1 (AI visual smell rejection) expanded here.
- [`accessibility-invariants.md`](accessibility-invariants.md) — companion card; concern 2 (Accessibility) expanded there.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared severity-rubric false-claim table.
- [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md) — contract.
- Pattern source: `addyosmani/agent-skills/skills/frontend-ui-engineering/references/` (adapted patterns; UI-specific rows authored from the source plus the modular-architecture principle).
