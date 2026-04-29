# Mission

> What Paideia is, who it serves, and the commitments that make it different. Vision and audience framing extracted from CONTEXT.md (now retired) at S-0002.

## What this is

Paideia is a knowledge mastery app built on a **pedagogical dependency graph** — not a historical influence map. The key insight: "you need Kant's epistemology before phenomenology" is a different claim than "Kant influenced Husserl." The graph encodes what you must understand before something else makes sense, not just what influenced what.

Users select a target topic. The system traverses prerequisites, topologically sorts them, and generates a reading syllabus (primary + supplementary) for each step. A persistent learner model tracks mastery across sessions and texts.

## Cross-domain porosity (load-bearing)

Philosophy has the densest coverage first, but the graph is **inherently multi-domain from day one**. Philosophical concepts have prerequisite dependencies on history, psychology, economics, theology, logic, and the natural sciences. These cross-domain nodes are first-class graph elements, not future expansion. The architecture is domain-agnostic — the same graph structure, teaching system, and learner model serve any field where prerequisite relationships matter.

No domain can claim complete coverage without nodes from neighboring domains. Service nodes from other domains carry exactly enough depth to make the target concept comprehensible. Prerequisite chains terminate when further depth stops affecting comprehension of the target concept.

## Audience framing

### Freshman defaults, autodidact ceiling

The system calibrates **cold-start defaults for a learner encountering ideas for the first time**. The adaptive teaching system escalates rapidly based on engagement quality. Both audiences are served by the same product without either knowing the other exists.

The asymmetry of failure is directional: a freshman encountering content beyond their scope cannot proceed (and the failure feels like inadequacy, which is destructive). An autodidact encountering freshman-level calibration is mildly annoyed for a few exchanges before the adaptive system escalates. The cost of defaulting too low is brief annoyance; the cost of defaulting too high is a learner who quits.

### Audience vs. market

- **Audience** (shapes pedagogical defaults): community college students, particularly first-generation learners encountering academic philosophy without institutional scaffolding.
- **Market** (shapes eventual enterprise features): community college departments and similar institutional buyers. Deferred — schema provisions exist (nullable `cohort_id` on events, shareable constrained paths) so the institutional path remains open without building the enterprise wrapper now.

V1 priority is the teaching system, not the institutional wrapper. LMS integration, instructor dashboards, FERPA compliance, and grade export are bolt-on features deferred until the teaching system proves itself.

## Strong working commitments

These are the strongest current ideas — not closed questions, but the positions that would require substantial new thinking to displace. The full set lives in `ROADMAP.md` ("Strong working commitments referenced throughout"). Each becomes an ADR in S-0003.

1. **Pedagogical edges, not historical.** The graph encodes "must understand X before Y" — never just "X influenced Y."
2. **Commercial sustainability without pedagogical compromise.** Revenue logic must never change what the product teaches or how it teaches.
3. **Supplementary media is metadata, not structure.** Film, art, music attach to concept nodes as companions; never structural prerequisites.
4. **The learner model is relational.** Tracks connections between concepts and forward-looking teaching opportunities, not a flat checklist.
5. **Each text gets its own interpretive outline.** No templates. Generated from parametric knowledge of the scholarly tradition, optionally enhanced by user-supplied commentary.
6. **Domain-agnostic architecture.** Philosophy is the first domain, not the only one.
7. **All domains are mutually porous.** Cross-domain prerequisite edges are first-class graph elements.
8. **Nodes are concepts, not thinkers.** The atomic unit is an idea, never a person or school.
9. **Mastery is portable.** One mastery state per concept, regardless of path.
10. **Assessment is continuous and contextual.** Three-dimensional rubric (reconstruction, application, boundary awareness), discounted by scaffolding proximity, scaled by rigor score.
11. **The app never hosts or distributes copyrighted material.** Mastery graph teaches parametrically; close reading uses bring-your-own-book.
12. **Freshman defaults, autodidact ceiling.** Cold-start defaults; adaptive escalation.

The reasoning behind each lives in `design-reasoning.md` (transitional; absorbed into ADRs in S-0003).

## What's settled, what's open

`STATE.md` — current phase and next session's work item.
`ROADMAP.md` — full phase arc with success criteria.
`docs/tensions.md` — active tradeoffs and unresolved questions.
`docs/CROSS_REFERENCES.md` — high-value file dependencies.

## See also

- `README.md` — repo orientation.
- `CLAUDE.md` — AI session conventions.
- `docs/architecture.md` — graph data model.
- `docs/pedagogy.md` — teaching design and assessment.
- `docs/learner-model.md` — mastery, decay, events.
