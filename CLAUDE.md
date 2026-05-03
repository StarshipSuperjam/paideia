# CLAUDE.md

> AI orientation. Auto-loaded by Claude Code at session start. Lightweight by design — names the rules and points at the procedures, not a manual.
>
> Stays at root per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md) edge-case (c) — Claude Code expects it there. Content is engine-side; the wall the ADR commits to is conceptual, not a physical-purity test.

## Startup ceremony

Every session begins by reading these in order:

1. **`engine/STATE.md`** — current phase, last-closed session, next-session work item, infrastructure pointers.
2. **`engine/session/register_state.json`** — counter state. If `next_id`'s 4-digit suffix mod 30 == 0, the health-check cadence trigger fires (see `engine/operations/health-check.md`). The `SessionStart` hook (`engine/tools/hooks/session-start.sh` per [ADR 0043](engine/adr/0043-hook-architecture.md)) emits the cadence surface from the harness side regardless of how the session is launched, so steps 1–2 are also mechanically backstopped.
3. **MemPalace** — query `mempalace_search` with terms derived from the next-session work item. Surface anything relevant the user previously named.
4. **Files referenced by `engine/STATE.md` and `ROADMAP.md`** for the current work.

`/start-engine` automates this and claims the next slot. The slash command's documented procedure routes through the `session-build-lifecycle` Skill (per [ADR 0044](engine/adr/0044-skill-conversion-recipe-vs-reference.md)). See `.claude/commands/start-engine.md` and `.claude/skills/session-build-lifecycle/SKILL.md`.

## First-session reading order

A fresh session reading only this file learns the rules but not the procedures. The smallest set of operations docs to read on cold start, in order:

1. [`engine/operations/session-build-lifecycle.md`](engine/operations/session-build-lifecycle.md) — boot procedure, eager-claim ritual, in-session commit cadence, push policy, recovery paths.
2. [`engine/operations/session-shutdown-sequence.md`](engine/operations/session-shutdown-sequence.md) — close-of-session protocol; partial-closure handling; recovery from interrupted shutdown.
3. [`engine/operations/escalation-criteria.md`](engine/operations/escalation-criteria.md) — when to interrupt the user; worked examples both ways.
4. [`engine/operations/tools-validate-interpretation.md`](engine/operations/tools-validate-interpretation.md) — hard-fail vs soft-warn handling.

Other operations docs are defer-on-demand: read when the session's work item references them or when one of the four core docs points at them. The full index lives at [`engine/operations/README.md`](engine/operations/README.md).

## Two session modes

- **Default — exploration.** No project file edits to tracked files. No commits. No slot claim. Sketch in conversation. MemPalace captures with the `exploration` tag (via the stop/precompact hooks in `.claude/settings.json`). When discussion converges on something worth committing, offer `/start-engine`.
- **Build — `/start-engine`.** Eager-claims the next slot, allows commits and project file edits, runs the shutdown sequence at close. Canonical invocation routes through three user-defined Skills under `.claude/skills/` (per [ADR 0044](engine/adr/0044-skill-conversion-recipe-vs-reference.md)):
  - `session-build-lifecycle` — boot procedure invoked at session start (Layer 1 doc: `engine/operations/session-build-lifecycle.md`).
  - `session-shutdown-sequence` — close procedure invoked at session end (Layer 1 doc: `engine/operations/session-shutdown-sequence.md`).
  - `build-readiness-gate` — gate procedure invoked before substantive build sessions (Layer 1 doc: `engine/operations/build-readiness-gate.md`).

  All three Skills carry `disable-model-invocation: true` — the AI invokes deliberately rather than auto-firing on description match. The Layer 1 ops docs remain the source-of-truth; updates flow doc → skill, never the reverse.

## Standing rules

### Pushback rule

The AI is pre-authorized to surface unnamed risks, hidden pitfalls, and unstated opportunities at the moment of noticing. Push back specifically — name the concern concretely. Apply equally to user proposals AND AI proposals (self-critique). The bar is "I see a specific thing you may not be seeing," not "I should challenge this on principle." Calibrate by mode: looser when the user is venting/exploring, tighter when proposing a commitment.

