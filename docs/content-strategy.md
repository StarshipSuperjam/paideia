# Content Strategy

## Philosophy Domain — Source Licensing

| Source | License | Commercial use? | Notes |
|--------|---------|-----------------|-------|
| Wikipedia | CC BY-SA | Yes, with attribution | Broad coverage, decent quality. Available in structured dumps. |
| Project Gutenberg | Public domain | Yes | Primary texts: Kant, Hume, Descartes, Plato, Aristotle, etc. Clean text. |
| Internet Archive | Public domain (older works) | Yes (for PD material) | Out-of-copyright secondary literature. Programmatic API access. |
| Stanford Encyclopedia of Philosophy | Non-commercial | Structural reference only — see below | Best quality. Used as a concept inventory and cross-reference source, not as teaching content. |

### SEP as Structural Reference, Not Content Source

SEP's value to Paideia is structural, not textual. It tells us *which concepts exist* and *what cross-references suggest about prerequisite relationships* — essentially a curated index of ideas. You cannot copyright a concept list. No SEP content is reproduced to the learner. Teaching content comes from Claude's trained knowledge, primary texts via Gutenberg, and whatever RAG corpus is built from licensable sources. This eliminates the SEP licensing dependency as a blocking concern: using SEP to decide that "Transcendental Idealism" should be a node and that it relates to "Synthetic A Priori" is research, not reproduction.

Because the graph is generatively seeded — AI produces concept nodes and prerequisite edges, validated through use — no licensed dataset is required for graph construction. SEP, IEP, and Oxford dictionaries are useful cross-reference checks, not dependencies. This means commercial use introduces no licensing constraint on the graph itself. Source licensing still matters for the RAG corpus (what the app teaches *from*), but the graph structure is proprietary from day one. See business.md under "Generative Graph Independence" for the competitive implications.

Source licensing will need to be evaluated per domain as new domains are added. The philosophy sources above are specific to the first domain.

## Graph Curation

Each node needs: prerequisite edges, reading/resource recommendations (primary + supplementary), and a key concepts list. AI generates first-pass edges and recommendations; the user validates and corrects through experience, and the self-correcting feedback loops (see architecture.md) reshape the graph over time. The bottleneck for scaling is cross-domain edge quality — connections between philosophy, psychology, history, etc. that no single reference work covers. Within-domain graph construction is a decomposition-and-linking problem, not a scholarship problem. The graph is the moat, and its value compounds with use.

## Corpus Pipeline (Designed)

- One-time ingest per domain. For philosophy: Wikipedia + Gutenberg + Internet Archive for public-domain secondary literature.
- Academic reference works (SEP, IEP, Oxford dictionaries) are structural cross-checks for graph construction, not corpus sources for the RAG pipeline. The graph does not depend on any licensed dataset.
- Chunk, embed, store in vector database.
- App retrieves relevant passages at query time via semantic search.
- Each new domain needs its own corpus sourcing strategy.

## User Text Ingestion Pipeline (Close Reading)

The close reading system (see reading-system.md) depends on a "bring your own book" model. The app never hosts, distributes, or embeds copyrighted material. All copyrighted text lives in user-scoped personal corpora — the user's own purchased material, stored for their own use.

### Acquisition Path

There is no "buy and it appears in the app" pipeline. Amazon does not expose Kindle content via API. DRM on commercial ebooks prevents legitimate extraction. Publisher partnership deals are a business development effort that makes no sense until the product has significant user volume. The realistic path: the user acquires a DRM-free EPUB, PDF, or plain text file through legitimate channels (purchase, library, publisher direct) and uploads it once. The app ingests it into their personal corpus.

This friction is appropriate. Close reading is an optional deep-dive mode, not the default learning experience. By the time a user uploads a text, they've been learning conversationally through the mastery graph, encountered a concept that warrants deeper engagement, received an AI recommendation for a specific text, and decided to invest in acquiring and reading it. Uploading a file is a trivially small step at that point.

### Storage Economics

A typical ebook is 500KB-2MB as raw text (stripped of formatting). Chunked into ~500-token segments, a book produces 200-400 chunks. Each chunk's embedding (1536 dimensions, 4 bytes each) adds ~6KB. Per book: roughly 1-4MB of raw text plus embeddings. Per user with 40 books: roughly 150MB total (text + embeddings). At Supabase pricing ($0.125/GB/month beyond included storage), 1,000 users with 40 books each (~150GB) costs about $19/month in overage. Storage is a rounding error relative to API compute costs.

### Connection to Commerce Layer

The AI's reading recommendation (see reading-system.md under "AI-Initiated Reading Recommendations") links directly to acquisition channels. Amazon Associates deep links favor the specific edition, translation, or commentary the AI recommended — not whatever Amazon ranks highest. This closes the loop: the AI recommends a text → the referral link helps the user acquire it → the user uploads it → close reading begins. The commerce layer serves the pedagogical pipeline, not the reverse.

