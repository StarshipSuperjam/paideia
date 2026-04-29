# Cross-references

> High-value file dependencies. When changing a commitment or a downstream file, check the files that depend on it. This is not exhaustive — it captures connections where a change would silently break something.

The validator (`tools/validate.py`) checks that every `.md` link in this file resolves to an existing file. Keep paths accurate.

## Commitments → downstream files

Commitments live in [`docs/MISSION.md`](MISSION.md) (numbered list, audience framing) and [`ROADMAP.md`](../ROADMAP.md) (Strong working commitments referenced throughout). Each commitment is recorded as an ADR in [`adr/`](../adr/) (the contract); MISSION.md is the audience-facing summary.

- **Commitments 8 / 9** (node granularity, portable mastery) → [`adr/0008`](../adr/0008-concept-nodes-not-thinkers.md), [`adr/0009`](../adr/0009-portable-mastery.md), [`docs/architecture.md`](architecture.md) (Node Granularity Principle, Portable Mastery, Edge Schema, Node Schema), [`docs/pedagogy.md`](pedagogy.md) (assessment rubric assumes concept-level nodes).
- **Commitment 3** (media as metadata) → [`adr/0003`](../adr/0003-supplementary-media-as-metadata-not-structure.md), [`docs/expansion.md`](expansion.md), [`docs/architecture.md`](architecture.md) (graph traversal assumes no media edges).
- **Commitment 11** (no hosted copyrighted material) → [`adr/0011`](../adr/0011-no-hosted-copyrighted-material.md), [`docs/content-strategy.md`](content-strategy.md) (Copyright Model), [`docs/reading-system.md`](reading-system.md) (bring-your-own-book architecture).
- **Commitment 7** (cross-domain porosity) → [`adr/0007`](../adr/0007-cross-domain-porosity.md), [`docs/architecture.md`](architecture.md) (Cross-Domain Porosity), [`docs/MISSION.md`](MISSION.md) (cross-domain section is load-bearing).
- **Commitment 12** (audience defaults) → [`adr/0012`](../adr/0012-freshman-defaults-autodidact-ceiling.md), [`docs/business.md`](business.md) (Audience vs. Market), [`docs/pedagogy.md`](pedagogy.md) (V1 Calibration Defaults).

## Bidirectional sync requirements

Some pairs of files must stay synchronized — one defines a principle and the other operationalizes it.

- [`docs/pedagogy.md`](pedagogy.md) expression contract (three teaching modes) ↔ [`docs/session-lifecycle.md`](session-lifecycle.md) (mode transition signals). pedagogy.md states the principle; session-lifecycle.md operationalizes the triggers.
- [`docs/learner-model.md`](learner-model.md) engagement depth / scaffolding proximity ↔ [`docs/pedagogy.md`](pedagogy.md) (assessment rubric, mastery verification). Both define and consume the same evidentiary model.
- [`docs/business.md`](business.md) audience defaults ↔ [`docs/pedagogy.md`](pedagogy.md) (V1 Calibration Defaults). The audience decision drives the pedagogical starting posture.

## Shared capability consumers

Multiple files depend on the same shared service or schema component. Changes to the shared component require an audit of consumers.

- [`docs/architecture.md`](architecture.md) entity resolution service → [`docs/reading-system.md`](reading-system.md) (outline generation), [`docs/architecture.md`](architecture.md) (syllabus upload pipeline), [`docs/self-correction.md`](self-correction.md) (teaching session context). Three consumers of the same shared capability.
- [`docs/architecture.md`](architecture.md) rigor score computation → [`docs/learner-model.md`](learner-model.md) (mastery decay, mastery computation). The effective rigor score feeds decay rate, decay floor, and assessment calibration.
- [`docs/architecture.md`](architecture.md) node schema (`status`, `superseded_by`) → [`docs/learner-model.md`](learner-model.md) (event remapping on node splits). Deprecated nodes with learner events need successor pointers.

## Procedural dependencies (project machinery)

Operational artifacts that depend on each other. Changes propagate.

- [`STATE.md`](../STATE.md) (next-session work item) → consumed by `/start-engine` and [`docs/operations/session-build-lifecycle.md`](operations/session-build-lifecycle.md).
- [`session/register_state.json`](../session/register_state.json) → consumed by `/start-engine`, [`docs/operations/session-build-lifecycle.md`](operations/session-build-lifecycle.md), [`docs/operations/health-check.md`](operations/health-check.md) (cadence trigger).
- [`tools/validate.py`](../tools/validate.py) → run by `tools/hooks/pre-commit`; output interpretation in [`docs/operations/tools-validate-interpretation.md`](operations/tools-validate-interpretation.md).
- [`.claude/settings.json`](../.claude/settings.json) (lands in S-0002) → defines stop / precompact hooks per [`docs/operations/mempalace-operations.md`](operations/mempalace-operations.md).

## Phase-boundary checks

When a phase closes or opens, audit:

- **Phase 0 → Phase 1** *(verified at S-0003 close)* — every commitment in [`docs/MISSION.md`](MISSION.md) (1–12) has a corresponding ADR in [`adr/`](../adr/) with `Status: Accepted`. Every entry that was in `design-reasoning.md` became an ADR (0013 Mastery Verification, 0014 Sonnet/Opus, 0015 Event-Sourced Learner Model, 0017 Postgres over OWL/RDF, 0018 Flat Domain Tags, 0019 Two-Column Rigor Score, 0020 Teaching Notes Separation, 0021 Node Status + Superseded_by); the file retired in CHANGELOG. ADRs 0016 (Graph construction needs live validation) and 0022 (Periodic project health checks) emerged in the S-0001 plan conversation. Final tally: 22 ADRs, all Accepted; `tools/validate.py` `adr_status` check returns 0 soft-warns.
- **Phase 1 → Phase 2** — all open `OQ-DEC1-*` and `OQ-PHASE8-*` tensions in [`docs/tensions.md`](tensions.md) have an Accepted ADR or are explicitly tagged `deferred`.
- **Phase 4 → Phase 5** — `tools/validate.py`'s graph audit is live; `supabase/migrations/PREDICATE_MANIFEST.md` and `supabase/migrations/ROUTING.md` are populated.

## When to update this file

Add an entry when a new file is created that becomes load-bearing for an existing file, or when a file's relationship to others is non-obvious. Remove an entry when a file is retired or its dependency is severed by an architectural change.

The validator checks every `.md` link here resolves. If a target file is renamed, update this file in the same commit.
