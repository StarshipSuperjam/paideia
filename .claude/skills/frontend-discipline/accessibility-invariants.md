# Accessibility invariants — reference card

> Companion reference for [`/frontend-discipline`](SKILL.md). Expands concern 2 from the SKILL.md body with the stack-agnostic accessibility requirements + the docking convention for future stack-specific verification appendices.
>
> **Scope.** Accessibility *invariants* — the requirements that hold regardless of stack. The *verification surface* (VoiceOver rotor, browser screen-reader, TalkBack actions, Switch Control gestures, hardware-keyboard navigation, automated accessibility scanners) is stack-specific and lives in sibling stack-skills (e.g., a future `frontend-swiftui` carries SwiftUI-specific accessibility verification; a future `frontend-web` carries WAI-ARIA / HTML semantics / browser-DevTools verification). This card carries the invariants; the docking section at the end names how stack-specific appendices should be added.

## The seven invariants

Each invariant produces zero or more findings on every frontend review. Severity rubric per [`SKILL.md`](SKILL.md). Most accessibility findings skew `Critical` or `Required` — the cost of an accessibility blocker shipping is asymmetric.

### Invariant 1: Reachability

Every interactive element must be reachable via the platform's assistive-input modalities. Modalities vary by platform; the principle does not.

**The contract:**

- Keyboard navigation reaches every actionable element (Tab/Shift+Tab/Arrow keys, depending on context).
- Switch-control / single-input navigation reaches every actionable element with a predictable scan order.
- Voice-control identifies every actionable element by an accessible name.
- Alternative pointers (head-tracking, eye-tracking, joystick-as-pointer) reach every target with reasonable hit-target size.
- No focus traps. The user can always exit the current focused region (Escape, programmatic dismissal, navigation away).

**Common violations:**

- Custom interactive elements (`<div onClick>`, custom `Button`-like views) that are not focusable.
- Modal dialogs that trap focus without an escape path.
- Skip-link or back-link missing on long-traversal screens.
- Auto-focus that fights the user's input intent.

**Finding tier:** `Critical` for any unreachable primary action; `Required` for unreachable secondary actions; `Required` for focus traps.

### Invariant 2: Semantic clarity

Every interactive and structural element conveys its accessible name + role to assistive technology. Decorative content is marked as decorative.

**The contract:**

- Each interactive element has an accessible name. Icon-only buttons need explicit labels (the icon is visual, not accessible).
- Each interactive element has an accessible role conveyed (button, link, switch, slider, menuitem, tab, etc.).
- Structural elements (headings, landmarks, lists) are conveyed via the platform's semantic primitive, not a styled `div`/`View` lookalike.
- Decorative images / icons / surfaces are marked decorative (`aria-hidden="true"` / `accessibilityHidden(true)` / equivalent) so assistive tech does not announce them as content.
- Reading/traversal order matches visual order. When it cannot (intentional design), the order is explicitly authored, not accidental.

**Common violations:**

- Icon-only buttons with no `aria-label` / `accessibilityLabel`.
- Headings styled with `<div class="heading-1">` instead of `<h1>`.
- Lists rendered as flat `<div>` siblings without `<ul>`/`<li>` structure or platform-list semantics.
- Decorative icons announced to screen readers.
- Custom interactives (drag-handle, swipe-action) with no announcement of their action.

**Finding tier:** `Critical` for missing names on primary actions; `Required` for missing roles or wrong-element semantics.

### Invariant 3: No-color-alone

State (selected, error, disabled, mastered, completed, warning, success) is never communicated by color alone. The platform's high-contrast / color-blind / monochrome modes must remain legible.

**The contract:**

- State pairs color with at least one other signal: shape, weight, symbol, label, position, or border.
- Error states pair red with an icon + text label.
- Selected states pair the accent color with a checkmark + label/border.
- Disabled states pair lower opacity with a non-color signal (struck-through, label, position).
- "Differentiate without color" platform settings remain functional.

**Common violations:**

- Form-field errors shown only by red border, no icon, no text.
- "Required" fields marked only by red asterisk color.
- Selected tab indicated only by background color difference.
- Status badges colored differently with no label difference.

**Finding tier:** `Required` always; `Critical` when the state being communicated is safety-relevant (error in irreversible action, warning before destructive operation).

### Invariant 4: Motion respect

Animations are gated behind the platform's reduce-motion preference. Auto-play, parallax, and decorative motion disable when the preference is set.

**The contract:**

- Decorative motion (entrance animations, parallax, transitions, idle-state animations) reads the reduce-motion preference and disables / substitutes still-frame when set.
- Essential motion (loading spinners that *communicate* state, progress indicators) may remain but should be the simplest expression possible.
- Auto-play (video, audio, animated content) is opt-in, not opt-out, regardless of motion preference.
- Vestibular-disturbance motion (long-distance translates, rapid scale changes, spinning content) gated even more conservatively.

**Common violations:**

- Hero-section parallax that ignores reduce-motion.
- Modal/sheet entrance animation always-on.
- Page-transition animations that ignore the preference.
- Background-video auto-play.

**Finding tier:** `Required` always; `Critical` for vestibular-triggering motion (rapid camera-like translates, rotation, scale-pulses).

### Invariant 5: Contrast minima

WCAG 2.1 AA equivalent or stricter. Verified against the *rendered context*, not the token value in isolation.

**The contract:**

- Body text: 4.5:1 contrast ratio against its rendered background.
- Large text (18pt+ regular, 14pt+ bold): 3:1.
- Non-text meaningful content (form-field borders, focus rings, status indicators, icon-only buttons): 3:1.
- Verified in both light + dark + high-contrast (where available) appearance modes.
- Verified against hover/focus/pressed/disabled state backgrounds, not only resting state.
- Verified against semitransparent overlays where used (a 50%-alpha black overlay on a white background is not the same context as the white background alone).