## Commerce Layer: Amazon/Kindle Referrals

Reading lists generated by the mastery map and syllabus system deep-link to Amazon and Kindle editions via the Amazon Associates program. This serves two functions: it is a distribution mechanism for the content pipeline (closing the gap between "here's what to read" and "here's where to get it"), and it is the bridge between the mastery graph's reading recommendations and the close reading system's "bring your own book" requirement. Links should favor editions recommended in the graph metadata (specific translations, annotated editions, etc.) rather than defaulting to whatever Amazon ranks highest. Per-domain source licensing (above) governs what the app teaches *from*; the commerce layer governs where users *acquire* the texts.

## Reference Datasets as Node Sources

Existing academic reference works serve as curated idea inventories with cross-references already built in. Stanford Encyclopedia of Philosophy, Internet Encyclopedia of Philosophy, Oxford dictionaries of psychology, economics, and literary terms — each domain has encyclopedic and dictionary coverage that provides the raw node inventory.

**Decomposition step required.** Reference work entries are organized by thinker or broad topic (e.g., "Kant's Epistemology"), not at concept-level granularity. The ingestion pipeline must decompose each entry into the individual concepts it covers, following the node granularity principle (see architecture.md): an SEP entry on Kantian Epistemology becomes separate nodes for Analytic-Synthetic Distinction, Synthetic A Priori, Transcendental Idealism, Kantian Categories, and the Thing-in-Itself. Claude performs this decomposition and generates first-pass prerequisite edges. The user validates and corrects through experience.

This makes initial graph construction a decomposition-and-linking problem, not a scholarship problem. Cross-domain connections (where philosophy meets psychology meets literature) are the part no existing dataset covers — these emerge through the self-correcting feedback loops and the user's own intellectual work.

## Cross-Domain Reference Inventories — Survey

The Philosophy-Domain table above and the SEP/IEP/Oxford-dictionary commitments specifically cover *philosophy*. The settled posture in the section above ("Source licensing will need to be evaluated per domain as new domains are added") is the gap this section closes. A tiered survey runs in **ROADMAP Phase 4.5** (between Phase 4 validation utility and Phase 5 seed authoring) and lands its output here.

**The survey targets cross-reference inventories and prerequisite-shape priors, not corpus dependencies.** "Generative Graph Independence" (`business.md`) and "SEP as Structural Reference, Not Content Source" (above) remain in force — concept nodes and prerequisite edges are generatively seeded by Claude. The survey gives that generation pass better starting inventories per domain.

### Five usability axes

Every candidate dataset is evaluated against these. The Önduygu philo-browser case (worked example below) extracted them.

1. **Graph-shape orientation.** Prerequisite-shaped (per [ADR 0001](../adr/0001-pedagogical-edges-not-historical.md)) vs. influence / agreement / dialectical / citation / co-occurrence. Influence-shaped data drags the modeler dialectical even when intended only as vocabulary. Filter aggressively.
2. **License.** Three buckets:
   - **Ingestable** (CC0 / CC-BY / MIT / public domain) — usable as direct seed input or RAG corpus.
   - **Mineable for facts only** — bibliographic citations, topic taxonomies. Facts about works are not copyrightable; the prose summarizing them often is.
   - **Consultable only** (all-rights-reserved, scrape-restricted, non-commercial like SEP) — usable as structural cross-reference per the SEP precedent above; never reproduced.
3. **Form.** Structured graph data vs. structured taxonomy/tags vs. long-form prose. Long-form prose has low novel value — already parametrically accessible to Sonnet/Opus.
4. **Coverage breadth.** Single-domain vs. cross-domain native. Commitment 7 (cross-domain porosity per [ADR 0007](../adr/0007-cross-domain-porosity.md)) makes cross-domain-native sources disproportionately valuable.
5. **Depth uniformity / methodology transparency.** Sources that disclose their own uneven depth are higher-trust than sources that don't. Hidden unevenness produces silent depth holes in derived inventories.

### Tiered survey scope (not exhaustive)

Decision-quality return on surveying everything plateaus quickly past the prerequisite-shaped tier. Survey depth is proportional to graph-shape value.

- **Tier 1 — exhaustive on prerequisite-shaped graphs.** Small, load-bearing, novel value. Known candidates to evaluate: Khan Academy knowledge map (math-dense, pedagogical-prerequisite, license verification needed); ConceptNet's `Prerequisite` relation (CC BY-SA); university CS curriculum prerequisite graphs; Mathlib / Metamath dependency graphs (literally logical-prerequisite, math-only).
- **Tier 2 — comprehensive on per-domain cross-reference inventories outside philosophy.** For each non-philosophy domain in `docs/expansion.md` (history, theology, literature, economics, poetry, political theory, law, psychology), identify the SEP/Oxford-dictionary equivalent and run the license check.
- **Tier 3 — representative sample on bibliographies and citation graphs.** Önduygu's reference page (~800 works, ~400+ authors), Open Syllabus Project, Semantic Scholar / OpenAlex. Reading-list and co-occurrence priors, not content.
- **Tier 4 — minimal on long-form prose references already parametrically accessible.** SEP, IEP, Wikipedia. Note as *consult-during-validation*, not as survey targets.

