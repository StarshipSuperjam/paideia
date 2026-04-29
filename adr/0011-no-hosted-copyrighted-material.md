# ADR 0011 — No hosted or distributed copyrighted material

- **Status:** Accepted
- **Date:** 2026-04-08
- **Deciders:** pre-foundation deliberation; formalized in S-0003

## Context

Two architectures are available for the close-reading surface. **Hosted-text**: Paideia licenses or hosts copyrighted texts directly, serving them to learners through the app. **Bring-your-own-book** (BYOB): learners supply their own copies of texts (purchased, library-borrowed, openly-licensed); Paideia provides the interpretive scaffolding (outline generation per ADR 0005, teaching against the text) without ever distributing the text itself.

The hosted-text model creates three coupled problems. (1) **Licensing dependency that scales with every domain** — each new field would require separate publisher negotiations before launch. The graph teaches philosophy today; tomorrow it teaches chemistry; tomorrow it teaches music theory. Each adds publisher relationships. (2) **Copyright profile coupling** — the mastery graph's copyright profile becomes dependent on the close-reading system's copyright profile. Two surfaces that should be independent become entangled. (3) **No appropriate user friction** — the bring-your-own model creates a useful filter: by the time someone uploads a text, they've been learning conversationally, encountered a concept that warrants deeper engagement, received an AI recommendation, and decided to invest. That friction selects for genuine interest.

## Decision

The app **never hosts or distributes copyrighted material**. The mastery graph teaches parametrically (the AI's parametric knowledge of the scholarly tradition; node `summary` and `teaching_notes` carry zero copyrighted text). The close-reading system uses the bring-your-own-book model: learners supply their copies, Paideia provides outlines and teaching against the text without storing or transmitting the text content.

## Consequences

- The mastery graph teaches parametrically with **zero copyright exposure in every domain, forever**, regardless of what happens with close reading. This independence is load-bearing.
- The close-reading pipeline is structured to keep text content learner-side: outline generation can be parametric (no text needed) or per-text (text supplied at runtime, processed in-session, not persisted on Paideia servers beyond what the learner explicitly stores).
- New domains add no licensing prerequisites. Each domain requires graph authoring (Phase 5) and pedagogical calibration; neither requires a publisher relationship.
- Outline quality varies with how well the AI's parametric knowledge covers the text (per ADR 0005). Canonical texts get strong outlines; obscure texts get weaker ones. This is acceptable because BYOB concentrates uploads on texts with deep scholarly traditions.
- The friction of acquiring a text *is the point*. Learners who upload a text have already committed to engagement; the system doesn't waste teaching energy on uncommitted browsing.
- This commitment binds future product decisions. Any feature that would require Paideia to host copyrighted text needs a Status: Superseded change to this ADR plus a corresponding licensing strategy.

## See also

- [`docs/MISSION.md`](../docs/MISSION.md) — strong working commitment 11.
- [`docs/content-strategy.md`](../docs/content-strategy.md) — Copyright Model.
- [`docs/reading-system.md`](../docs/reading-system.md) — bring-your-own-book architecture.
- ADR 0005 — Per-text interpretive outline (parametric generation; user-supplied text optional).
- ADR 0002 — Commercial sustainability without pedagogical compromise (related independence: pedagogy decoupled from commercial dependencies).
