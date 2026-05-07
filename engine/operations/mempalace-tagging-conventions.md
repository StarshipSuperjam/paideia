# MemPalace tagging conventions

> Five tags carry semantic load in this project. Apply consistently so cross-session retrieval is reliable. Mechanics for capturing into MemPalace live in [`mempalace-operations.md`](mempalace-operations.md).

## The five tags

### `exploration`

Default-mode (non-build) conversations capture under `exploration`. The tag means: "we discussed this; it may or may not be settled; the value is in the reasoning, not the conclusion."

Apply when:
- The conversation considered an approach and rejected it (so future sessions don't re-litigate).
- The conversation noted a constraint, edge case, or downstream implication that wasn't material enough for a tension entry.
- The user surfaced a working hypothesis that hasn't crystallized into a commitment.

Don't apply `exploration` to closed decisions — those are `decision`.

### `decision`

Settled choices. The tag means: "this is what we're doing, and reversing it requires substantial new evidence."

Apply when:
- An ADR is being authored — the conversation that produced the ADR's reasoning gets `decision`-tagged so the verbatim story is recoverable next to the ADR's structured contract.
- A working commitment is added to (or removed from) `STATE.md` / `ROADMAP.md` / a design doc's commitment list.
- A tension in `docs/tensions.md` resolves and moves to a downstream file.

Pair with `wing: paideia`, `room: decisions` (per the room-targeting conventions below).

### `pushback`

Added at S-0032 per the audit's Improvement G recommendation. Verbatim moments where the AI surfaced a real unnamed risk and the user accepted the pushback, producing a course correction. The tag means: "I almost made this mistake; this is the conversation that prevented it."

CLAUDE.md's "Posture vs machinery" section explicitly notes the pushback rule has no log and no audit; a session that fails to surface a real risk leaves no trace. The `pushback` tag is the partial mechanization of the missing trace — when pushback works, capture the moment so future sessions can retrieve it via semantic search before re-attempting the same mistake.

**Capture surface (added at S-0041).** The convention's primary capture surface is the explicit yes/no ask in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) step 7 (after the diary write). The S-0041 second project health check measured zero `pushback`-tagged drawers across S-0033 → S-0040 — eight sessions of opportunity, judgment-alone produced zero captures. The convention was too implicit to reach the AI's authoring loop. The shutdown-step explicit ask makes the capture decision a structural surface, not a judgment call. In-session capture is also welcome whenever the moment is visible — the shutdown-step ask is the backstop, not the only opportunity.

Apply when:
- The AI surfaced an unnamed risk specifically (not generic concern), the user heard it, and the conversation changed direction in response.
- Self-pushback also qualifies — AI critiquing its own proposal, user accepting the critique.

What goes in:
- Verbatim user framing (the proposal that prompted the pushback).
- Verbatim AI pushback (the specific concern named).
- Verbatim user acceptance (the language that signaled "yes, change course").
- One-line summary of the resulting change.

Without verbatim, the recall value collapses — the point is to recover the actual moment, not a summary.

Pair with `wing: paideia`, `room: decisions` if the pushback crystallized into an ADR-shaped change (also tag `decision`); otherwise `room: general` until the room-targeting conventions evolve. Manual capture via `mempalace_add_drawer` — auto-capture cannot tell pushback from any other exchange.

### `work`

Build-session activity logs. The tag means: "this session did this work; here's what got produced and why."

Apply when:
- A build session produces an ENGINE_LOG-tracked material change.
- A session encounters a non-obvious obstacle and resolves it (the obstacle and its resolution are the value, not the final committed state).
- A session decides to defer something to a future session — the deferral plus reason gets a `work` drawer so the picking-up session can recover the context.

The hooks tag autocaptures from build sessions with `work` by default unless the conversation has been actively talking about an exploration or decision moment, in which case the more specific tag applies.

### `lesson`

Added at S-0032. Procedural failures and their fixes — "we tried X, it failed because non-obvious Y, the fix that worked was Z." The tag means: "future session considering X, look here first."

Currently the project captures procedural failures inconsistently: some show up in `outcome_summary`, some drive ops-doc updates, many vanish. The `lesson` tag standardizes the capture channel so semantic search recovers prior failure context before a session re-attempts the same approach.

**Capture surface (added at S-0041).** The convention's primary capture surface is the explicit yes/no ask in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) step 7 (after the diary write, paired with the `pushback` ask). The S-0041 second project health check measured zero `lesson`-tagged drawers across S-0033 → S-0040 — eight sessions of opportunity, judgment-alone produced zero captures. The convention was too implicit to reach the AI's authoring loop. The shutdown-step explicit ask makes the capture decision a structural surface, not a judgment call. In-session capture is also welcome whenever the moment is visible — the shutdown-step ask is the backstop, not the only opportunity.

Apply when:
- A session tried an approach, it failed for a reason that was not obvious before the failure, and a working fix was found.
- The reason for failure is the value (not the fix). If the fix is obvious once the failure is identified, the lesson is the identification — record the failure mode itself.

What goes in:
- The failed approach (specific enough that a future search on similar approaches surfaces this).
- The non-obvious reason it failed.
- The working fix.
- Optional: pointers to related ADRs or ops docs that the lesson should eventually flow into if it generalizes.

Pair with `wing: paideia`, `room: lessons` (per the room-targeting conventions below — `lessons` room established at S-0032). Manual capture via `mempalace_add_drawer` at the moment of recovery; not auto-captured.

## Room-targeting conventions

Added at S-0032 per the audit's Improvement B recommendation. Where a new drawer goes by room, given its tag(s):

- `decision`-tagged drawers (ADR companions or other settled-choice records) → `decisions` room.
- `pushback`-tagged drawers that crystallized into a settled change → `decisions` room (also tag `decision`). Pushback that resulted in a course correction without an ADR → `general` room (until a `pushback` room is established if/when volume warrants).
- `lesson`-tagged drawers → `lessons` room.
- Session-meta exchanges that aren't ADR-attached (e.g., S-0001's verbatim foundation-planning exchanges, S-0003's ADR-collection narrative) → `s<NNNN>-<topic>` room (existing convention).
- Auto-captured `work` and `exploration` drawers from Stop/PreCompact hooks → `general` room (default fallback).
- Operations docs themselves → don't reindex them as drawers; they live in git, queryable via grep + Read.

When the right room isn't obvious, default to `general` rather than inventing a new room. New rooms are added by deliberate convention (additions to this section), not by ad-hoc drawer filing.

**Tagging carries the meaning; room targeting is best-effort** (clarification per [Issue #43](https://github.com/StarshipSuperjam/paideia/issues/43) / S-0086 audit R8). The S-0086 review observed that pushback drawers occasionally land in `decisions` even when no ADR resulted — for example `drawer_paideia_decisions_a3d64680e953450f011e582f`, which is `pushback`-tagged and substantively about a settled-during-conversation course correction without a downstream ADR. The recommended disposition is to **trust the tag, not the room**: semantic search returns drawers by content + tag, so a pushback drawer in `decisions` is functionally retrievable as a pushback. Don't move drawers between rooms post-hoc; the tagging convention is what governs retrieval.

## How tags interact with the hooks

The Stop hook fires every 15 human messages and the PreCompact hook fires before context compaction. Both invoke `mempalace hook run` which decides what to capture and how to tag based on conversation content. Tags are not a manual gate — they're applied to the captured drawers based on detected content patterns.

When manually capturing via `mempalace_add_drawer`, set the tag explicitly. Drawers can carry multiple tags; prefer the most-specific applicable tag plus any cross-cutting ones.

## Cross-cutting tags

Beyond the three core tags, free-form tags are encouraged for retrievability:

- `phase-0`, `phase-1`, etc. — anchor a memory to its build phase.
- `architecture`, `pedagogy`, `infrastructure`, etc. — domain hooks.
- `watch` — for items that aren't actionable yet but shouldn't be forgotten (mirrors `docs/tensions.md`'s `watch` tag).
- `oq-DEC1-A` etc. — for memories tied to a specific open question.

## Anti-patterns

- Don't use `decision` for working hypotheses that haven't been committed-to. That's `exploration`.
- Don't use `work` for the conclusion of a build session — `ENGINE_LOG` already records that. Use `work` for the *journey* (obstacles, deferrals, surprises).
- Don't apply all three tags to one drawer. If a drawer's content spans multiple categories, split it.

## See also

- [`mempalace-operations.md`](mempalace-operations.md) — install, init, hook config.
- [`adr-authoring.md`](adr-authoring.md) — how `decision` drawers complement ADRs.
