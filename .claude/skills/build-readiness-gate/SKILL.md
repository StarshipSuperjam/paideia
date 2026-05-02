---
name: build-readiness-gate
description: Run a Paideia build-readiness gate session — adversarial reconnaissance via Explore subagents, Tier 1/2/3 triage, Tier 1 resolution with the user, source-document citation pass, cold-review pass against citations, build-readiness report at engine/build_readiness/<phase>_<chunk>.md. Invoke before any substantive build session per ADR 0040.
disable-model-invocation: true
---

# build-readiness-gate

> Canonical executable form of the Paideia build-readiness gate procedure. The Layer 1 source-of-truth prose lives at [`engine/operations/build-readiness-gate.md`](../../../engine/operations/build-readiness-gate.md) per [ADR 0036](../../../engine/adr/0036-expression-contract-for-inward-documents.md). This skill body is the procedural form per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Updates flow doc → skill, never the reverse.

## When to invoke

A gate session is required before any substantive build session per [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md). Substantive = authors or modifies load-bearing artifacts that downstream phases depend on (schema, durable code, content, validators, teaching layer).

Non-substantive sessions skip the gate: health checks, ENGINE_LOG-only edits, operational doc refinements, retrievability cleanups. The gate session itself is operational; gate sessions are not preceded by gate sessions. No infinite regression.

The build_plan/ chunk being prepared is the unit the gate scopes against. A multi-chunk phase consumes one gate session per chunk (or one per phase if the chunks share a single decision surface).

## Procedure

### 1. Read the build_plan chunk and load-bearing ADRs

Read the build_plan/ file for the work being prepared. Note:

- The chunk's load-bearing ADRs (named in the "Load-bearing ADRs" section).
- Source documents (named in "Source documents (boot reads beyond CLAUDE.md auto-load)").
- Success criteria.

These are the inputs the build session will operate against. The gate's job is to surface what's underspecified, ambiguous, or unsettled in any of them.

### 2. Launch up to three Explore agents in parallel

Adversarial reconnaissance through Explore subagents — fresh context, no session premises, structured prompts. Three parallel perspectives are the default:

- **Build-plan & source-doc audit.** Reads the chunk and its source docs (architecture.md, learner-model.md, etc.). Surfaces cross-doc disagreements, underspecified types and constraints, JSONB shape ambiguities, missing index/PK/FK decisions, missing CHECK constraint contracts, hidden assumptions about prerequisite tables.

- **Discipline machinery audit.** Reads the relevant expression-contract rows (per [`expression-contract-instantiation.md`](../../../engine/operations/expression-contract-instantiation.md)), the gate stack (validate.py, pre-commit hook, cold-review trigger), and the operational docs the build session will follow. Surfaces gaps: an authoring pattern with no row, a gate that doesn't cover the chunk's artifact type, a layer that the chunk's work would escape.

- **Open tensions & deferred decisions audit.** Reads [`product/docs/tensions.md`](../../../product/docs/tensions.md), engine STATE.md's "Open tensions and deferred decisions" section, the build_plan/ MANIFEST and adjacent chunks. Surfaces decisions the chunk would settle by accident, backup-tag staleness, health-check cadence proximity, multi-session phase coordination.

Each agent returns triaged findings with citations (file:line). Agents do not converge — three perspectives surface three angles, and the gate session synthesizes.

The "up to three" upper bound is calibrated to context cost vs. analysis breadth. A tight, well-specified chunk may need only one agent; a broad cross-cutting chunk benefits from three. The choice is the gate session's judgment call. Adding a fourth perspective is a refinement under [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md)'s amendment discipline.

### 3. Triage findings into Tier 1 / Tier 2 / Tier 3

Each finding lands in exactly one tier:

- **Tier 1 — must resolve before the build session opens.** The build session cannot author its target artifact without an answer. Examples: auth model choice (FK target table), RLS posture, enum vocabularies, column shape that downstream code reads, the discipline-instantiation row for a new authoring pattern. Tier 1 findings halt the build session until resolved.

