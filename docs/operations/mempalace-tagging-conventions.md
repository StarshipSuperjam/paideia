# MemPalace tagging conventions

> Three tags carry semantic load in this project. Apply consistently so cross-session retrieval is reliable. Mechanics for capturing into MemPalace live in [`mempalace-operations.md`](mempalace-operations.md).

## The three tags

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

Pair with `wing: paideia`, `room: <topic>` (e.g., `room: self-correction`, `room: operations`).

### `work`

Build-session activity logs. The tag means: "this session did this work; here's what got produced and why."

Apply when:
- A build session produces an ENGINE_LOG-tracked material change.
- A session encounters a non-obvious obstacle and resolves it (the obstacle and its resolution are the value, not the final committed state).
- A session decides to defer something to a future session — the deferral plus reason gets a `work` drawer so the picking-up session can recover the context.

The hooks tag autocaptures from build sessions with `work` by default unless the conversation has been actively talking about an exploration or decision moment, in which case the more specific tag applies.

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
