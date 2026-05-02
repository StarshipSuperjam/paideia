# Expansion

## Supplementary Media Layer

Film, art, and music attach as metadata on concept nodes. They never create structural graph dependencies.

### Film
- Strongest mappings in philosophy domain. Tarkovsky ↔ Eastern Orthodox theology + phenomenology. Bergman ↔ existentialism. Godard ↔ Bazin + Sartre.
- Films that *are* philosophical arguments slot naturally into the graph.
- Most film connections run the opposite direction from text prerequisites — film illuminates ideas already encountered, rather than being required before text.

### Music
- Tightest documented mappings in philosophy. German Romanticism ↔ Wagner. Nietzsche ↔ music broadly. Schopenhauer's metaphysics of music. 20th century serialism ↔ specific philosophical movements.
- AI instruction skews toward context and meaning rather than perceptual listening guidance.

### Art
- Well-established connections: Impressionism ↔ phenomenology, Surrealism ↔ Freud, Renaissance painting ↔ Neoplatonism.
- Risk: loose thematic association that sounds plausible but isn't pedagogically real.

### Generation Strategy
*(Added: 2026-04-07)*

The user cannot self-populate supplementary media connections — doing so requires already knowing what the system is trying to teach. Three generation methods work around this: (1) mining university film/music/art history syllabi, which contain argued connections rather than bare assertions; (2) inverting the query — per concept node, ask what works are commonly cited in relation to it, rather than asking abstractly which works belong in the graph; (3) flagging all generated connections as unverified until the user has experienced the work and confirmed the relationship holds. The low-stakes nature of supplementary connections (no prerequisite edges, no structural consequences) makes imperfect generation acceptable — a weak suggestion is simply skipped or revised.

### Open Design Question

Whether to distinguish works that *participated in* a philosophical conversation from works that merely *rhyme thematically*. Worth encoding but adds complexity.

### AI Instruction Quality

Claude can discuss intellectual context well across all three media. Limitation: instruction skews toward *context and meaning* rather than *how to experience the work*. This may be exactly right for an intellectual mastery tool — the user brings aesthetic experience themselves.

## New Knowledge Domains

### Organizing Principle: Liberal Education
**Added: 2026-04-07**

The product identity is an AI-guided liberal education through source and supplemental text analysis and discussion. This frames which domains belong and which don't. Philosophy is the core. History, poetry, literature, economics, theology, political theory — yes. These are fields where reading primary sources in the right order, with interpretive guidance, constitutes genuine education. Vocational or technical domains (SQL, project management, etc.) don't fit — not because they lack prerequisite structure, but because they lack the textual tradition that the teaching method is built around.

Mathematics and science enter the graph only insofar as their concepts are prerequisites for adjacent domains (e.g., formal logic for analytic philosophy, Newtonian mechanics for Kant's metaphysics of nature, calculus for philosophy of science). Mastery of these concepts in Paideia means understanding their history, function, and place in the larger arena of human knowledge — not operational proficiency with their tools and techniques. Using mathematics to prove a theorem is application; understanding why the model was invented and what it changes about how we think is liberal education. The graph node for "calculus" here looks nothing like it would in a math tutoring app.

This principle also explains why the domains cohere as a product rather than being arbitrary expansion. A user who finishes a philosophy path and enters a history or economics path is continuing a single kind of education, not switching to a different app.

The architecture is domain-agnostic. Philosophy is the first domain and proving ground. Future domains include history, theology, literature, economics, poetry, political theory, and law — fields where reading primary sources in the right order, with interpretive guidance, constitutes genuine education. Mathematics and science appear as service nodes for these domains, not as standalone mastery tracks.

Each new domain requires: its own curated graph, its own corpus sourcing strategy, and potentially its own supplementary media connections. The teaching system (expression contract, learner model, outline method) transfers without modification.

Cross-domain edges are a future possibility — philosophy nodes connecting to theology, mathematics to physics, etc. This is architecturally straightforward but editorially complex.

## Age-Aware Paths

### Sequencing

1. **Community college** — first. Defines the graph, corpus, and teaching style for the philosophy domain.
2. **High school** — same domains, adjusted entry points. Literature and narrative as on-ramps (e.g., ethics through *To Kill a Mockingbird* before Kant).
3. **Younger learners** — distinct phase. Abstract philosophical reasoning doesn't develop until mid-adolescence. Needs stories, concrete moral scenarios, more Socratic dialogue, less formal argument. Closer to a parallel product sharing backend infrastructure.

### Family Vision

A shared intellectual map where the owner and his sons move through at different depths, where their questions occasionally meet. The supplementary media layer becomes primary for young learners — a child who watches *The Seventh Seal* has an intuitive grip on mortality that makes Camus more accessible later.

The app becomes infrastructure for a certain kind of family intellectual life.

---
*Last updated: 2026-04-07 (liberal education principle sharpened: math/science as service nodes, mastery = understanding not application)*
