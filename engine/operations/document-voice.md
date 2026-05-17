# Document voice — expression contract for inward-facing documentation

> An expression contract is a tool that constrains how the AI expresses itself for a specific surface. This document is the expression contract governing inward-facing project documentation: `docs/MISSION.md`, `ROADMAP.md`, the `docs/` tree, ADRs, and root-level project files. The project's other expression contract — [`AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md), contracted in [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — governs learner-facing prose. They are kindred tools, separately scoped.

## Posture

Inward-facing project documents are **present-state descriptions** of the project's mission, architecture, operating discipline, and open questions. They speak for the project as it stands now — not for the path by which the project arrived at its present state. The reader is a future implementer or a future session booting cold; their need is what is true now, not what changed.

This contract protects that present-state purpose against authorship-history leakage. The artifact's purpose stays at the front; the production trace sits in its proper layer.

This is a working contract among the people and sessions that author and maintain governed documents. It governs voice, not content.

## The voice

**Present tense, declarative, current state.** Documents assert what is the case ("the graph encodes pedagogical prerequisites"; "the audience is freshmen calibrating up"; "Discovery, Planning, and Engagement are the three primary surfaces"). The author position is the project speaking about itself as it stands — not a session reporting on what it just decided.

**Cross-references are bibliographic, not running commentary.** When a doc names a commitment contracted in an ADR, the cross-reference belongs in a "See also" section at the end of the relevant block — or as a single end-of-section pointer when the block is shorter — not as a parenthetical attached to every assertion. The reader who wants to follow the contract layer can; the reader who is here for the present-state description is not interrupted by per-sentence citations.

**The reader does not need to know what the document used to say.** A document that opens by summarizing its own revision history before describing its subject is asking the reader to absorb the path before reading the present. The mission *now* is the mission; the architecture *now* is the architecture. Earlier versions are part of the project's history, recoverable from the trace layers below — not part of the present-state description.

## Where the trace lives

Traceability is a four-layer system, redundantly covering different facets of the project's history. The body of a governed document does not duplicate any of them.

- **ADRs** — the contract layer. Settled architectural decisions, Nygard format, Status / Context / Decision / Consequences. Citable and durable. Per [`adr-authoring.md`](adr-authoring.md).
- **ENGINE_LOG.md** — the dated narrative. Material engine changes by category (Added / Changed / Removed / Deprecated). Anyone scanning project history reads this. (Was named `CHANGELOG.md` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md); the `CHANGELOG.md` filename is now reserved for the future learner-visible product release log.)
- **engine_memory `decisions`-room drawers** — the conversational story. Verbatim form, recoverable by similarity search. Per [`engine-memory-conventions.md`](mempalace-tagging-conventions.md).
- **Git history** — the granular blame. Every line's authorship and editing history, recoverable by `git log` and `git blame`.

The four layers compose. ADRs answer *what's settled*; ENGINE_LOG answers *when did it change*; MemPalace answers *have we considered X before*; git answers *who wrote this line, and when*. A reader who wants the path to a present-state assertion has four ways to find it. Governed documents trust this redundancy and describe present truth without inlining the trace.

## Worked example

Source: `docs/MISSION.md`, opening blockquote.

### Before

> What Paideia is, who it serves, and the commitments that make it different. Vision and audience framing extracted from CONTEXT.md (now retired) at S-0002. Project disposition revised at S-0012 per ADR 0032. Mission focus realigned at S-0013 per ADR 0033 — Paideia fills the structured-guidance gap a self-learner has when there is no teacher.

### After

> Paideia fills the structured-guidance gap a self-learner has when there is no teacher. This file describes what Paideia is, who it serves, and the commitments that distinguish it.

### What the rewrite does

The opening states the mission. A reader picking up the file encounters the project's mission as it currently stands — not the path the file took to its current state. The sentence is short, declarative, and stays in the present tense.

The deletions name the failure mode by their absence. The "extracted from CONTEXT.md (now retired) at S-0002" clause was authorship history; CONTEXT.md's retirement is in ENGINE_LOG, S-0002's contribution is in `session/archive/S-0002.json`, and the file's edit history is in git. The "Project disposition revised at S-0012 per ADR 0032 ... Mission focus realigned at S-0013 per ADR 0033" sequence was supersession narration; ADRs 0032, 0033, and 0035 carry the chain themselves, with one-directional Status pointers per [`adr-authoring.md`](adr-authoring.md). The reader who wants to follow that chain can; the reader who wants the present mission encounters it in the first sentence.

The ADR cross-references that survive — MISSION.md naming "structured guidance for self-learners" as the mission and the contract being ADR 0033 — belong in a "See also" footer or end-of-section pointer, not in the title-page blockquote.

## Scope

**Governed:**