### Auto-mode interrupt criteria

While running in auto/build mode, do NOT pause and escalate to the user EXCEPT for:

- **Irreversible-with-unclear-path** — a decision propagates as irreversible structure across multiple downstream sessions AND the right direction is genuinely unclear.
- **Unsolvable** — multiple approaches tried, no viable path.
- **Destructive-action confirmation** — any `rm -rf`, `git reset --hard`, force-push, deleting tracked files in bulk. Confirm before executing.

Routine judgment calls during a session are session-internal and recorded in `engine/session/current.json`'s `outcome_summary`, not escalated.

### Budget guidance

- Substantive extraction work: target 60% context, hard cap 70%.
- Mechanical/procedural work: target 70%, hard cap 80%.

The percentages refer to the active context window (1M tokens for Claude Opus 4.7, the model the project currently runs under). Absolute thresholds: ~600K (substantive target), ~700K (substantive cap), ~700K (mechanical target), ~800K (mechanical cap). These are higher than pre-1M intuitions; a session at 30% load (~300K tokens) is comfortably within budget, not near the cap.

**Do not propose splitting, deferring, or re-scoping a session based on "this feels big" alone.** Read the actual percentage. The default is single-session full execution; splits require a concrete blocker (the percentage itself, an external constraint surfaced mid-work, a structural reason such as foundations-vs-mechanization that's named in the plan up front).

Worked examples:

- 20% load while planning a multi-file refactor: not a budget concern. Continue.
- 35% load mid-extraction with three large operations docs still to read: not yet a concern; estimate the additional load (each doc adds ~5-10% typically) and continue.
- 65% load mid-extraction with substantive new code yet to author: this is the moment to consider whether to halt at the next sensible boundary. Concrete cap, not "feels big."
- 75% load on mechanical procedural work (drift sweep, link audit): approaching the mechanical cap; either finish the immediate task and close, or queue the remainder as next-session work with a specific pointer.

If a session hits its cap mid-work, halt at the next sensible boundary, write `outcome_summary` with partial-completion notes, archive `engine/session/current.json` with `status: closed_partial`, push, and the next session picks up.

### End-state-quality first-pass

Author at production quality the first time. Don't write a draft and polish; don't write a placeholder and revisit. The cost of re-reading and re-revising a sloppy first pass exceeds the cost of slowing down to write it correctly. Particularly true for documents that downstream sessions will read cold — readability *is* the artifact's value.

Applies to newly-authored content. Cleanup sweeps that retrofit existing content to a newly-imposed contract — applying [ADR 0036](engine/adr/0036-expression-contract-for-inward-documents.md) to documents authored before the contract existed, for example — are exempt and belong in the new contract's own Consequences section.

### Default to fix-in-context

A bug found mid-session whose fix you understand defaults to **inline fix in this session**, not a HANDOFF.md entry. The deferral overhead — writing prose that names the bug, names the fix, names the proposed verification, plus the future session re-deriving the same details from cold — exceeds the inline-fix cost in nearly every case. Even when the bug is preexisting (not introduced by this session) and even when it's tangential to the session's named scope, the calculus holds: if you have the fix in context, apply it.

Three named exceptions admit deferral:

- **Substantial scope.** The fix touches load-bearing contracts (multiple ADRs, a posture rule, a cross-cutting refactor). Estimate honestly — most "feels substantial" reads are wrong.
- **Contract change required.** The fix mutates a public surface another file or session depends on; that mutation needs its own ADR-tracked deliberation.
- **Budget cap reached.** Per the budget-guidance percentages above, the session genuinely cannot fit the additional work without spilling.

If one of those three applies, **flag the user before adding a HANDOFF.md entry**: name the bug, name the fix, name which exception applies, ask whether to fix in context now or defer. Do not write the HANDOFF entry first.

Mechanically backstopped by [`engine/tools/audit_handoff_dispositions.py`](engine/tools/audit_handoff_dispositions.py): every new section added to HANDOFF.md during a session must carry a `**Disposition:**` line in one of the accepted forms (`fixed-in-session @ <SHA>`, `deferred-with-user-confirmation`, `out-of-scope`, `not-actionable`). The audit hard-fails at session shutdown if any new section is missing or has an unrecognized disposition. The intent is to make the deferral choice explicit at authoring time; the audit catches lapses.

### Two-layer decision recording

Every settled decision lands in two places, serving different consumers:

- **ADR** — durable, structured, citable. The contract. Engine ADRs (about how the AI build apparatus works) live in `engine/adr/`; product ADRs (pedagogy, learner model, curriculum, schema, business) live in `product/adr/`. Partitioned at S-0024 per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md).
- **MemPalace** (`decision` tag) — semantic memory, conversational form, recall-by-similarity. The story.