### Önduygu philo-browser — worked example

Deniz Cem Önduygu's `denizcemonduygu.com/philo` (Western philosophy graph: ~800 works, ~400+ authors, propositions linked by green/red agree-or-disagree edges, twelve-year autodidact project, all-rights-reserved, no API) is the worked example that surfaced the axes.

- **Propositions+edges layer:** graph-shape-incompatible (dialectical, not prerequisite). **Consciously not consulted during seed authoring** — the contamination risk in axis 1 applies precisely to this layer.
- **Tag layer (named -isms, theses, paradoxes):** usable as a concept-vocabulary checklist during Phase 5 Western-philosophy authoring. Mineable-for-facts (axis 2) — names of named ideas are facts about the field.
- **Reference list (~800 works):** usable as a starting reading list. Bibliographic facts are clean territory under the all-rights-reserved shield.
- **Author's own caveat** — "Browsing this visual summary cannot substitute reading a good book of history of philosophy, let alone studying the original texts" — is rhetorical prior art for [ADR 0011](../adr/0011-no-hosted-copyrighted-material.md) and the BYO-book commitment. A Dennett-endorsed twelve-year project explicitly disclaiming the pedagogical role is citable evidence the visual-summary approach has known limits — Paideia is positioned in the gap.
- **Calibration evidence:** twelve disciplined autodidact years produced ~800 works at uneven depth. Phase 5 throughput projections should be set against this prior, not against optimistic LLM-augmentation-as-multiplier assumptions.

### Per-candidate assessment template

Candidate datasets are recorded using this template:

```
**<Dataset name>** ([URL])
- Tier: 1 / 2 / 3 / 4
- Graph-shape: prerequisite | influence | agreement | citation | co-occurrence | none
- License: ingestable | mineable-for-facts | consultable-only — [specific terms]
- Form: structured-graph | tag-taxonomy | long-form-prose | bibliography
- Coverage: <domain(s) covered>; cross-domain native? Y/N
- Depth disclosure: explicit | implicit | absent
- Verdict: usable as <use> in <phase> | excluded for <reason>
- Authoring contact / scrape policy: <if relevant>
```

The template anchors the survey to a comparable shape across candidates. It is not a contract — categories may extend if a candidate surfaces a relevant axis the five didn't anticipate, recorded explicitly.

## User Library as Optional Signal Layer

Users can optionally input their existing library or reading history. This sets "exposed" status on relevant concept nodes (see architecture.md for mastery states) and enables gap detection: books the user doesn't own that would unlock or connect graph paths. It also enables source-preference routing — when the system needs to teach a concept, it can prioritize sources the user already has access to. The library input is a convenience feature, not a requirement. The graph carries its own source recommendations per node and assumes nothing about what any user owns. Owning or having read a book is never equivalent to mastery — the user must still engage meaningfully with the ideas to demonstrate understanding.

## Copyright Model

The product has two distinct copyright profiles, corresponding to its two teaching surfaces.

**Mastery graph (parametric teaching).** No copyrighted material in context. The AI teaches concepts conversationally from trained knowledge. No text is quoted, displayed, or retrieved from copyrighted sources during teaching interactions. The RAG corpus (when built) draws from public domain and openly licensed sources. The graph structure itself — concept nodes, prerequisite edges, metadata — is proprietary and generatively seeded with no dependency on any licensed dataset.

**Close reading (user-supplied text).** All copyrighted material is supplied by the user from their own purchased copies. The app stores it in a user-scoped personal corpus. The app never distributes copyrighted content between users, never hosts it for public access, and never pre-generates outlines from copyrighted commentary for distribution. Outlines generated from a user's uploaded commentary exist only in that user's scope. The app provides the teaching infrastructure (outline generation prompts, expression contract, session management, learner model) — the copyrighted inputs come from the user.

This separation is clean across every domain. Philosophy, literature, history, psychology — the mastery graph teaches parametrically without copyright dependency in all of them. Close reading requires user-supplied text in all of them. No domain introduces a structural copyright constraint that the architecture doesn't already handle.

## AI-Generated Content Policy

- Film/art/music connections: let Claude generate with reasoning, not bare assertions. Frame as "argued proposals" the user can verify or revise.
- The user cannot pre-populate connections they haven't verified — that defeats the learning purpose.
- Low-stakes recommendations ("after reading Sartre, you might watch La Strada") are acceptable even if imperfect.
- For new domains, Claude can propose graph structures as starting points for expert review.