- **Tier 2 — settle in advance and document.** The build session *could* improvise an answer, but doing so under build pressure produces compound drift. Examples: CHECK constraint shapes, primary key choices, index decisions, default values, rollback test specifics, opt-out comment markers. Tier 2 decisions land in the build-readiness report's "Tier 2 decisions" section as concrete answers (column types, constraint forms, exact CHECK expressions). The build session implements without re-deciding.

- **Tier 3 — name as deferred forward-pointer.** A decision that genuinely belongs to a later session, where naming it explicitly prevents disappearance. Examples: a remapping formula deferred to Phase 6 (with a schema comment naming the deferral), a column reservation deferred to a future ADR, a coordination note for the next health check. Tier 3 entries land in the report.

The triage is judgment-bound, not algorithmic. A finding that the gate session classifies as Tier 2 may, on user review, escalate to Tier 1 or de-escalate to Tier 3. The gate session's first triage is a draft; user review is the load-bearing pass.

### 4. Resolve Tier 1 findings with the user

The gate session is conversational by default. For each Tier 1 finding:

1. State the finding with its citations and why it matters now.
2. Present resolution options with tradeoffs.
3. Use AskUserQuestion or direct conversation to settle.
4. Author the resolution artifact: ADR amendment, sibling vocabulary doc, ADR sub-decision update, or a new ADR if the resolution warrants one.

The gate session does not push past unresolved Tier 1. If a Tier 1 finding requires multi-conversation reasoning, surface "this needs more conversation than this session can hold" — escalating per [`escalation-criteria.md`](../../../engine/operations/escalation-criteria.md).

The user-directed posture is what distinguishes gate sessions from build sessions. Build sessions running in auto-mode push through routine judgment calls; gate sessions surface them. The mode-switch is structural: a gate session that finds itself wanting to push through a Tier 1 has misidentified its mode.

### 5. Author resolution artifacts

Tier 1 resolutions produce concrete artifacts the build session will reference:

- ADR amendments (recorded in ENGINE_LOG per the existing amendment-asymmetry pattern).
- New ADRs when the resolution warrants one (per [`adr-authoring.md`](../../../engine/operations/adr-authoring.md)).
- Sibling Layer 1 documents (e.g., a TENSION_VOCABULARY.md authored alongside the schema migration that consumes it).
- Pattern instantiation rows in [`expression-contract-instantiation.md`](../../../engine/operations/expression-contract-instantiation.md) when the gate opens a new authoring pattern.

Tier 2 decisions live in the build-readiness report directly; they do not produce separate artifacts. Tier 3 forward-pointers also live in the report.

### 6. Write the build-readiness report

Path: `engine/build_readiness/<phase>_<chunk>.md` where `<phase>` matches the build_plan/ chunk's phase identifier (e.g., `phase_3`, `phase_4`, `phase_5_seed_geometry`) and `<chunk>` names the specific work (e.g., `sql`, `graph_validation`, `seed_geometry_part_1`). Multi-chunk phases get one file per chunk; single-chunk phases use the phase name alone (`phase_3_sql.md`).

The report's structure follows the template in [`build-readiness-gate.md`](../../../engine/operations/build-readiness-gate.md) — Pre-session decisions, Tier 2 decisions, Tier 3 forward pointers, Success criteria, Authored resolution artifacts, See also.

### 7. Source-document citation pass (gate-on-the-gate)

Per [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md) gate-on-the-gate amendment. Before the report is declared complete, every Tier 1 and Tier 2 decision in the report must explicitly cite the source-document line(s) that ground the decision. Citation form: `<doc-path>:L<line>` or `<doc-path>:L<start>-<end>` for ranges, or `<ADR-id>:L<line>` for ADR citations.

If a decision is grounded in multiple source documents, cite both. If a decision is grounded in conversational consensus from this gate session rather than a source document, write `decided in S-<NNNN> conversation` — but flag in Tier 1's resolution prose so the cold-review pass below knows it has no document to verify against.

