# ADR 0005 — Each text gets its own interpretive outline

- **Status:** Accepted
- **Date:** 2026-04-08
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

The reading-system component of Paideia takes a learner-uploaded text (per ADR 0011's bring-your-own-book model) and provides an interpretive outline to scaffold close reading. Two approaches are available: **template-based** (canonical sections — Introduction, Themes, Key Passages, Connections — applied to every text) or **per-text generated** (each text gets a custom outline derived from parametric knowledge of the scholarly tradition around that text, optionally enhanced by user-supplied commentary).

Templates are simpler and faster to render. They also produce outlines that don't actually fit most texts — Plato's *Phaedrus* and Wittgenstein's *Tractatus* require materially different scaffolding, and a one-size template does both poorly. The per-text approach exploits the fact that the AI has parametric knowledge of canonical interpretive moves for major texts (the *Symposium*'s ladder of love, the *Tractatus*'s ladder-to-be-thrown-away).

## Decision

Each text gets its own interpretive outline, **generated from parametric knowledge of the scholarly tradition for that text**, optionally enhanced by user-supplied commentary (annotations, alternative readings). No standardized templates. Domain-specific reading profiles (philosophy, literature, history, psychology) shape the *kind* of outline produced but do not template the structure.

## Consequences

- Outline generation is an LLM task at upload time. The reading-system pipeline: acquire text → resolve identity → generate outline (parametric, optionally enhanced) → present to learner.
- Different texts get materially different outlines. *Being and Time* gets a structure-of-Dasein outline; the *Republic* gets a tripartite-soul-and-city outline. Neither maps to the other's shape.
- User-supplied commentary is **enhancement, not replacement**. The default is parametric; user input adjusts. This keeps the cold-start UX functional (the learner doesn't have to provide commentary to use the system) while respecting that learners with prior expertise can shape the outline.
- The outline contract specifies that entries can carry teaching-mode hints (per `docs/reading-system.md`) — a dialectical text needs different teaching moves than an expository one. The outline becomes a richer scaffold than just section headings.
- Per-text generation costs LLM calls at upload time. This cost is bounded (one outline per text per user) and amortizes across reading sessions.
- Quality varies with the AI's parametric coverage. Canonical texts get strong outlines; obscure texts get weaker ones. This is acceptable because the bring-your-own-book model concentrates uploads on texts with deep scholarly traditions.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 5.
- [`docs/reading-system.md`](../docs/reading-system.md) — outline generation pipeline, domain profiles.
- [`docs/content-strategy.md`](../docs/content-strategy.md) — bring-your-own-book model.
- ADR 0011 — No hosted copyrighted material (the close-reading surface depends on user-supplied texts).
- `docs/tensions.md` — outline rigidity tension (resolved by per-text generation + user enhancement).