ADRs answer "what's settled?". MemPalace answers "have we considered X before?". Neither replaces the other.

### Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/). Types in active use: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`, `perf`. Eager-claim commits use `chore(session):`. Always attribute via the `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` footer.

`engine/tools/validate.py` runs in the pre-commit hook. Hard-fails block the commit. Soft-warns are recorded in `engine/session/current.json`'s `outcome_summary`. See `engine/operations/tools-validate-interpretation.md`.

### Posture vs machinery

Some rules above remain postures held by AI discipline:

- The **pushback rule** — no log, no audit; a session that fails to surface a real risk leaves no trace.
- The **startup ceremony order** — steps 1, 3, and 4 run by judgment; nothing prevents skipping or reordering. Step 2 (the cadence trigger) is now mechanized via the `SessionStart` hook per [ADR 0043](engine/adr/0043-hook-architecture.md), but the order in which the AI consumes the surface remains posture.
- **Skill invocation** — the three build-mode Skills (`session-build-lifecycle`, `session-shutdown-sequence`, `build-readiness-gate`) carry `disable-model-invocation: true`. The AI is responsible for invoking each at the appropriate moment; the harness will not auto-fire them.

These postures don't admit clean mechanical detection. The cost is that drift accumulates silently if discipline lapses. The mitigation is awareness — a session that knows the rule is unenforced can hold itself accountable rather than mistake the absence of an alarm for the presence of compliance.

Other rules previously held by posture are now mechanized:

- **Two-layer decision recording** is soft-enforced by the `PostToolUse` hook on ADR writes (`engine/tools/hooks/post-adr-write.sh` per [ADR 0043](engine/adr/0043-hook-architecture.md)) — the hook reminds when an ADR write produces no matching `decision`-tagged MemPalace drawer. The reminder is non-blocking; the AI may proceed if the apparent absence is intentional.
- **STATE.md required-fields verification** is soft-enforced by the `PostToolUse` hook on STATE.md edits (`engine/tools/hooks/post-state-edit.sh` per [ADR 0043](engine/adr/0043-hook-architecture.md)) — the hook surfaces reminders for empty rows or placeholder tokens.
- **Health-check cadence trigger** is mechanized by the `SessionStart` hook (`engine/tools/hooks/session-start.sh` per [ADR 0043](engine/adr/0043-hook-architecture.md)) — fires regardless of whether `/start-engine` is invoked.
- **Subprocess environment scrubbing** is mechanized via [`engine/tools/scrub_env.py`](engine/tools/scrub_env.py) and [`engine/tools/scrub_env.sh`](engine/tools/scrub_env.sh) per [ADR 0045](engine/adr/0045-shared-state-integrity-discipline.md). All four hook scripts source the bash helper and call `scrub_git_env` before any git-aware subprocess; `validate.py`'s four code-gate subprocess calls (ruff, ruff format, mypy, pytest) pass `env=scrubbed_env()`; `engine/tools/conftest.py` carries the autouse fixture so every pytest discovers no inherited `GIT_*`. Closes the S-0033 vector.
- **Mempalace mine atomic-write** is mechanized by the `mempalace-hook-wrapper.sh` extension per [ADR 0045](engine/adr/0045-shared-state-integrity-discipline.md): pre-mine snapshot via `cp -a`, post-mine `probe_palace.py` verification, rollback on probe failure (palace + KG together), one `palace.last-good` retained between hook fires. Closes the S-0034 vector.
- **Boot-time shared-state health probes** are mechanized by `validate.py --health-probe-only` invoked from `session-start.sh` per [ADR 0045](engine/adr/0045-shared-state-integrity-discipline.md). `probe_palace.py` (chromadb opens, lists, counts) and `probe_repo.py` (effective + parent-clone direct `core.bare`, HEAD resolution) report findings to stderr at every session boot. Hard-broken findings emit a LOUD attention surface; the hook still exits 0 to avoid catch-22 boot-blocks.

