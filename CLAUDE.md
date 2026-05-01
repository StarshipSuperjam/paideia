# CLAUDE.md

> AI orientation. Auto-loaded by Claude Code at session start. Lightweight by design — names the rules and points at the procedures, not a manual.

## Startup ceremony

Every session begins by reading these in order:

1. **`STATE.md`** — current phase, last-closed session, next-session work item, infrastructure pointers.
2. **`session/register_state.json`** — counter state. If `last_claimed`'s 4-digit suffix mod 30 == 0, the health-check cadence trigger fires (see `docs/operations/health-check.md`).
3. **MemPalace** — query `mempalace_search` with terms derived from the next-session work item. Surface anything relevant the user previously named.
4. **Files referenced by STATE.md and ROADMAP.md** for the current work.

`/start-engine` automates this and claims the next slot. See `.claude/commands/start-engine.md`.

## First-session reading order

A fresh session reading only this file learns the rules but not the procedures. The smallest set of operations docs to read on cold start, in order:

1. [`docs/operations/session-build-lifecycle.md`](docs/operations/session-build-lifecycle.md) — boot procedure, eager-claim ritual, in-session commit cadence, push policy, recovery paths.
2. [`docs/operations/session-shutdown-sequence.md`](docs/operations/session-shutdown-sequence.md) — close-of-session protocol; partial-closure handling; recovery from interrupted shutdown.
3. [`docs/operations/escalation-criteria.md`](docs/operations/escalation-criteria.md) — when to interrupt the user; worked examples both ways.
4. [`docs/operations/tools-validate-interpretation.md`](docs/operations/tools-validate-interpretation.md) — hard-fail vs soft-warn handling.

Other operations docs are defer-on-demand: read when the session's work item references them or when one of the four core docs points at them. The full index lives at [`docs/operations/README.md`](docs/operations/README.md).

## Two session modes

- **Default — exploration.** No project file edits to tracked files. No commits. No slot claim. Sketch in conversation. MemPalace captures with the `exploration` tag (via the stop/precompact hooks in `.claude/settings.json`). When discussion converges on something worth committing, offer `/start-engine`.
- **Build — `/start-engine`.** Eager-claims the next slot, allows commits and project file edits, runs the shutdown sequence at close. Procedure: `docs/operations/session-build-lifecycle.md` + `docs/operations/session-shutdown-sequence.md`.

## Standing rules

### Pushback rule

The AI is pre-authorized to surface unnamed risks, hidden pitfalls, and unstated opportunities at the moment of noticing. Push back specifically — name the concern concretely. Apply equally to user proposals AND AI proposals (self-critique). The bar is "I see a specific thing you may not be seeing," not "I should challenge this on principle." Calibrate by mode: looser when the user is venting/exploring, tighter when proposing a commitment.

### Auto-mode interrupt criteria

While running in auto/build mode, do NOT pause and escalate to the user EXCEPT for:

- **Irreversible-with-unclear-path** — a decision propagates as irreversible structure across multiple downstream sessions AND the right direction is genuinely unclear.
- **Unsolvable** — multiple approaches tried, no viable path.
- **Destructive-action confirmation** — any `rm -rf`, `git reset --hard`, force-push, deleting tracked files in bulk. Confirm before executing.

Routine judgment calls during a session are session-internal and recorded in `session/current.json`'s `outcome_summary`, not escalated.

### Budget guidance

- Substantive extraction work: target 60% context, hard cap 70%.
- Mechanical/procedural work: target 70%, hard cap 80%.

If a session hits its cap mid-work, halt at the next sensible boundary, write `outcome_summary` with partial-completion notes, archive `current.json` with `status: closed_partial`, push, and the next session picks up.

### End-state-quality first-pass

Author at production quality the first time. Don't write a draft and polish; don't write a placeholder and revisit. The cost of re-reading and re-revising a sloppy first pass exceeds the cost of slowing down to write it correctly. Particularly true for documents that downstream sessions will read cold — readability *is* the artifact's value.

Applies to newly-authored content. Cleanup sweeps that retrofit existing content to a newly-imposed contract — applying [ADR 0036](adr/0036-expression-contract-for-inward-documents.md) to documents authored before the contract existed, for example — are exempt and belong in the new contract's own Consequences section.

### Two-layer decision recording

Every settled decision lands in two places, serving different consumers:

- **ADR** (`adr/NNNN-title.md`, from S-0003 onward) — durable, structured, citable. The contract.
- **MemPalace** (`decision` tag) — semantic memory, conversational form, recall-by-similarity. The story.

ADRs answer "what's settled?". MemPalace answers "have we considered X before?". Neither replaces the other.

### Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/). Types in active use: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`, `perf`. Eager-claim commits use `chore(session):`. Always attribute via the `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` footer.

`tools/validate.py` runs in the pre-commit hook. Hard-fails block the commit. Soft-warns are recorded in `session/current.json`'s `outcome_summary`. See `docs/operations/tools-validate-interpretation.md`.

### Posture vs machinery

Several rules above are postures held by AI discipline, not machinery enforced by validators or hooks:

- The **pushback rule** — no log, no audit; a session that fails to surface a real risk leaves no trace.
- **Two-layer decision recording** — `tools/validate.py` does not check whether a settled decision was filed to MemPalace alongside its ADR.
- The **startup ceremony order** — the four steps run by judgment; nothing prevents skipping or reordering.

The choice is deliberate: these don't admit clean mechanical detection. The cost is that drift accumulates silently if discipline lapses. The mitigation is awareness — a session that knows the rule is unenforced can hold itself accountable rather than mistake the absence of an alarm for the presence of compliance.

## Topical pointers

Procedural depth lives in `docs/operations/` — one file per topic. Browse with `ls docs/operations/`. Index at `docs/operations/README.md`. High-frequency entries:

- `session-build-lifecycle.md` — boot, eager-claim, in-session work, push cadence.
- `session-shutdown-sequence.md` — audit, spot-check, STATE.md, CHANGELOG, archive.
- `mempalace-operations.md` — install, init, mine, hook wiring, query patterns.
- `mempalace-tagging-conventions.md` — `exploration` / `decision` / `work` tags.
- `tools-validate-interpretation.md` — hard-fail vs soft-warn, what to do with each.
- `escalation-criteria.md` — when to interrupt user; redundant with auto-mode criteria above but with worked examples.
- `adr-authoring.md` — Nygard template, status conventions, when an ADR is warranted.
- `health-check.md` — audit categories, report template, cadence policy.

Project context (the *what* and *why*, not the *how*):

- `docs/MISSION.md` — vision, audience framing, cross-domain commitment.
- `docs/CROSS_REFERENCES.md` — high-value file dependencies.
- `STATE.md` — current state. `ROADMAP.md` — full arc.