**Common violations:**

- Body text in `color.text.secondary` against `color.surface.subtle` failing 4.5:1.
- Icon-only buttons whose icon stroke fails 3:1 against the button surface.
- Focus rings whose color fails 3:1 against the surrounding background.
- Disabled-state text using opacity-50 falling below 3:1.

**Finding tier:** `Required` for AA failures; `Critical` for failures on safety-relevant surfaces (error messages, destructive-action confirmations).

### Invariant 6: Scaling

Content scales correctly when the user enlarges the system text size (Dynamic Type on Apple, browser zoom + font-size preferences on web, accessibility text size on Android).

**The contract:**

- All body text uses the platform's semantic text style (`Font.body`, `1rem`, `text-base`), not fixed pixel/point sizes.
- Layout reflows at the largest accessibility text size — no clipped content, no truncation that loses meaning, no overlapping elements.
- Interactive targets remain reachable at large scale; hit-target sizes scale with content where appropriate.
- Components verified at the largest scale, not only at default.

**Common violations:**

- `font-size: 16px` / `font(.system(size: 16))` instead of semantic style.
- `max-height` on a button that clips text at large scale.
- Two-column layouts that don't reflow to single-column at large scale.
- Tooltip / popover content truncated at large scale.

**Finding tier:** `Required` always.

### Invariant 7: Logical ordering

Tab / swipe / scan traversal order matches reading order. Custom focus management is explicit, not accidental.

**The contract:**

- Focus moves in reading order (top-to-bottom, left-to-right in LTR; mirrored in RTL) unless explicitly overridden.
- When a modal/sheet opens, focus moves to the modal; when it closes, focus returns to the trigger.
- Programmatic focus changes are authored deliberately — never silently moved by a render-cycle side effect.
- Scan order for switch-control / single-input matches the same reading order.
- Custom widgets (date pickers, comboboxes, tab strips) follow the platform's standard interaction pattern for that widget.

**Common violations:**

- Modal trap retains focus after close because the trigger is no longer mounted.
- Tab order broken by `tabindex` values applied unevenly.
- Custom widget's keyboard interaction inconsistent with platform expectations (e.g., a custom tab strip that doesn't respond to arrow keys).
- Skip-link that doesn't skip to where it claims.

**Finding tier:** `Required` always; `Critical` for traversal that's effectively broken (a modal where Escape doesn't dismiss; a focus-trap with no exit).

## Stack-appendix docking convention

The invariants above are stack-agnostic. The *verification surfaces* (how you mechanically check each invariant) are stack-specific. As stack-specific sibling skills are authored, each contributes a verification appendix that this card cross-references.

**Convention** (per [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md)):

- A new stack-skill (e.g., `frontend-swiftui`, `frontend-web`) authors its own `accessibility-verification.md` (or equivalent name) under its own skill directory.
- That stack-skill's reference card carries:
  - Per-invariant verification recipe for the stack (e.g., "Invariant 2 on SwiftUI: every interactive primitive should carry `accessibilityLabel` for icon-only cases; verify via VoiceOver rotor at … ; auto-trait audit via … ").
  - Platform-specific terminology mapping (e.g., "Apple platforms call this 'Dynamic Type'; Android calls it 'Font scale'; web calls it 'browser zoom + font-size preference'").
  - Tool/scanner pointers (Xcode's Accessibility Inspector, browser-DevTools Lighthouse, axe-core, etc.).
- This card cross-references the stack-specific appendix when invocation context names the relevant stack.

**Until stack-skills exist**, this card carries no stack-specific verification — the reviewer applies the invariants using the platform's accessibility tools as available. Honest gap, not silent gap: when the gap is felt, that's the signal a stack-skill is warranted.

**Anti-pattern:** Adding SwiftUI-specific or web-specific verification recipes into this card. That would make the invariant card stack-coupled, violating the modular partition this card depends on.

## How to use this card

1. On every frontend review, walk the seven invariants in order.
2. For each invariant, surface zero or more findings. Use the severity rubric.
3. If a stack-skill is also invoked, defer to its verification appendix for the *mechanical* checks; this card's invariants are the *contract* the appendix verifies against.
4. Empty findings rows are fine. Don't invent findings.

## See also

- [`SKILL.md`](SKILL.md) — `/frontend-discipline` recipe; concern 2 (Accessibility) expanded here.
- [`ai-smell-rejection.md`](ai-smell-rejection.md) — companion card; concern 1 (AI visual smell) expanded there.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared severity-rubric false-claim table; consulted on every review.
- [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md) — contract; stack-appendix docking convention defined here.
- WCAG 2.1 (AA): [`https://www.w3.org/WAI/WCAG21/quickref/`](https://www.w3.org/WAI/WCAG21/quickref/). Upstream source for the body-text + non-text contrast minima.
- Apple Human Interface Guidelines — Accessibility: [`https://developer.apple.com/design/human-interface-guidelines/accessibility`](https://developer.apple.com/design/human-interface-guidelines/accessibility). When SwiftUI stack-skill lands, the appendix references this.
- Android Accessibility: [`https://developer.android.com/guide/topics/ui/accessibility`](https://developer.android.com/guide/topics/ui/accessibility). When Android stack-skill lands (if ever; Paideia per ADR 0035 forecloses), the appendix references this.
- Pattern source: `addyosmani/agent-skills/skills/frontend-ui-engineering/references/accessibility-checklist.md` (adapted — invariant-only; stack-specifics moved to the docking-convention pattern).
