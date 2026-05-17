---
name: paideia-frontend-overlays
description: Run the Paideia-specific overlays on top of `/frontend-discipline` — triad-only primary surfaces (ADR 0034), rendering-policy compliance (ADR 0027), no engagement-loop dark patterns, quiet mastery rendering (ADR 0013), visual-identity working direction (gold-on-dark classical-scholarly per the working prototype), iconography discipline, pedagogical-graph rendering norms, and inherited project-discipline overlays (scope_lock awareness, ADR-citation requirement, engine_memory decisions-room drawer check). Composes with `/frontend-discipline`. Invoke deliberately on any Paideia frontend change.
disable-model-invocation: true
---

# paideia-frontend-overlays

> Project-tailoring skill for Paideia frontend work. The doctrine is this SKILL.md per [ADR 0073](../../../engine/adr/0073-paideia-frontend-overlays-skill.md) — no separate Layer 1 ops-doc.
>
> **Composition contract.** This skill is the **project-tailoring module** of the *core-invariant-plus-project-tailoring* architectural pattern. It composes with [`/frontend-discipline`](../frontend-discipline/SKILL.md) (the invariant core covering AI visual smell, accessibility, design tokens, state-flow, composition, adaptive layout, performance). Both should be invoked on Paideia frontend changes. They do not duplicate; the invariant pass surfaces universal findings, this pass surfaces project-specific findings. Stack-specific verification (SwiftUI, web) lives in future sibling skills that dock when each stack opens — neither this skill nor `/frontend-discipline` carries stack-coupled content.

## When to invoke

