# Build-readiness gate — halting discipline before substantive build sessions

> The operational surface for [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md). The gate runs before every substantive build session. Its deliverable is a build-readiness report at `engine/build_readiness/<phase>_<chunk>.md` that the build session reads at boot.
>
> Sibling to [`session-build-lifecycle.md`](session-build-lifecycle.md) (the build session itself) and [`session-shutdown-sequence.md`](session-shutdown-sequence.md) (close-of-session protocol). The gate sits temporally before the lifecycle.
>
> **Canonical invocation:** Skill `build-readiness-gate` (per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md)). The skill's body is the procedural form of this document; this document is the Layer 1 source-of-truth prose. Updates flow doc → skill, never the reverse.

## When the gate runs

A gate session is required before any substantive build session. Substantive = authors or modifies load-bearing artifacts that downstream phases depend on (schema, durable code, content, validators, teaching layer). Non-substantive sessions — health checks, ENGINE_LOG-only edits, operational doc refinements, retrievability cleanups — proceed under the standard build lifecycle without a preceding gate.

The build_plan/ chunk being prepared is the unit the gate scopes against. A multi-chunk phase consumes one gate session per chunk (or one per phase if the chunks share a single decision surface).

The gate session itself is operational; gate sessions are not preceded by gate sessions. No infinite regression.

## Procedure

### 1. Read the build_plan chunk and load-bearing ADRs

The gate session begins by reading the build_plan/ file for the work being prepared. Note the chunk's load-bearing ADRs (named in the chunk's "Load-bearing ADRs" section), source documents (named in "Source documents (boot reads beyond CLAUDE.md auto-load)"), and success criteria. These are the inputs the build session will operate against; the gate's job is to surface what's underspecified, ambiguous, or unsettled in any of them.

### 2. Launch up to three Explore agents in parallel

The gate session runs adversarial reconnaissance through Explore subagents — fresh context, no session premises, structured prompts. Three parallel perspectives are the default:

