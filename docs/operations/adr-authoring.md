# ADR authoring

> Architecture Decision Records: durable, structured, citable. The contract layer in two-layer decision recording (per CLAUDE.md). The story layer is MemPalace `decision`-tagged drawers.

ADRs live in `adr/`. The collection lands in S-0003. ADRs 0001-0022 absorb the 12 strong working commitments (`docs/MISSION.md` / `ROADMAP.md`) plus 10 architectural decisions from `design-reasoning.md` plus any new decisions made during S-0003 itself.

## Template (Nygard)

```markdown
# ADR NNNN — Decision title

- **Status:** Proposed | Accepted | Deprecated | Superseded by ADR NNNN
- **Date:** YYYY-MM-DD
- **Deciders:** <session ID(s) that settled this>

## Context

What's the situation calling for this decision? Constraints, forces, prior commitments that bear on the choice. ~1-3 paragraphs. Don't argue for the decision yet — just describe the terrain.

## Decision

What was chosen. State it plainly, in the present tense ("The graph uses Postgres with recursive CTEs, not OWL/RDF"). One paragraph.

## Consequences

What follows from this decision — both intended and incidental. Include downstream files this affects, future work it enables, and tradeoffs accepted. ~1-3 paragraphs.

If superseding a prior ADR, include a brief reference to what changed and why.

## See also

- Related ADRs.
- Source material (design-reasoning.md entries, tension.md resolutions, MemPalace drawer IDs if useful).
```

Filename pattern: `adr/NNNN-kebab-case-title.md` (e.g., `adr/0001-pedagogical-edges-not-historical.md`).

## Status conventions

Four states. The Status field is required (validate.py soft-warns if missing).

### `Proposed`

The decision is drafted but not yet committed-to. Used when an ADR lands ahead of the actual decision moment (rare). Most ADRs skip this state and start at `Accepted`.

### `Accepted`

The decision is in force. Downstream files and code may rely on it. The default state for a newly-authored ADR.

### `Deprecated`

The decision is no longer in force, and no replacement exists yet. The ADR remains in `adr/` so future sessions can read why it was abandoned. If a replacement exists, use `Superseded by ADR NNNN` instead.

### `Superseded by ADR NNNN`

The decision has been replaced by a newer ADR. The pointer is one-directional (the older ADR points at the newer; the newer doesn't need to point back). The older ADR remains in place — it carries the historical reasoning.

## When an ADR is warranted

Author an ADR when the decision satisfies *any* of:

- It propagates structurally to schema, file layout, or naming conventions.
- It commits to a tradeoff with significant alternatives that future sessions might want to revisit.
- It supersedes an earlier ADR.
- It resolves an open tension (`docs/tensions.md`) of architectural significance.

Don't ADR for:

- Editorial choices (wording, formatting, file ordering).
- Reversible local decisions with no downstream propagation.
- Decisions already covered by a settled ADR — those go in CHANGELOG entries and design-doc updates, not new ADRs.

## ADR vs CHANGELOG vs MemPalace

| Surface | What | Format | Reader |
|---|---|---|---|
| ADR | Settled architectural decision | Structured (Status / Context / Decision / Consequences) | Future sessions, expected to act on the contract |
| CHANGELOG | Material change | Categorized (Added / Changed / Removed / etc.) | Anyone scanning project history |
| MemPalace `decision` drawer | The conversation that produced the decision | Verbatim | Anyone running a similarity search; recovers the *story* |

A new ADR typically generates one CHANGELOG entry (under Added) and one or more MemPalace drawers (the verbatim conversation that produced it).

## See also

- [`mempalace-tagging-conventions.md`](mempalace-tagging-conventions.md) — `decision` drawer conventions.
- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — when ADR creation triggers CHANGELOG entries.
- `STATE.md` — current ADR scope (S-0003 lands ADRs 0001-0022).
- `ROADMAP.md` — phases that produce subsequent ADRs.