Always alongside [`/frontend-discipline`](../frontend-discipline/SKILL.md) on substantive Paideia frontend changes (per that skill's "When to invoke" rubric). The invariant pass surfaces universal findings; this pass surfaces Paideia-specific findings. Run both, neither substitutes for the other.

Specific cases where this skill is the *most* important:

- New primary surface proposed (anything claiming to be at the top of the navigation hierarchy)
- Any AI-instructor copy authored in frontend code (chat-context messages, onboarding text, syllabus-rendering prose, mastery-state communication)
- Engagement-loop mechanisms proposed (streak counters, leaderboards, "X-day streak broken" notifications, scoreboards)
- Visual-identity surfaces (logo placement, color usage, type pairings, iconography)
- Pedagogical-graph rendering (concept catalog, syllabus prerequisite topology, mastery overlay on graph)

## The Paideia overlays

Walk every Paideia frontend change against these overlays in order. Each surfaces zero or more findings. Severity rubric inherited from [`/frontend-discipline`](../frontend-discipline/SKILL.md) (Critical / Required / Nit / Optional / FYI).

### Overlay 1: Triad-only primary surfaces

Per [ADR 0034](../../../product/adr/0034-discovery-planning-engagement-triad.md), Paideia has exactly three primary surfaces: **Discovery** (browseable concept catalog + AI conversational onboarding), **Planning** (syllabus-as-plan with prerequisite ordering + concurrent-syllabus cap), **Engagement** (three bounded conversational contexts: concept engagement, diagnostic, bring-your-own-book close reading per [ADR 0028](../../../product/adr/0028-input-side-scope-structural-not-prompt.md)).

**Findings:**

- A new primary surface outside the triad (e.g., a "Library", "Trophy room", "Globe view", "Community", "Feed") — `Critical`. The fix is "remove or supersede ADR 0034", not "tweak the surface". Surface the supersession requirement before further authoring.
- Secondary/utility surfaces are allowed (settings, account, data export, exit affordances) — these are not "primary" and are operational continuity, not pedagogy surfaces.
- A surface that *appears* to be triad-aligned but in substance is something else (e.g., a "Daily Review" that's actually a streak-mechanic engagement-loop) — `Critical`; route to overlay 3.

### Overlay 2: Rendering-policy compliance

Per [ADR 0027](../../../product/adr/0027-rendering-policy-prompt-layer-contract.md), AI-instructor copy authored *anywhere in the frontend* (chat messages, modal prompts, onboarding scripts, syllabus narration, system surfaces speaking with the instructor's voice) must comply with the forbidden-token rules:

**Forbidden tokens in instructor voice:**

- Mastery-state labels ("you've mastered X", "X is now learned", "you've achieved proficiency in X")
- Prerequisite-framing prose ("X is a prerequisite for Y", "before tackling Y, master X")
- Scaffolding-distance mentions ("we're starting easy", "this is harder", "next is the advanced topic")
- Graph-version references ("according to the knowledge graph", "the prerequisite structure says")
- Sphere / world / map / trophy / globe metaphors ("explore the world of philosophy", "unlock this region", "your knowledge map")

**Findings:**

- Any forbidden token in instructor-voice copy — `Critical`. The rendering policy is contract; deviations require superseding 0027.
- Chrome / system-voice copy (e.g., "Next concept" button label, settings menu items) is NOT instructor-voice; the policy does not apply. Distinguish carefully.
- Learner-authored copy (user input, learner notes) is content, not instructor-voice; the policy does not apply.

The skill verifies via grep-able patterns on the touched files plus semantic reading of any rendered prose.

### Overlay 3: No engagement-loop dark patterns

Paideia is a pedagogical product, not an engagement product. The retention/conversion mechanics typical of consumer SaaS and ed-tech are explicitly refused (per [ADR 0033](../../../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md) mission realignment + [ADR 0032](../../../product/adr/0032-personal-project-disposition.md) corruption-vector identification).

**Explicitly forbidden patterns** (all `Critical` absent an explicit superseding pedagogical ADR):

- Streak counters / "X-day streak" surfaces / "streak broken" notifications
- Leaderboards / ranked-against-peers framing
- Trophy / badge / achievement collection surfaces
- Daily notification cadence calibrated to retention (vs. legitimate calendar/spacing-driven cues)
- "Reward animations" on mastery acknowledgment (mastery is rendered quietly per overlay 4)
- Loss-aversion framing ("don't lose your progress", "you'll forget X if you don't review", calibrated to anxiety)
- Variable-reward / surprise-reveal interaction patterns
- Social-pressure features (friends learning, peer activity feeds, public profiles)
- Streak freezes / streak-restoration purchases / any monetization of engagement-loss

**Findings:**

- Any of the patterns above without an explicit superseding pedagogical ADR — `Critical`.
- "We could add X to improve retention" framing in PRs, comments, or commit messages — `Required` finding even if the change itself is benign; the framing signals the corruption vector ADR 0032 warns against.
- Edge cases (a calendar-driven reminder for a learner-set spaced-repetition cadence is NOT a retention mechanic) — judgment-bound; document the distinction.

### Overlay 4: Quiet mastery rendering

Per [ADR 0013](../../../product/adr/0013-mastery-verification-organic-escalation.md), mastery happens through downstream callback references and zero-scaffolding probes, not through labeled celebration. The frontend must render mastery contextually within the syllabus, not as a separate event.

**Findings:**

- "Mastery achieved" toast / banner / modal — `Critical`. Mastery is shown by the concept's quiet appearance in the mastered-region of the syllabus, not announced.
- Trophy / badge / "you mastered X" celebration surface — `Critical`. Per overlay 3 + overlay 4 jointly.
- Color-coded "mastery level" visualization (red→yellow→green progress bars on concepts) — `Required` for over-celebration; consider muted typographic / positional rendering instead.
- Numerical mastery scores exposed to the learner (e.g., "Confidence: 0.87") — `Required`. Mastery state is a system concern; the learner sees position in the syllabus, not the underlying scoring.

The frontend is allowed and expected to show *what concepts the learner has covered* — that's syllabus state, not mastery celebration.

### Overlay 5: Visual-identity working direction

**Status: prototype-stage, not ADR-locked.** The user has shared a working visual-identity direction at session S-0135 (logo banner + app icon prototypes). Findings against this direction are recorded as **findings to discuss**, not Critical violations, until a product-side visual-identity ADR commits the palette and motifs formally. When that ADR lands, this overlay tightens — severities increase, the direction becomes contract.

**Working direction (S-0135):**

- **Aesthetic register:** classical-scholarly. References: Ionic column iconography, Greek-pedagogical heritage made literal, restrained ornamentation, thin-line geometric treatment.
- **Palette:** gold (warm tones with material-suggesting tonal variation, not decorative gradients) on near-black navy ground. No purple, no decorative rainbow gradients, no AI-default schemes.
- **Iconography motif:** Ionic column + abstract knowledge-graph lattice (the column as foundation, the graph growing upward from the capital). Used at logo, app icon, and identity-surface scale; not as a recurring decorative motif at component scale.
- **Typography register:** classical serif wordmark for display/identity moments with optional Greek-letter allusions (lambda-form `A`s, diamond flourish). Functional sans-serif for body text — not classical serif at body scale (legibility + scaling concerns).
- **Composition:** generous negative space, restrained ornamentation, no decorative chrome around content.

**Findings (against the working direction):**

- Surface using a non-working-direction palette (purple, default Tailwind/Material/iOS-system) — `FYI` until ADR-locked; routes to a discussion finding, not a block. When ADR lands, this becomes `Required`.
- Decorative gradients applied to UI chrome contrary to the restraint principle — `FYI` until ADR-locked.
- Mixed display fonts that fight the classical register — `FYI` until ADR-locked.
- Brand mark used at component-decoration scale (e.g., the Ionic column motif as repeating background pattern) — `Required` even pre-ADR; this is a clear deviation from "restrained at identity scale only".

**When the visual-identity ADR lands** (future product session): this overlay updates to reference the ADR; severities tighten; the working-direction prose is replaced with ADR-cited specs.

### Overlay 6: Iconography discipline

Distinct from overlay 5; concerns the icon system regardless of palette specifics.

- **Platform icon system as default.** SF Symbols for any Apple-target frontend surface (per ADR 0065 commitment 1 platform commitment). When a web surface opens for marketing or knowledge-graph viz — both permitted per ADR 0065 commitment 1's scope clarification (S-0154, [Issue #106](https://github.com/StarshipSuperjam/paideia/issues/106)): "no web app" scopes to the consumer product distribution channel only — the web equivalent (Lucide, Heroicons, project-authored) governs there. Stack-skills (future) carry the per-platform icon-set choice details.
- **Custom iconography for identity/marquee moments.** Logo, app icon, brand-mark applications. Custom is preferred over platform-default when the surface is identity-scale (not utility-scale).
- **No emoji-as-icon.** Under any condition, in UI chrome. (Learner-authored content is separate per overlay 2.)
- **No mixed-source icon collections.** A UI that pulls icons from three different sets (some SF Symbols, some Heroicons, some Material) reads chaotic. One set is the source for utility iconography; identity icons are custom.

**Finding tier:** `Required` for emoji-as-icon or mixed-source collections; `Optional` for "could be more on-brand" custom-vs-platform calls (judgment-bound).

### Overlay 7: Pedagogical-graph rendering norms

When a Paideia surface renders the prerequisite topology — syllabi visualization, concept catalog grouped by prerequisite chain, or any future graph-viz surface (knowledge-graph public visualizer, learner-facing topology view) — additional constraints:

- **Token discipline applies to graph styling.** Node fills, edge strokes, label colors all resolve through the theme tokens; no inline graph styling.
- **AA contrast applies to graph text.** Node labels, edge labels, hover-state text all verify against the surface they render on.
- **Direction-of-prerequisite legible by structure, not color alone.** Arrow shape, layout direction, or position carries the prerequisite-direction signal; color is a secondary signal at most.
- **State of graph nodes (mastered, current, locked, available) follows overlay 4.** Quiet rendering: muted typographic / positional treatment for state, not celebration colors or icons.
- **Performance posture per [`/frontend-discipline`](../frontend-discipline/SKILL.md) concern 7.** A graph of 380 nodes (current Phase 5 closeout count) and 532 edges renders without jank during pan/zoom/hover. Profile before claiming.
- **Accessibility per [`/frontend-discipline`](../frontend-discipline/SKILL.md) concern 2 invariants.** Graph navigable by keyboard / switch / voice / alternative pointer; nodes have accessible names; edge relationships announced where the structure is the content.

### Overlay 8: Scope_lock awareness (inherited)

Per [ADR 0051](../../../engine/adr/0051-routine-mode-and-engine-loop.md). In routine-mode, an out-of-scope review finding routes to a GitHub Issue per [`issue-discipline.md`](../../../engine/operations/issue-discipline.md), not an inline fix.

Mirrors [`/review`](../review/SKILL.md)'s Paideia overlay — when this skill is invoked from a routine-mode session, the same scope_lock surface applies.

### Overlay 9: ADR-citation requirement (inherited)

A change touching a contract surface (any ADR file, or modifying a component/migration that an existing ADR names by reference) must amend the ADR and update ENGINE_LOG.md. The PostToolUse hook on ADR writes per [ADR 0043](../../../engine/adr/0043-hook-architecture.md) reminds non-blockingly; this skill verifies.

**Frontend-specific contract surfaces:**

- ADR 0034 (triad) — touched by any change to primary-surface navigation
- ADR 0027 (rendering policy) — touched by any change to AI-instructor copy
- ADR 0028 (input-side scope) — touched by changes to the three bounded engagement contexts
- ADR 0013 (mastery rendering) — touched by changes to mastery display
- ADR 0065 commitment 1 (platform commitment) — touched by stack-target changes
- Future visual-identity ADR (when authored) — touched by palette/type/motif changes
- Future Phase 6 product-side ADRs (per ROADMAP)

**Findings:** Any of the above contract surfaces touched without ADR amendment + ENGINE_LOG update is `Required`.

### Overlay 10: engine_memory decisions-room drawer check (inherited)

If a new ADR is authored in this session: confirm a matching `decision`-tagged drawer in engine_memory via `engine_memory_search`. The post-adr-write hook reminds; this skill verifies.

## Process sequence

1. **Load context.** Read the touched product ADRs (0034, 0027, 0028, 0013, 0065, visual-identity ADR if it exists), the session's plan file, any active scope_lock if in routine-mode.
2. **Walk the ten overlays** in the order above. Each surfaces zero or more findings.
3. **Categorize every finding by severity tier.**
4. **Verify cross-reference with [`/frontend-discipline`](../frontend-discipline/SKILL.md) findings.** A finding flagged here as project-specific should NOT be duplicated by the invariant pass; if a finding appears on both sides, judge whether it's genuinely project-specific (keep here) or universal (move to invariant). The partition is load-bearing.
5. **Emit the structured Markdown report** (next section). Self-check against [`../review/anti-rationalization.md`](../review/anti-rationalization.md) and [`../frontend-discipline/ai-smell-rejection.md`](../frontend-discipline/ai-smell-rejection.md).

## Output shape

A structured Markdown report. Sample:

```markdown
## `paideia-frontend-overlays` — <branch-name> @ <SHA-short>

**Composed with:** `/frontend-discipline` report at <link or "ran in parallel">.

### Findings (Paideia overlays)

| Severity | Overlay | Finding | File:Line | Suggested action |
|---|---|---|---|---|
| Critical | 1 (Triad) | New primary surface "Library" outside ADR 0034 triad | path/to/Nav.swift:42 | Remove OR author ADR superseding 0034 |
| Critical | 2 (Rendering policy) | Forbidden token "you've mastered" in instructor-voice copy | path/to/SyllabusView.swift:117 | Replace with quiet rendering per ADR 0013 |
| Required | 3 (Dark patterns) | Streak counter surface proposed | path/to/EngagementView.swift:88 | Remove; engagement-loop dark patterns forbidden per ADR 0033 |
| FYI | 5 (Visual identity) | Surface uses Tailwind violet-700 as accent | path/to/Theme.ts:25 | Discuss against working brand direction; will tighten when visual-identity ADR lands |
| Required | 9 (ADR-citation) | ADR 0034 not amended after primary-surface change | path/to/Nav.swift | Amend 0034 + update ENGINE_LOG.md |

### Inherited-overlay grid

- **Scope_lock:** PASS (or: `<finding>` — Issue filed/needed)
- **ADR-citation:** PASS (or: `<finding>` — ADR NNNN needs amendment)
- **engine_memory decisions-room drawer:** PASS (or: `<finding>` — drawer missing for ADR NNNN)

### Anti-rationalization self-check

- Reviewed against [`../review/anti-rationalization.md`](../review/anti-rationalization.md) + [`../frontend-discipline/ai-smell-rejection.md`](../frontend-discipline/ai-smell-rejection.md): no rationalizations applied.
```

## Failure modes this skill prevents

- **Primary surface creep.** A new "Library" / "Trophy" / "Globe" / "Community" / "Feed" surface ships without superseding ADR 0034 because it "feels useful". Overlay 1 makes the contract explicit.
- **Instructor-voice drift.** Mastery-state labels, prerequisite-framing prose, scaffolding-distance mentions appearing in copy because they read "encouraging" without the policy in view. Overlay 2 catches.
- **Engagement-loop infiltration.** A "streak" or "leaderboard" proposed because "every learning app has one", drifting Paideia toward the corruption vector ADR 0032 forecloses. Overlay 3 catches at the proposal point.
- **Mastery celebration.** A toast/banner/modal "celebrating" learner achievement, fighting overlay 4's quiet-rendering contract.
- **AI visual smell aliased as brand.** A purple-gradient hero claimed as "brand identity" without an actual brand-identity ADR. Overlay 5 captures the working direction as the basis for discussion findings; the universal pass at `/frontend-discipline` ai-smell-rejection.md handles the default-vs-intentional rubric.
- **Premature lock-in of provisional direction.** Overlay 5 is explicitly prototype-stage; severities are deliberately soft. This prevents authoring a "visual identity is settled" contract before the user has settled it.

## Failure modes this skill does NOT prevent

- **Universal frontend smell** — covered by [`/frontend-discipline`](../frontend-discipline/SKILL.md). The invariant pass and the project pass are complementary.
- **Stack-specific verification** — covered by future stack-skills (`frontend-swiftui`, `frontend-web`) when authored. This skill stays stack-agnostic.
- **Wrong product surface entirely** — if the surface itself shouldn't exist (e.g., a feature outside Paideia's mission per ADR 0033), that's a product decision upstream of any frontend skill.
- **Backend / API / data-layer concerns** — those use [`/review`](../review/SKILL.md) + [`/security-review`](../security-review/SKILL.md) primarily.

## See also

- [`/frontend-discipline`](../frontend-discipline/SKILL.md) — invariant core; always invoked alongside this skill.
- [`/review`](../review/SKILL.md) — five-axis code review; covers the code-quality side of any frontend change.
- [`/security-review`](../security-review/SKILL.md) — depth security review; compose for auth/form/content-rendering surfaces.
- [`../review/anti-rationalization.md`](../review/anti-rationalization.md) — shared severity-rubric false-claim table.
- [`../frontend-discipline/ai-smell-rejection.md`](../frontend-discipline/ai-smell-rejection.md) — frontend-specific AI-visual-smell catalog + UI rationalization table.
- [`../frontend-discipline/accessibility-invariants.md`](../frontend-discipline/accessibility-invariants.md) — invariant accessibility requirements.
- [ADR 0073](../../../engine/adr/0073-paideia-frontend-overlays-skill.md) — the citable contract this skill operationalizes.
- [ADR 0072](../../../engine/adr/0072-frontend-discipline-skill.md) — sibling contract (invariant core).
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition.
- [ADR 0034 (product)](../../../product/adr/0034-discovery-planning-engagement-triad.md) — triad shape (overlay 1).
- [ADR 0027 (product)](../../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — rendering policy (overlay 2).
- [ADR 0033 (product)](../../../product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md) — mission realignment that forecloses engagement-loop dark patterns (overlay 3).
- [ADR 0013 (product)](../../../product/adr/0013-mastery-verification-organic-escalation.md) — quiet mastery rendering (overlay 4).
- [ADR 0065 (product)](../../../product/adr/0065-oss-pivot-and-byok-disposition.md) — platform commitment (Apple SwiftUI; commitment 1 preserves ADR 0035's platform language verbatim and scopes "no web app" to the consumer product distribution channel per the S-0154 Issue #106 clarification).
- [ADR 0028 (product)](../../../product/adr/0028-input-side-scope-structural-not-prompt.md) — three bounded engagement contexts.
- Future visual-identity product ADR — overlay 5 cross-references when authored.