- **Build-plan & source-doc audit.** Reads the chunk and its source docs (architecture.md, learner-model.md, etc., per the chunk's references). Surfaces cross-doc disagreements, underspecified types and constraints, JSONB shape ambiguities, missing index/PK/FK decisions, missing CHECK constraint contracts, hidden assumptions about prerequisite tables.

- **Discipline machinery audit.** Reads the relevant expression-contract rows (per [`expression-contract-instantiation.md`](expression-contract-instantiation.md)), the gate stack (validate.py, pre-commit hook, cold-review trigger), and the operational docs the build session will follow. Surfaces gaps: an authoring pattern with no row, a gate that doesn't cover the chunk's artifact type, a layer that the chunk's work would escape.

- **Open tensions & deferred decisions audit.** Reads [`../../product/docs/tensions.md`](../../product/docs/tensions.md), engine STATE.md's "Open tensions and deferred decisions" section, the build_plan/ MANIFEST and adjacent chunks. Surfaces decisions the chunk would settle by accident (an OQ tagged "decide-before Phase N" where the chunk hard-codes an answer), backup-tag staleness, health-check cadence proximity, multi-session phase coordination.

Each agent returns triaged findings with citations (file:line). Agents do not converge — three perspectives surface three angles, and the gate session synthesizes.

The "up to three" upper bound is calibrated to context cost vs. analysis breadth. A tight, well-specified chunk may need only one agent; a broad cross-cutting chunk benefits from three. The choice is the gate session's judgment call. Adding a fourth perspective is a refinement-signal under [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s amendment discipline.

### 3. Triage findings into Tier 1 / Tier 2 / Tier 3

Each finding lands in exactly one tier:

- **Tier 1 — must resolve before the build session opens.** The build session cannot author its target artifact without an answer. Examples: auth model choice (FK target table), RLS posture, enum vocabularies, column shape that downstream code reads, the discipline-instantiation row for a new authoring pattern. Tier 1 findings halt the build session until resolved.

- **Tier 2 — settle in advance and document.** The build session *could* improvise an answer, but doing so under build pressure produces the compound-drift mode the gate exists to prevent. Examples: CHECK constraint shapes, primary key choices, index decisions, default values, rollback test specifics, opt-out comment markers. Tier 2 decisions land in the build-readiness report's "Tier 2 decisions" section as concrete answers (column types, constraint forms, exact CHECK expressions). The build session implements without re-deciding.

- **Tier 3 — name as deferred forward-pointer.** A decision that genuinely belongs to a later session, where naming it explicitly prevents it from disappearing. Examples: a remapping formula deferred to Phase 6 (with a schema comment naming the deferral), a column reservation deferred to a future ADR, a coordination note for the next health check. Tier 3 entries land in the report so the build session and downstream sessions see them.

The triage is not algorithmic — judgment-bound. A finding that the gate session classifies as Tier 2 may, on user review, escalate to Tier 1 (must resolve before authoring) or de-escalate to Tier 3 (acceptable to defer). The gate session's first triage is a draft; user review is the load-bearing pass.

### 4. Resolve Tier 1 findings with the user

The gate session is conversational by default. For each Tier 1 finding:

1. State the finding with its citations and why it matters now.
2. Present resolution options with tradeoffs.
3. Use AskUserQuestion or direct conversation to settle.
4. Author the resolution artifact: ADR amendment, sibling vocabulary doc, ADR sub-decision update, or a new ADR if the resolution warrants one.

The gate session does not push past unresolved Tier 1. If a Tier 1 finding requires multi-conversation reasoning, the gate session may pause and surface "this needs more conversation than this session can hold" — escalating per [`escalation-criteria.md`](escalation-criteria.md).

The user-directed posture is what distinguishes gate sessions from build sessions. Build sessions running in auto-mode push through routine judgment calls; gate sessions surface them. The mode-switch is structural: a gate session that finds itself wanting to push through a Tier 1 has misidentified its mode.

### 4a. No descoping or reordering at gate time (per ADR 0049)

The gate session itself is a descoping vector — a gate that quietly trims the chunk's deliverables vs. the original build-plan scope, or that proposes reordering ("let's do Phase 5 before Phase 4.5") under the guise of triage, becomes the failure mode the scope-discipline machinery exists to catch.

Any reduction OR reordering of declared deliverables vs. the build-plan chunk's stated scope must be flagged to the user explicitly, not silently absorbed into the gate report. The flag carries:

- What the chunk said it would deliver.
- What the gate is now proposing.
- Why the change is warranted (a Tier 1 finding that surfaced a structural blocker, a downstream phase that subsumes the work, an ADR that supersedes the chunk's premise, etc.).

The user accepts (proceed with the new scope; the build-plan chunk is amended in the same gate session) or rejects (preserve original scope; the gate triages around the proposed change rather than absorbing it). Silent absorption is not an option.

This clause exists because the gate session's auto-mode posture (per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)) is *conversational by default* — exactly the surface most amenable to drift. The mode-switch from auto to conversational does not by itself prevent quiet scope erosion; this clause makes the erosion visible.

### 5. Author resolution artifacts

Tier 1 resolutions produce concrete artifacts the build session will reference:

- ADR amendments (recorded in ENGINE_LOG per the existing amendment-asymmetry pattern).
- New ADRs when the resolution warrants one (per [`adr-authoring.md`](adr-authoring.md)).
- Sibling Layer 1 documents (e.g., a TENSION_VOCABULARY.md authored alongside the schema migration that consumes it).
- Pattern instantiation rows in [`expression-contract-instantiation.md`](expression-contract-instantiation.md) when the gate opens a new authoring pattern.

Tier 2 decisions live in the build-readiness report directly; they do not produce separate artifacts. Tier 3 forward-pointers also live in the report.

### 6. Write the build-readiness report

Path: `engine/build_readiness/<phase>_<chunk>.md` where `<phase>` matches the build_plan/ chunk's phase identifier (e.g., `phase_3`, `phase_4`, `phase_5_seed_geometry`) and `<chunk>` names the specific work (e.g., `sql`, `graph_validation`, `seed_geometry_part_1`). Multi-chunk phases get one file per chunk; single-chunk phases use the phase name alone (`phase_3_sql.md`).

The report's structure is the template below.

### 7. Source-document citation pass (per ADR 0040 gate-on-the-gate amendment)

Before the report is declared complete, every Tier 1 and Tier 2 decision in the report must explicitly cite the source-document line(s) that ground the decision. The citation form is `<doc-path>:L<line>` or `<doc-path>:L<start>-<end>` for ranges, or `<ADR-id>:L<line>` for ADR citations.

If a decision is grounded in multiple source documents (e.g., architecture.md establishes the shape, ADR 0026 establishes the rationale), cite both. If a decision is grounded in conversational consensus from this gate session rather than a source document, write `decided in S-<NNNN> conversation` — but flag it in Tier 1's resolution prose so the cold-review pass below knows it has no document to verify against.

The citation discipline serves the cold-review pass that follows; without citations the cold-review has no grounding to verify against and falls back to authorial trust (which is what the gate exists to avoid).

### 8. Cold-review pass against citations (per ADR 0040 gate-on-the-gate amendment)

Launch a sub-agent (Explore type) with no session context. Brief: "Read this build-readiness report. For each Tier 1 and Tier 2 decision, fetch each cited source-document passage. Verify that the cited passage supports the decision claimed. Report per decision: matches | partial | discrepancy | citation-not-found | citation-misquoted, with the relevant excerpt for any non-match. Also flag any decision lacking a citation that names a fact-of-the-world rather than a conversational consensus."

The sub-agent has no memory of the gate session's authoring premises and so cannot share its blind spots. The mechanism targets the failure mode S-0028 surfaced: the gate session improvised a column shape (UUID for `mastery_snapshots.concept_id`) that contradicted [`product/docs/architecture.md`](../../product/docs/architecture.md)'s portable-mastery design (which requires TEXT). The citation-and-cold-review combination would have caught this at gate close: the Tier 2 decision had no architecture.md citation, the cold reviewer would have flagged "T2-C: no source citation for column type — what's the design source?", the gate session would have had to look up architecture.md, and the divergence would have surfaced before S-0028.

Findings block gate close until resolved. Resolution paths:

- **Match.** No action; the citation supports the decision.
- **Partial.** The citation supports part of the decision; either tighten the decision to what the citation supports, or add additional citations covering the rest.
- **Discrepancy.** The citation contradicts the decision. Either the decision is wrong (amend it to match the source) or the source is wrong (amend the source — typically with the user, since source-document changes are themselves substantive). Either way, the gate session does not close until alignment is restored.
- **Citation-not-found.** The cited line does not exist; the gate session likely cited a stale line number after editing the source. Update the citation.
- **Citation-misquoted.** The cited passage exists but the gate session's paraphrase of it is misleading. Rewrite the gate report's prose to match the source.

Findings are appended to the gate session's `outcome_summary` even after resolution — they are calibration data for refining the gate's adversarial-analysis stage (Step 2's Explore agents).

#### S-0028 case study — what cold-review would have caught

S-0028's Phase 3 SQL build session against [`../build_readiness/phase_3_sql.md`](../build_readiness/phase_3_sql.md) found four divergences mid-build:

| Gate report claim | Source-document reality | What cold-review would have surfaced |
|---|---|---|
| T1-A: DELETE trigger missing or under-specified for `auth.users` mirror | [`product/adr/0031-erasure-mechanism-and-individual-only-regime.md`](../../product/adr/0031-erasure-mechanism-and-individual-only-regime.md) Consequences mandates DELETE-trigger cascade alongside INSERT trigger | "T1-A cites no ADR/source for the trigger shape — only the auth model. What grounds the trigger specification?" |
| T2-C: `mastery_snapshots.concept_id UUID` | [`product/docs/architecture.md`](../../product/docs/architecture.md) Node Schema names id as TEXT (slugified concept identifier); portable-mastery commitment requires concept_id to match nodes.id | "T2-C cites no architecture.md line for concept_id type — what's the design source for UUID?" |
| T2-E: `edges.source_id`/`target_id UUID`, `type TEXT`, `provenance JSONB`, `evidence JSONB` | architecture.md Edge Schema names source_id/target_id as TEXT FK to nodes.id, `edge_type`, and TEXT for provenance/evidence | Same shape: "T2-E cites no architecture.md line for column types — what's the design source?" |
| Gate report's T1/T2 decisions in general | architecture.md is the authoritative design document for graph schema; gate report did not cross-reference it | "Multiple T2 decisions cite no source document for column types. Is architecture.md the authoritative design source? If yes, every T2 decision needs an architecture.md citation." |

The citation discipline (Step 7) plus the cold-review pass (Step 8) together convert "the build session catches gate errors mid-build" into "the gate session catches its own errors at close." The build session implements without re-deciding, which is the design intent of [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md).

### 9. Update STATE.md to point at the report

The "Next session work item" block in STATE.md gains a line: `Gated by [`engine/build_readiness/<phase>_<chunk>.md`](build_readiness/<phase>_<chunk>.md).` The build session reads the line at boot and follows it.

The gate session's `outcome_summary` records: report path, Tier 1 / Tier 2 / Tier 3 counts, citation-and-cold-review findings (matches and resolutions), any open follow-ups (gate sessions can also produce work that didn't fit the gate's scope and surfaces as "next gate session" or "next health check" pointers).

### 10. Close

Invoke the `session-shutdown-sequence` skill to run the close-of-session protocol. Gate sessions follow the standard shutdown like any session.

## Build-readiness report template

```markdown
# Phase <N> — <chunk-title> build-readiness report

> Authored by S-<NNNN> (gate session) for S-<MMMM> (build session) per
> [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md).
> The build session reads this at boot. If Tier 1 contains unresolved items
> at boot, the build session halts and escalates.

## Pre-session decisions

Tier 1 resolutions settled in S-<NNNN>:

- **<T1-A short label>** — <one-paragraph resolution>. <pointer to authored artifact>.
- **<T1-B short label>** — <one-paragraph resolution>. <pointer to authored artifact>.
...

## Tier 2 decisions

Concrete answers the build session implements without re-deciding. Each entry
names the question, the decision, and the rationale. Format favors copy-pasteable
SQL/code where applicable.

- **<T2-A short label>** — <decision in concrete form, e.g., specific CHECK constraint expression>.
- **<T2-B short label>** — <decision>.
...

## Tier 3 forward pointers

Decisions explicitly deferred. Each entry names the deferral, the deciding
phase, and where the entry lives if it's deferred to a structural marker (a
schema comment, an ADR amendment trigger, a tensions.md OQ entry).

- **<T3-A short label>** — <deferral statement>. Decide-before <phase>; <where it's marked>.
...

## Success criteria for the build session

Inherits from build_plan/<chunk>.md plus any session-specific verification
the gate exercise surfaced. Concrete checkpoints the build session verifies
at shutdown.

- <criterion 1>
- <criterion 2>
...

## Authored resolution artifacts (in S-<NNNN>)

- <list of files created/modified during the gate session that the build session references>

## See also

- [build_plan/<chunk>.md](../../build_plan/<chunk>.md) — the chunk being prepared.
- [<load-bearing ADR 1>] — <one-line summary>.
...
```

## Worked example — Phase 3 SQL build-readiness report

The S-0027 gate exercise produced [`../build_readiness/phase_3_sql.md`](../build_readiness/phase_3_sql.md) as this protocol's first execution. The report covers the Phase 3 SQL build for S-0028. Reading it cold, an S-0028 boot session encounters:

- **Pre-session decisions:** auth model (local users mirror), RLS posture (on with v1 policies), TENSION_VOCABULARY.md authored, universal expression contract widened (ADR 0039), gate protocol authored (ADR 0040), learner_events.context column shape pinned.
- **Tier 2 decisions:** for each of T2-A through T2-H from the adversarial analysis, a concrete answer — exact CHECK constraint expressions, mastery_snapshots column shape, graph_version contract, edges PK and unique constraint, session_id opaqueness, migration directory location, rollback test command sequence.
- **Tier 3 forward pointers:** superseded_by remapping (Phase 6), mastery formula version (acceptable; sub-signals stored raw), backup tag (cut in S-0027), health-check cadence (manual at S-0030), validate_graph stub (Phase 4 closes).

S-0028 reads the report, sees Tier 1 fully resolved, no AskUserQuestion needed for schema decisions, every column type named in advance — and proceeds to author SQL.

The worked example is itself dogfooded — S-0027's first exercise of the protocol produced the report S-0028 will consume.

## Failure modes the gate prevents

The gate is calibrated to a specific failure mode: a build session that begins with one or more Tier 1 decisions unresolved, improvises resolutions in the moment, and produces internally coherent artifacts that pass mechanical gates and survive cold review — because both layers check artifact-vs-contract alignment, not contract-vs-reality alignment. The compound-drift mode [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) names for code applies at the session level too: a contract authored under build pressure with a wrong premise has every layer compounding the wrong premise.

The gate compensates by inserting a halting checkpoint *before* the contract is authored, where the AI's premises can be challenged with fresh-context Explore agents and where the user can direct resolution before authoring begins.

The gate does NOT prevent:

- Drift within an in-flight build session — the existing standing rules ([CLAUDE.md](../../CLAUDE.md) Pushback rule, Auto-mode interrupt criteria, escalation-criteria.md) cover this.
- Errors in the build session's implementation against a clear contract — Layer 2 mechanical gates and Layer 3 cold-review cover this.
- Errors that surface only at runtime (e.g., a Postgres semantics surprise, a downstream code bug) — these are detected by the next phase's audit, ADR 0022 health checks, or live testing.

The gate's specific job is the session-entry-time decision space. Other failure modes have other compensations.

## Failure modes the gate introduces

Honest accounting:

- **Gate sessions consume slots.** Phase 3 used to be one slot (S-0028); now it is two (S-0027 gate + S-0028 build). The cost compounds across phases.
- **Triage judgment is fallible.** A Tier 2 decision the gate session classifies as "settle and document" might warrant Tier 1 escalation, or a Tier 3 deferral might be too quick a punt. User review at step 4 is the load-bearing pass; the gate session's first triage is a draft.
- **Adversarial-analysis dependency.** The gate's value depends on the Explore agents finding what's actually wrong. Three agents on a tight chunk may surface only superficial findings. Refining the prompts, adding a fourth perspective, or rerunning with different framing are the available levers — refinements under ADR 0040.
- **Conversational mode-switch overhead.** A user used to auto-mode build sessions experiences the gate session as conversational by default. The mode-switch is intentional but is friction.

These are the costs the project accepts in exchange for the compound-drift prevention the gate provides.

## Amendment discipline

The contract's load-bearing surface is the halting commitment — no substantive build session opens without a build-readiness report covering its work. Refinements within the gate model are cheap; restructuring the model is expensive.

**Refinements (ENGINE_LOG-tracked, no new ADR):**

- Refining the build-readiness report template (additional sections, sharper Tier definitions, worked-example updates).
- Adjusting the Explore-agent prompts (better triggers for specific finding categories).
- Adding or replacing a perspective in the parallel-agent step (e.g., adding a "performance-and-scale" perspective for chunks where it's load-bearing).
- Sharpening the "substantive vs operational" boundary (which session types require a gate).
- Adding a section to the report template (e.g., "External-system dependencies" if a phase touches new infrastructure).

**Posture changes (require superseding ADR):**

- Removing the build-readiness report requirement.
- Making the report optional rather than load-bearing.
- Dropping the "build session refuses to author with unresolved Tier 1" rule.
- Replacing the conversational-by-default posture for gate sessions with auto-mode default.

The asymmetry holds because what the contract protects is the halting discipline. Refinements preserve halting; posture changes alter what halting is calibrated to.

## Related — mechanism-first-exercise gate

[`mechanism-first-exercise-gate.md`](mechanism-first-exercise-gate.md) (per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md)) is the sibling pre-flight gate, structurally similar but with a different trigger:

- **Build-readiness gate (this doc):** *phase-triggered.* Fires before each substantive build session; one report per build_plan/ chunk.
- **Mechanism-first-exercise gate:** *mechanism-triggered.* Fires once per novel cross-cutting mechanism (per ADR 0053's trigger criterion), before that mechanism is used unattended for the first time.

Both gates use the same Tier 1 / Tier 2 / Tier 3 triage rubric, both produce reports under `engine/build_readiness/`, both run in conversational-with-the-user mode rather than auto-mode. They can both apply to a single phase if a new mechanism lands as part of that phase's work.

## See also

- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the citable contract this document operationalizes.
- [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — sibling structural ADR; the gate enforces "no row, no authoring" for new authoring patterns.
- [`session-build-lifecycle.md`](session-build-lifecycle.md) — boot procedure; amended in this commit to read the build-readiness report at boot.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — close-of-session protocol; gate sessions follow it like any session.
- [`escalation-criteria.md`](escalation-criteria.md) — when sessions interrupt the user; gate sessions invert the default for routine decisions (conversational by default).
- [`expression-contract-instantiation.md`](expression-contract-instantiation.md) — the per-pattern instantiation table; gate sessions add rows for new patterns.
- [`adr-authoring.md`](adr-authoring.md) — Nygard template; ADR amendments authored during gate sessions follow this.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — hard-fail vs soft-warn semantics; gate findings are not validate.py outputs but follow analogous triage discipline.