- All `docs/*.md` and `docs/**/*.md`, including the `docs/operations/` and `docs/pedagogy/` trees
- `docs/MISSION.md` and `ROADMAP.md` (with three-speech-acts handling — see below)
- Root-level `README.md`, `CLAUDE.md`, `HANDOFF.md`, `SECURITY.md`
- `AGENT_INSTRUCTIONS.md`
- All `adr/*.md` in non-Superseded status, plus `adr/README.md`
- `docs/CROSS_REFERENCES.md`
- `docs/tensions.md` open entries (resolved entries are exempt — see below)
- Default rule: any file newly authored under `docs/`, `docs/operations/`, or as a non-Superseded ADR is governed automatically.

**Exempt** — journal and snapshot files that are dated chronicles by design:

- `STATE.md` — the daily snapshot
- `ENGINE_LOG.md` — the dated narrative (was `CHANGELOG.md` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md))
- `session/archive/*` — per-session journal
- `docs/tensions.md` resolved entries — preserved historical record per the project's tension-resolution discipline (the entry was a present-state open question when authored; its `Resolved: YYYY-MM-DD` marker is the journal moment that closed it)
- ADRs in Status: Superseded — they retain the supersession pointer per [`adr-authoring.md`](adr-authoring.md)

The exemption distinguishes *dates that are the artifact's content* (an ENGINE_LOG entry, a STATE.md snapshot, a Resolved-tension marker) from *dates that narrate the revision history of an otherwise current-state document* (a "Revised: 2026-04-30 (S-0012 — per ADR 0032)" footer inside a body section of MISSION.md). The first is the artifact doing its job; the second is in-document revision narration the contract forbids.

### ROADMAP.md three-speech-acts handling

ROADMAP.md mixes three kinds of content. Each is governed separately:

- **Phase scope, output, success criteria** — present-tense plan as it stands. Governed.
- **Cross-phase strong working commitments** — present-tense commitment list. Governed.
- **Per-phase additions and revisions** — the content survives in the phase prose at present-state voice; date-stamp markers like `**Added: YYYY-MM-DD (S-NNNN — per ADR ZZZZ ...)**` migrate to ENGINE_LOG.
- **Supersession narration of prior phase plans** — migrates entirely to git history; not duplicated in-document.

ROADMAP.md is the file most likely to drift, because phase-narrative is part of how the file works. Authoring sessions touching it distinguish *the plan as it stands* (governed) from *what changed in S-NNNN* (ENGINE_LOG and git).

## Amendment discipline

This contract is governed positively. When a new failure mode surfaces — an authoring move that the present voice statement does not catch — the response is to **refine the positive voice description**, not to append a prohibition.

A refinement looks like this: a session encounters a passage where verification stamps have accreted ("Last verified: 2026-05-15. Re-verified: 2026-06-22."). This is a failure mode the present posture implicitly forbids but does not name. The contract's amendment is not "forbidden token: Last verified". The amendment sharpens the posture itself — for example: *the document describes what is the case as of the moment of reading; verification dates, like revision dates, belong in the trace layers — git history records when each line was last written, and ENGINE_LOG records when material changes landed*. The discipline grows in precision; the prohibition list does not exist.

**Refinements are ENGINE_LOG-tracked but require no new ADR.** They sharpen the present description.

**Substantive changes to the voice posture itself require a superseding ADR.** If the project decides that governed documents should narrate their own revision history inline — that the four-layer trace system is insufficient — that is a posture change, not a refinement, and warrants the deliberation a superseding ADR forces.

This amendment asymmetry is appropriate to what this contract protects. Different expression contracts in the project carry amendment disciplines suited to their load-bearing surface. [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md)'s rendering policy enumerates forbidden tokens as its load-bearing surface; tightening (adding a forbidden token) is cheap, loosening (removing one) is expensive, because what that contract protects is the hidden machinery each new token covers. This contract's load-bearing surface is the positive voice characterization, and the asymmetry inverts: refinement (sharpening the characterization) is cheap because it preserves the discipline; posture change is expensive because it is what the discipline binds.

## See also

- [`AGENT_INSTRUCTIONS.md`](../../product/AGENT_INSTRUCTIONS.md) — the project's expression contract for learner-facing prose.
- [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) — the rendering policy contract `AGENT_INSTRUCTIONS.md` operationalizes.
- [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) — the decision record establishing this contract.
- [`adr-authoring.md`](adr-authoring.md) — the contract layer of the four-layer trace system; ADR vs ENGINE_LOG vs MemPalace boundary.
- [`engine-memory-conventions.md`](mempalace-tagging-conventions.md) — the `decision` tag on the conversational-story layer.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — per-session protocol for landing changes in governed docs, ENGINE_LOG, and STATE.md.
