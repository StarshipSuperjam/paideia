# ADR 0044 — Skill conversion: recipe-shaped procedures become Skills; reference docs stay docs

- **Status:** Accepted
- **Date:** 2026-05-02
- **Deciders:** S-0031

## Context

The `engine/operations/` library carries roughly 15 markdown files. Two shapes coexist in the library, and they call for different invocation models:

- **Recipe-shaped docs** are step-by-step executable workflows the AI follows top-to-bottom at a discrete moment. [`session-build-lifecycle.md`](../operations/session-build-lifecycle.md) at session boot, [`session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) at session close, [`build-readiness-gate.md`](../operations/build-readiness-gate.md) before substantive build sessions. The AI reads these documents once at the appropriate moment and follows the steps in order.
- **Reference-shaped docs** are consulted repeatedly during work, not invoked as a unit. [`escalation-criteria.md`](../operations/escalation-criteria.md) when judging whether to interrupt the user, [`code-discipline.md`](../operations/code-discipline.md) when authoring Python, [`tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) when triaging validator output, [`mempalace-tagging-conventions.md`](../operations/mempalace-tagging-conventions.md) when capturing memory. The AI dips into these documents at any of many junctures during a session.

The Claude Code harness exposes two relevant invocation surfaces. **Slash commands** (`.claude/commands/<name>.md`) are user-typed. The project carries one (`/start-engine`) backing the boot-procedure recipe. **User-defined Skills** (`.claude/skills/<name>/SKILL.md`) are AI-invoked via the `Skill` tool; with `disable-model-invocation: true` the model invokes deliberately rather than auto-firing on description match. Skills are first-class with the bundled `anthropic-skills:*` and other plugin-namespaced skills the harness ships.

The mismatch the project has been carrying: recipe-shaped ops docs are read-and-followed by AI discipline. The AI knows the document exists, knows when to read it, and reads it. There is no hard error when the AI skips a step, reorders steps, or paraphrases the procedure from memory. The S-0030 audit did not measure recipe-doc compliance directly, but the cadence-trigger off-by-one (the trigger logic in `start-engine.md` step 2 contradicted the prose intent in ROADMAP.md and ADR 0022, and persisted unnoticed across 30 sessions) is exactly the kind of latent drift recipe-as-doc-only invites.

Reference docs do not have the same drift exposure. They are read on demand; the AI's incentive at the moment of reading is to extract the relevant rule for the case in hand. There is no "follow the document top-to-bottom" surface for reference docs to drift against.

The conversion is therefore partition-shaped: recipes become Skills (canonical executable invocation, registered with the harness), reference docs stay docs (read on demand, no canonical entry point needed).

## Decision

Three recipe-shaped operations docs convert to user-defined Skills under `.claude/skills/`:

1. **`.claude/skills/session-build-lifecycle/SKILL.md`** — boot procedure (read STATE.md, check cadence, query MemPalace, read referenced docs, eager-claim ritual, begin work) plus in-session commit cadence and push policy. Frontmatter `disable-model-invocation: true`.
2. **`.claude/skills/session-shutdown-sequence/SKILL.md`** — close procedure (audit pass, spot-check, cold-context review pass for Python and SQL, update STATE.md, update ENGINE_LOG.md, fill `outcome_summary` plus `outcome_summary_soft_warns`, archive, final commit + FF + push). Frontmatter `disable-model-invocation: true`.
3. **`.claude/skills/build-readiness-gate/SKILL.md`** — gate procedure (read chunk + ADRs, launch Explore agents, triage Tier 1/2/3, resolve Tier 1 with user, author resolutions, write report, source-document citation pass, cold-review pass against citations, update STATE.md). Frontmatter `disable-model-invocation: true`.

Each Skill's body is the canonical executable form of the procedure. The corresponding ops doc (`engine/operations/session-build-lifecycle.md`, etc.) remains in place as the Layer 1 source-of-truth governed by [`document-voice.md`](../operations/document-voice.md) per [ADR 0036](0036-expression-contract-for-inward-documents.md); each ops doc gains a header line pointing at the Skill: "Canonical invocation: Skill `<name>`." The ops doc is the readable contract; the Skill is the invocable entry point.

Reference-shaped ops docs explicitly do NOT convert. The current set, named so the boundary is auditable:

- [`escalation-criteria.md`](../operations/escalation-criteria.md)
- [`code-discipline.md`](../operations/code-discipline.md)
- [`migration-discipline.md`](../operations/migration-discipline.md)
- [`expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md)
- [`tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md)
- [`mempalace-operations.md`](../operations/mempalace-operations.md)
- [`mempalace-tagging-conventions.md`](../operations/mempalace-tagging-conventions.md)
- [`adr-authoring.md`](../operations/adr-authoring.md)
- [`document-voice.md`](../operations/document-voice.md)
- [`health-check.md`](../operations/health-check.md)
- [`cascade-discipline.md`](../operations/cascade-discipline.md)
- [`soft-warn-lifecycle.md`](../operations/soft-warn-lifecycle.md)
- [`cross-references.md`](../operations/cross-references.md)
- [`README.md`](../operations/README.md)

The recipe-vs-reference partition criterion: a doc converts to a Skill iff the AI consumes it as a top-to-bottom procedure at a discrete moment (read-once, follow-in-order, exit when done). A doc stays a doc iff the AI consumes it at multiple junctures and extracts case-relevant rules without following start-to-finish.

The partition is not a permanent boundary; a reference doc that grows a procedure section may motivate a future Skill conversion, and a Skill whose body comes to be read more for its embedded reference content than its procedure may de-convert. Refinements are amendment-tracked under this ADR; abandoning the partition or removing the recipe-vs-reference framing requires superseding.

## Consequences

`.claude/skills/` (currently absent) is created. Three new directories under it carry SKILL.md files with frontmatter (`name`, `description`, `disable-model-invocation: true`) and a body adapted from the corresponding ops doc.

The three ops docs that converted gain a "Canonical invocation: Skill `<name>`" header line. Their substantive content remains intact — they are the Layer 1 source-of-truth under [ADR 0036](0036-expression-contract-for-inward-documents.md). The Skill body is the same procedure in skill voice; the doc is the same procedure in reference voice. The two are kept in sync by hand at authoring time. (A future enhancement could mechanize the sync — e.g., generate the Skill body from the doc — but the current scope is one-time conversion.)

CLAUDE.md's "Two session modes" section gains a paragraph naming the Skills as the canonical invocation path: `/start-engine` slash command at boot triggers (or invokes) the `session-build-lifecycle` Skill; the `session-shutdown-sequence` Skill is invoked at close; the `build-readiness-gate` Skill is invoked before substantive build sessions. The slash command remains the user-facing entry point; the Skills are the internal procedure surfaces.

The conversion does not change behavior in any session that follows the procedures correctly today. The benefit is forward-looking: future sessions encountering a procedure step the documentation ambiguates can fall back on the Skill body as the canonical form, and tooling (the `Skill` invocation tool) records the moment the procedure was invoked, providing a paper trail the doc-only model lacks.

Trade-offs accepted:

- **Two surfaces per recipe.** The Skill body and the ops doc both describe the procedure. Drift between them is a new failure mode. Mitigation: the ops doc remains the source-of-truth (Layer 1 under ADR 0036), and the Skill body is generated by adaptation, not by independent authoring; updates to the procedure flow doc → Skill, not Skill → doc. The next health check (S-0040 under the cadence-10 default per ADR 0022 Consequences amendment at S-0033) audits drift.
- **`disable-model-invocation: true` requires deliberate AI invocation.** The AI must call the `Skill` tool explicitly; the harness will not auto-fire the Skill based on description match. This is the design intent — these are session-protocol invocations, not pattern-matched skill triggers. The cost is that the AI must remember to invoke; the same posture-vs-machinery question that motivated this ADR partly recurs at the invocation layer. The slash command (`/start-engine`) and the SessionStart hook (per ADR 0043) together shoulder the boot-time invocation; shutdown invocation remains posture (the AI at end-of-work invokes by discipline). This is acceptable: the failure mode the conversion addresses is procedure-content drift, not invocation drift, and reference-doc invocation has always been posture without observable problems.
- **The `.claude/skills/` directory adds a third location for procedural content.** Existing locations: `engine/operations/` (Layer 1 source-of-truth), `.claude/commands/` (slash commands). Skills are the third. Mitigation: each location has a clear partition criterion (Layer 1 doc; user-typed entry point; AI-invoked procedure), and CLAUDE.md's "Topical pointers" section indexes all three.
- **Skills are not validated by `validate.py`.** The validator does not currently check SKILL.md frontmatter validity or body shape. A future validator extension could add this; the current scope leaves it manual. Skill bodies fall under [`document-voice.md`](../operations/document-voice.md) governance per [ADR 0036](0036-expression-contract-for-inward-documents.md) — the Prose / inward expression-contract row in [`expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md) covers them.
- **No new authoring pattern.** Skills do not warrant a new row in `expression-contract-instantiation.md`; they are markdown under the Prose / inward pattern with additional frontmatter shape. The frontmatter shape is fixed by the harness, not by the project; it is not a contract the project authors. Adding a row is overkill.

The conversion is one-shot for the three recipes named. Subsequent recipe-shaped procedures (a hypothetical "phase-close ceremony," a hypothetical "ADR-amendment ritual") would convert at the moment of authoring under this ADR's partition criterion.

## Consequences amendment — S-0163 (Issue #129 — Skill ↔ Layer-1 parity mechanized; drift-direction assumption falsified)

Two of this ADR's Consequences claims did not hold, and a third under-counted the recipe set:

- **The "doc → skill, not skill → doc" drift assumption is falsified.** The Consequences trade-off bullet asserted "updates to the procedure flow doc → Skill, not Skill → doc" and trusted "the next health check audits drift." The S-0142→S-0161 window produced a five-Issue drift cluster ([#122](https://github.com/StarshipSuperjam/paideia/issues/122)-[#126](https://github.com/StarshipSuperjam/paideia/issues/126)) in which drift ran *both* directions and *between siblings*: [#123](https://github.com/StarshipSuperjam/paideia/issues/123) was command ↔ skill, [#125](https://github.com/StarshipSuperjam/paideia/issues/125) is skill ↔ skill (a Skill *missing* a step its command and Layer-1 doc both carry). "The Skill is the canonical form" is an aspiration, not a guarantee.
- **The "future validator extension" is now realized — for the enumeration slice.** This ADR's Consequences flagged "Skills are not validated by `validate.py` ... A future validator extension could add this." [ADR 0089](0089-skill-layer1-parity-validator-check.md) lands that extension: `validate_skill_layer1_parity()` / the `skill_layer1_parity_drift` soft-warn compares each recipe Skill's procedure step-number *set* against its Layer-1 doc's. It mechanizes the *enumeration-parity* slice (a step present on one side only — the #123 / #125 class). **Intra-step content parity remains hand-discipline** — a step's prose drifting from its sibling's ([#122](https://github.com/StarshipSuperjam/paideia/issues/122)) or a step omitting required fields ([#126](https://github.com/StarshipSuperjam/paideia/issues/126) part 1) is not caught by a step-set comparison, and a title comparison would fire false positives because skill voice and reference voice legitimately differ in wording.
- **There are four recipe Skills, not three.** This ADR converted three; `routine-mode-lifecycle` followed at S-0044 per [ADR 0051](0051-routine-mode-and-engine-loop.md). The ADR 0089 parity check covers all four pairs.

The recipe-vs-reference partition itself is unchanged and unsuperseded; this amendment records present truth about the drift-direction model and the now-mechanized parity slice.

## See also

- [ADR 0036](0036-expression-contract-for-inward-documents.md) — the Layer 1 source-of-truth ops docs are governed by; Skill bodies fall under the same contract.
- [ADR 0043](0043-hook-architecture.md) — sibling structural decision authored in S-0031; introduces three new hooks. The two ADRs together codify the harness-mechanization slice of the approved infrastructure plan.
- [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md), [`session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md), [`build-readiness-gate.md`](../operations/build-readiness-gate.md) — the three converted recipes.
- [`engine/operations/expression-contract-instantiation.md`](../operations/expression-contract-instantiation.md) — Prose / inward row covers Skill bodies.
- [`.claude/skills/`](../../.claude/skills/) — destination directory for the three new skill modules.
- [`.claude/commands/start-engine.md`](../../.claude/commands/start-engine.md) — slash command entry point for the build-lifecycle Skill.