The citation discipline serves the cold-review pass; without citations cold-review has no grounding to verify against and falls back to authorial trust (which is what the gate exists to avoid).

### 8. Cold-review pass against citations (gate-on-the-gate)

Launch a sub-agent (Explore type) with no session context. Brief: "Read this build-readiness report. For each Tier 1 and Tier 2 decision, fetch each cited source-document passage. Verify that the cited passage supports the decision claimed. Report per decision: matches | partial | discrepancy | citation-not-found | citation-misquoted, with the relevant excerpt for any non-match. Also flag any decision lacking a citation that names a fact-of-the-world rather than a conversational consensus."

The sub-agent has no memory of the gate session's authoring premises and so cannot share its blind spots. The mechanism targets the failure mode S-0028 surfaced (mid-build divergence between gate report and architecture.md authoritative design) — the citation-and-cold-review combination would have caught the divergence at gate close.

Findings block gate close until resolved. Resolution paths:

- **Match.** No action; the citation supports the decision.
- **Partial.** Either tighten the decision to what the citation supports, or add additional citations covering the rest.
- **Discrepancy.** Either the decision is wrong (amend it) or the source is wrong (amend the source — typically with the user).
- **Citation-not-found.** Update the citation (likely a stale line number after editing the source).
- **Citation-misquoted.** Rewrite the gate report's prose to match the source.

Findings are appended to the gate session's `outcome_summary` even after resolution — they are calibration data for refining the gate's adversarial-analysis stage.

### 9. Update STATE.md to point at the report

The "Next session work item" block in STATE.md gains a line: `Gated by [`engine/build_readiness/<phase>_<chunk>.md`](build_readiness/<phase>_<chunk>.md).` The build session reads the line at boot and follows it.

The gate session's `outcome_summary` records: report path, Tier 1 / Tier 2 / Tier 3 counts, citation-and-cold-review findings (matches and resolutions), any open follow-ups.

### 10. Close

Invoke the `session-shutdown-sequence` skill to run the close-of-session protocol. Gate sessions follow the standard shutdown like any session.

## Failure modes the gate prevents

A build session that begins with one or more Tier 1 decisions unresolved, improvises resolutions in the moment, and produces internally coherent artifacts that pass mechanical gates and survive cold review — because both layers check artifact-vs-contract alignment, not contract-vs-reality alignment. The compound-drift mode applies at the session level too: a contract authored under build pressure with a wrong premise has every layer compounding the wrong premise.

The gate compensates by inserting a halting checkpoint *before* the contract is authored, where the AI's premises can be challenged with fresh-context Explore agents and where the user can direct resolution before authoring begins.

## Failure modes the gate does NOT prevent

- Drift within an in-flight build session — the existing standing rules cover this.
- Errors in the build session's implementation against a clear contract — Layer 2 mechanical gates and Layer 3 cold-review cover this.
- Errors that surface only at runtime — detected by the next phase's audit, ADR 0022 health checks, or live testing.

The gate's specific job is the session-entry-time decision space.

## See also

- [`engine/operations/build-readiness-gate.md`](../../../engine/operations/build-readiness-gate.md) — Layer 1 source-of-truth prose with full template + worked example.
- [ADR 0040](../../../engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the citable contract this skill operationalizes.
- [ADR 0039](../../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md) — sibling structural ADR; the gate enforces "no row, no authoring" for new authoring patterns.
- [`engine/operations/session-build-lifecycle.md`](../../../engine/operations/session-build-lifecycle.md) — boot procedure; build sessions read the gate report at boot.
- [`engine/operations/escalation-criteria.md`](../../../engine/operations/escalation-criteria.md) — when sessions interrupt the user; gate sessions invert the default for routine decisions.
- [`engine/operations/expression-contract-instantiation.md`](../../../engine/operations/expression-contract-instantiation.md) — per-pattern instantiation table; gate sessions add rows for new patterns.
- [`engine/operations/adr-authoring.md`](../../../engine/operations/adr-authoring.md) — Nygard template; ADR amendments authored during gate sessions follow this.
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition this skill instantiates.