Soft enforcement preserves AI judgment. A reminder can be acknowledged and overridden in legitimate cases (an ADR supersession that intentionally reuses an existing decision drawer; a STATE.md edit with a transient placeholder mid-edit). Hard enforcement was rejected for these rules in [ADR 0043](engine/adr/0043-hook-architecture.md) because the legitimate-exception surface is non-empty.

## Topical pointers

Procedural depth lives in `engine/operations/` — one file per topic. Browse with `ls engine/operations/`. Index at `engine/operations/README.md`. High-frequency entries:

- `session-build-lifecycle.md` — boot, eager-claim, in-session work, push cadence.
- `session-shutdown-sequence.md` — audit, spot-check, `engine/STATE.md`, `engine/ENGINE_LOG.md`, archive.
- `mempalace-operations.md` — install, init, mine, hook wiring, query patterns.
- `mempalace-tagging-conventions.md` — `exploration` / `decision` / `work` tags.
- `tools-validate-interpretation.md` — hard-fail vs soft-warn, what to do with each.
- `escalation-criteria.md` — when to interrupt user; redundant with auto-mode criteria above but with worked examples.
- `adr-authoring.md` — Nygard template, status conventions, when an ADR is warranted.
- `code-discipline.md` — three-layer expression contract for AI-authored code (per ADR 0038): contract-first prose, mechanical gates (ruff/mypy/pytest in pre-commit), cold-context review pass at shutdown.
- `migration-discipline.md` — Layer 1 source-of-truth for SQL migrations (per ADR 0039): per-migration contract block shape, naming convention, transaction wrap, CASCADE discipline, RLS posture, CHECK constraint shape, rollback authorship, cold-review prompt template.
- `expression-contract-instantiation.md` — pattern instantiation table (per ADR 0039): per-pattern Layer 1 / Layer 2 / Layer 3 mapping. New AI authoring patterns add a row before authoring begins ("no row, no authoring").
- `build-readiness-gate.md` — halting discipline before substantive build sessions (per ADR 0040): adversarial reconnaissance, Tier 1 / Tier 2 / Tier 3 triage, build-readiness report at `engine/build_readiness/<phase>_<chunk>.md`. Build sessions read the report at boot; halt on unresolved Tier 1.
- `cascade-discipline.md` — three soft-warn validator checks plus manual procedures for cascade audits (per ADR 0041): superseded-ADR-citation currency, ADR back-reference orphan detection, ADR Consequences-deliverable audit. Manual procedures attached to file rename, ADR supersession, ops-doc restructure, deliverable handshake.
- `cross-references.md` — engine-side dependency map (companion to product/docs/CROSS_REFERENCES.md): engine ADRs → consumers; operations docs → consumers; tools → consumers; harness → consumers. Read when restructuring an engine ADR, ops doc, or tool.
- `soft-warn-lifecycle.md` — how soft-warns surface across sessions (per ADR 0042): trend canon in committed `engine/session/archive/*.json`, persistent-warn surface at boot, escalation criterion at ≥10 sessions persistence.
- `health-check.md` — audit categories, report template, cadence policy.

Project context (the *what* and *why*, not the *how*):

- `product/docs/MISSION.md` — vision, audience framing, cross-domain commitment.
- `product/docs/CROSS_REFERENCES.md` — high-value file dependencies.
- `engine/STATE.md` — current state. `ROADMAP.md` — full arc.
