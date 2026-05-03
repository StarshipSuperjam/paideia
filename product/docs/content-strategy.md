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

The structural-reference posture established here for SEP extends to a class of curated philosophy reference works (Routledge Encyclopedia of Philosophy, Oxford Reference philosophy collection, Internet Encyclopedia of Philosophy, Wikipedia) — see [ADR 0046](../adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md). The graph-shape value of these works (cross-reference adjacency network and concept inventory) is distinct from their content value (entry prose); the graph-shape vector survives the no-hosted-copyrighted-material commitment per [ADR 0011](../adr/0011-no-hosted-copyrighted-material.md) because concept-list and adjacency facts are uncopyrightable per Feist. Per-candidate evaluation lives in the "Cross-Domain Reference Inventories — Survey" section below.

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
- **Tier 4 — focused on well-known structural references for the home discipline.** SEP, IEP, Routledge Encyclopedia of Philosophy, Oxford Reference (philosophy), Wikipedia. Tier 4 is "well-known" (the survey does not need to discover them) but not "low-value" — the earlier "minimal on long-form prose already parametrically accessible" framing conflated two value vectors. The *content/prose value* — what an entry says — is already in Sonnet/Opus's training data and adds no novel survey value. The *graph-shape value* (cross-reference adjacency network, concept-inventory curation, presupposition signals) does **not** survive model training: Sonnet/Opus can recall facts from SEP entries but cannot enumerate SEP's cross-reference adjacency matrix. Graph-shape value is exactly the structural prior Phase 5 seed authoring for the home discipline (philosophy) consumes. Per [ADR 0046](../adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) the distinction is settled at the contract layer; the survey records each Tier 4 source's graph-shape disposition separately from its content disposition and surfaces the access-warrant tradeoff for sources requiring acquisition.

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

### Tier 1 candidates — exhaustive

The five known prerequisite-shaped graph candidates. Tier 1 verdicts directly inform Phase 5 service-node sub-session source choices (logic primitives, mathematical prerequisites — `005N` per [ROUTING.md](../seed-graph/migrations/ROUTING.md)).

**Khan Academy knowledge map** ([khanacademy.org](https://www.khanacademy.org/), [creativecommons.org/licenses/by-nc-sa/3.0/us](https://creativecommons.org/licenses/by-nc-sa/3.0/us/))
- Tier: 1
- Graph-shape: prerequisite (math-dense; sparse outside math/sciences)
- License: consultable-only — Khan Academy content is published under CC BY-NC-SA 3.0 US. Share and adapt are permitted with attribution and same-license, but `NC` (non-commercial) cuts against any future App Store deployment if a derived structure is materially traceable to Khan content. The structural extraction (concept-list + adjacency facts) is closer to Feist-territory facts than to copyrightable expression — but Phase 5 should treat the concept-list as inspiration, not as adoptable structure.
- Form: structured-graph (historically); the public knowledge-map UI was retired around 2014–2015 and the structured prerequisite data is no longer exposed via a public surface — current Khan offerings (Khanmigo, course pages) expose topic taxonomies but not the original prerequisite adjacency
- Coverage: math (dense), sciences (moderate), economics / humanities (sparse); single-domain dominant
- Depth disclosure: implicit — strongest in K–12 math, falls off sharply in college topics and outside STEM
- Verdict: **Excluded** for Phase 5 philosophy seed authoring (out-of-domain coverage). Reserve for Phase 5 service-nodes sub-session (`005N`) for math-prerequisite scaffolding only, and even then as a vocabulary checklist rather than as adoptable structure (the original adjacency dataset is not publicly accessible).

**ConceptNet — `/r/HasPrerequisite` relation** ([conceptnet.io](https://conceptnet.io/), [github.com/commonsense/conceptnet5/wiki/Copying-and-sharing-ConceptNet](https://github.com/commonsense/conceptnet5/wiki/Copying-and-sharing-ConceptNet))
- Tier: 1
- Graph-shape: prerequisite (the relation exists by name, but the relation's coverage is heavily common-sense / everyday — "you need flour to bake bread" — not academic prerequisites)
- License: ingestable — Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0); attribution required, share-alike required, no further restrictions ("You may not add restrictions such as 'non-commercial' or 'research use only'")
- Form: structured-graph (RDF triples / JSON-LD; bulk download published)
- Coverage: cross-domain native, but coverage is breadth-over-depth; the `HasPrerequisite` relation is sparse for academic philosophy concepts
- Depth disclosure: explicit — ConceptNet documents its sources and the per-source weight contribution
- Verdict: **Tagged for Phase 5 consultation** as a concept-vocabulary checklist for service-nodes (`005N`) and cross-domain edges (`006N`). The `HasPrerequisite` relation itself is too sparse and too common-sense-shaped to seed pedagogical-prerequisite edges directly; it is consulted as a sanity-check for proposed prerequisite edges that touch everyday concepts (e.g., "Does ConceptNet agree that `arithmetic` is a prerequisite of `algebra`?"), not as a primary inventory.

**University CS curriculum prerequisite graphs**
- Tier: 1
- Graph-shape: prerequisite (course-level, not concept-level — adjacency is between course numbers, not between the underlying concepts)
- License: variable — most institutions publish course catalogs under institution copyright; pedagogical-prerequisite *facts* (Course X requires Course Y) are uncopyrightable per Feist
- Form: bibliography / structured-table (course catalogs); a small number of institutions expose prerequisite graphs as JSON or D3 visualizations (e.g., MIT OCW course dependency diagrams, University of Washington / Berkeley CS prerequisite trees published as student-facing tools)
- Coverage: single-domain (CS-only); even within CS, granularity mismatch with Paideia's concept-level graph
- Depth disclosure: absent — depth is an institutional artifact (which courses the institution offers), not a methodological disclosure
- Verdict: **Excluded** for Phase 5 (granularity mismatch — Paideia's nodes are concepts, not courses; cf. [ADR 0008](../adr/0008-concept-nodes-not-thinkers.md) "Nodes are concepts, not thinkers"). Course-prerequisite graphs do not transfer because a single CS course bundles many concepts. Re-evaluate only if Phase 5 expands into a vocational domain where course-level granularity *is* concept-level.

**Mathlib (Lean 4 mathematical library)** ([leanprover-community.github.io/mathlib_stats.html](https://leanprover-community.github.io/mathlib_stats.html), [github.com/leanprover-community/mathlib4/blob/master/LICENSE](https://github.com/leanprover-community/mathlib4/blob/master/LICENSE))
- Tier: 1
- Graph-shape: prerequisite (literally logical — every `theorem` carries its full proof-dependency chain; the dependency graph is exact, not interpretive)
- License: ingestable — Apache License 2.0
- Form: structured-graph (the source files are Lean 4; the project publishes a dependency-graph visualization plus tooling to extract structural data)
- Coverage: single-domain (mathematics); 130,141 definitions, 272,470 theorems, 772 contributors per the project's own statistics page; covers natural numbers, linear algebra, sets, topology, category theory and growing into undergraduate maths broadly ("1000+ theorems" milestone documented)
- Depth disclosure: explicit — Mathlib's coverage roadmap and per-area maturity are documented in community channels
- Verdict: **Tagged for Phase 5 consultation** for the service-nodes sub-session (`005N`) when authoring mathematical prerequisite scaffolding. Use for: cross-checking that mathematical-prerequisite chains assembled by generative authoring are logically sound (if Mathlib derives concept B from concept A, an asserted prerequisite A→B is sound; an asserted A↛B contradicts a known logical dependency). Not adopted as the seed structure — Mathlib's granularity is finer than Paideia's pedagogical concepts, and the mathematics it covers exceeds what philosophy service-nodes need.

**Metamath set.mm (Metamath Proof Explorer)** ([us.metamath.org](https://us.metamath.org/index.html), [github.com/metamath/set.mm](https://github.com/metamath/set.mm))
- Tier: 1
- Graph-shape: prerequisite (literally axiom-prerequisite; every theorem chains back to the ZFC axioms and definitions)
- License: ingestable — set.mm and the Metamath ecosystem are released into the public domain (CC0); see the project's `LICENSE.TXT` in the source repository for the verbatim statement
- Form: structured-graph (`.mm` plaintext files; the proof structure is parseable directly with `metamath-exe`, `mmj2`, and community tools that emit dependency graphs)
- Coverage: single-domain (formal mathematics — ZFC set theory primary; intuitionistic logic, NF set theory, higher-order / type theory, quantum logic in companion `.mm` files); over 23,000 proven theorems in the Metamath Proof Explorer database alone
- Depth disclosure: explicit — Metamath's own documentation describes the system as appealing to formal-verification interest more than working-mathematician practice ("Professional mathematicians may view it as a curiosity more than a tool")
- Verdict: **Excluded** for Phase 5 philosophy seed authoring (the granularity mismatch is severe — a single pedagogical concept like "Modus Ponens" maps to thousands of Metamath proof steps; the formal-verification depth offers no signal at the pedagogical layer Mathlib does not already provide more accessibly). Note as a structural reference for the rare case a Phase 5 service-node touches formal-logic foundations (`005N`) where a sanity-check on which axioms underlie a concept is informative.

### Tier 2 candidates — comprehensive per non-philosophy domain

For each non-philosophy domain in [`expansion.md`](expansion.md) (history, theology, literature, economics, poetry, political theory, law) plus psychology (consulted as a cross-domain anchor per the existing scaffold's enumeration), the most plausible cross-reference inventory candidate is named with license posture and graph-shape disposition. These are *recommendations for future per-domain Phase 5 sub-sessions* — Phase 5 epistemology proceeds without them. Adoption decisions for any non-philosophy domain land as ADRs in the consuming session per the chunk-file scope discipline.

**History — Cambridge Histories series + Oxford Bibliographies (History)**
- Cambridge Histories ([cambridge.org/core/series/cambridge-histories](https://www.cambridge.org/core/series/cambridge-histories)) — peer-reviewed multi-volume historical surveys; publisher-paywalled prose; entry-level table-of-contents and chapter titles are public and constitute a clean concept-inventory source
- Oxford Bibliographies in History ([oxfordbibliographies.com](https://www.oxfordbibliographies.com/)) — annotated subject-bibliography series; subscription/institutional access; provides cross-reference structure between historiographic concepts and primary sources
- License: consultable-only (paywalled prose); structural extraction (entry titles, cross-reference adjacency) is fact-shaped per Feist
- Form: long-form prose with structured TOCs / annotated bibliography
- Coverage: history (single-domain native); cross-domain to political theory, theology, economics is naturally dense
- Depth disclosure: implicit at the publisher level (volume-by-volume); explicit within each volume's preface
- Verdict: **Tagged for Phase 5 history sub-session** at TOC / bibliography level; adoption pending acquisition path (institutional library access vs. per-volume purchase)

**Theology — Encyclopedia of Religion (Eliade, Lindsay Jones eds.) + Oxford Research Encyclopedia of Religion**
- *Encyclopedia of Religion* (Macmillan Reference, 15-volume 2nd edition) — comprehensive cross-tradition entries with explicit cross-references; subscription/institutional via Gale eBooks
- Oxford Research Encyclopedia of Religion ([oxfordre.com/religion](https://oxfordre.com/religion)) — peer-reviewed long-form entries, growing collection; subscription/institutional
- License: consultable-only; structural extraction fact-shaped
- Form: long-form prose with explicit cross-references between traditions, concepts, and figures
- Coverage: theology (single-domain native); strong cross-domain to philosophy (philosophy of religion) and history
- Depth disclosure: explicit — both works document their editorial scope
- Verdict: **Tagged for Phase 5 theology sub-session**; adoption pending acquisition path

**Literature — Princeton Encyclopedia of Poetry and Poetics + Routledge Encyclopedia of World Literature**
- Princeton Encyclopedia of Poetry and Poetics ([press.princeton.edu](https://press.princeton.edu/books/hardcover/9780691133348/the-princeton-encyclopedia-of-poetry-and-poetics)) — single-volume reference; print and licensed digital editions; ~1,200 entries with extensive cross-references
- Routledge Encyclopedia of World Literature ([routledge.com](https://www.routledge.com/)) — subscription / institutional
- License: consultable-only; entry titles publicly listed
- Form: long-form prose with cross-references (Princeton edition is print-first; cross-references are explicit "see X" markers)
- Coverage: literature (single-domain native); spans poetry / fiction / drama traditions; cross-domain to philosophy (aesthetics, philosophy of language) and history natural
- Depth disclosure: explicit (Princeton edition's preface documents tradition-by-tradition coverage)
- Verdict: **Tagged for Phase 5 literature sub-session**; Princeton edition is the natural primary for poetry-adjacent concepts; adoption pending acquisition

**Economics — New Palgrave Dictionary of Economics**
- New Palgrave Dictionary of Economics ([link.springer.com/referencework/10.1057/978-1-349-95189-5](https://link.springer.com/referencework/10.1057/978-1-349-95189-5)) — Palgrave Macmillan; ~3,000 entries; comprehensive cross-references; subscription/institutional
- License: consultable-only; entry titles publicly listed
- Form: long-form prose with structured cross-references
- Coverage: economics (single-domain native); cross-domain to political theory, philosophy (ethics, decision theory), history of economic thought rich
- Depth disclosure: explicit (each edition's preface documents scope)
- Verdict: **Tagged for Phase 5 economics sub-session**; primary recommendation for the domain; adoption pending acquisition

**Poetry — Princeton Encyclopedia of Poetry and Poetics (primary)**
- Cross-listed with literature above. The Princeton encyclopedia is the canonical structural reference for poetry as a distinct mastery domain (per [`expansion.md`](expansion.md) which lists poetry separately from literature).
- License: consultable-only
- Form: long-form prose with explicit cross-references
- Coverage: poetry (single-domain native); cross-domain to literature, philosophy (aesthetics), and theology natural
- Depth disclosure: explicit
- Verdict: **Tagged for Phase 5 poetry sub-session**; same volume as the literature primary but with the entry-set scoped to verse-form, prosody, and poetic tradition entries

**Political theory — Routledge Encyclopedia of Political Thought + Stanford Encyclopedia of Philosophy (political-philosophy entries)**
- Routledge Encyclopedia of Political Thought ([routledge.com](https://www.routledge.com/)) — print/subscription; cross-references between thinkers, traditions, concepts
- Stanford Encyclopedia of Philosophy political-philosophy entries (already covered in Tier 4) — exhaustive on the philosophy/political-theory border concepts
- License: consultable-only (Routledge); SEP per Tier 4
- Form: long-form prose with cross-references
- Coverage: political theory (single-domain); strong overlap with philosophy
- Depth disclosure: explicit
- Verdict: **Tagged for Phase 5 political-theory sub-session**; SEP coverage in Tier 4 already addresses the philosophy/political-theory border; the Routledge volume is the supplementary primary

**Law — Oxford Public International Law + Cornell Legal Information Institute**
- Oxford Public International Law ([opil.ouplaw.com](https://opil.ouplaw.com/)) — subscription/institutional; encyclopedia entries on international-law concepts, cases, treaties; explicit cross-references
- Cornell Legal Information Institute ([law.cornell.edu/wex](https://www.law.cornell.edu/wex)) — Wex legal encyclopedia; free public access; CC BY-NC-SA license; ~7,000 entries on US law concepts with cross-references
- License: Cornell LII Wex is CC BY-NC-SA — ingestable for non-commercial structural extraction; Oxford OPIL is consultable-only
- Form: long-form prose with explicit cross-references in both
- Coverage: law (Cornell LII US-domestic-focused; Oxford OPIL international); cross-domain to political theory, philosophy (jurisprudence) natural
- Depth disclosure: explicit
- Verdict: **Tagged for Phase 5 law sub-session**; Cornell LII is the load-bearing primary for graph-shape extraction (free + CC BY-NC-SA structural extraction supportable for personal-use derivation); Oxford OPIL is supplementary on international concepts

**Psychology — APA Dictionary of Psychology + Oxford Reference psychology titles**
- APA Dictionary of Psychology ([dictionary.apa.org](https://dictionary.apa.org/)) — free public access for individual entry lookup; comprehensive cross-references; ~25,000 terms
- Oxford Reference psychology titles ([oxfordreference.com](https://www.oxfordreference.com/)) — subscription/institutional; multiple psychology-domain dictionaries
- License: APA Dictionary is free-access (publisher copyright on prose; entry-list and cross-reference adjacency are facts); Oxford is consultable-only
- Form: short-entry dictionary (APA) with cross-references; long-form prose (Oxford handbooks and dictionaries)
- Coverage: psychology (single-domain native); cross-domain to philosophy (philosophy of mind) natural
- Depth disclosure: APA Dictionary explicit on scope (terminology only, not theory exposition)
- Verdict: **Tagged for Phase 5 psychology sub-session** if/when psychology is admitted as a primary mastery domain (per [`expansion.md`](expansion.md) line 48 cross-domain-edges note — psychology is named in the cross-domain context, not yet committed as a primary domain); APA Dictionary is the natural primary for free-access graph-shape extraction

### Tier 3 candidates — bibliographies and citation graphs

Reading-list and co-occurrence priors. Tier 3 outputs are *prior-shape data* (which texts cluster together in actual courses; which papers cite which) used as cross-checks during Phase 5 source-recommendation authoring, not as structural seed inputs.

**Önduygu's reference page** ([denizcemonduygu.com/philo](https://denizcemonduygu.com/philo))
- Tier: 3
- Graph-shape: bibliography (the reference list); the propositions/edges layer is dialectical and explicitly excluded per axis 1 (see worked example above)
- License: all-rights-reserved on the visualization and prose; bibliographic facts (titles, authors, dates) are not copyrightable
- Form: bibliography; ~800 works enumerated
- Coverage: Western philosophy (single-domain); twelve-year solo-curated
- Depth disclosure: explicit (the author publishes a candid uneven-depth caveat — see worked example)
- Verdict: **Tagged for Phase 5 Western-philosophy sub-sessions** as a starting reading-list and tag-vocabulary checklist; the propositions/edges layer remains consciously not consulted

**Open Syllabus Project** ([opensyllabus.org](https://opensyllabus.org/))
- Tier: 3
- Graph-shape: co-occurrence (which texts are assigned together in actual courses); not prerequisite
- License: opaque from the public surface — most tools are free-to-use; bulk data access is research-partner gated; the indexed syllabi remain in their original copyright
- Form: structured-tabular (text-frequency rankings, co-assignment matrices via the Co-Assignment Galaxy tool); ~32.9 million syllabi indexed at the project level
- Coverage: cross-domain native (covers every academic discipline indexed in syllabi)
- Depth disclosure: implicit — the corpus is institution-skewed (heavily US, anglophone)
- Verdict: **Tagged for Phase 5 cross-domain edges sub-session (`006N`)** as a co-assignment prior — when the seed-authoring pass proposes a cross-domain edge between concepts X and Y, Open Syllabus's co-assignment data is a sanity check that the works supporting concepts X and Y do co-occur in actual curricula. Not a primary inventory source for any single domain.

**Semantic Scholar (S2AG / S2ORC datasets)** ([semanticscholar.org/about](https://www.semanticscholar.org/about))
- Tier: 3
- Graph-shape: citation (paper-to-paper); not prerequisite
- License: API and bulk datasets (S2AG, S2ORC) free for research / personal use; Semantic Scholar Academic Graph License governs redistribution; ~200 million papers indexed
- Form: structured-graph (citation network downloadable as JSON archives)
- Coverage: cross-domain native (every academic field indexed)
- Depth disclosure: explicit — Semantic Scholar publishes its source coverage notes
- Verdict: **Tagged for Phase 6 self-correction pipeline consultation, not Phase 5.** Citation-network data informs the *self-correction* pipeline (per [`self-correction.md`](self-correction.md)) — when a tension log records that learners struggle with concept X, the citation-network can surface highly-cited works addressing X that the graph might be missing. Phase 5 does not consume citation graphs as structural input (citations are influence-shaped per axis 1). Recorded here so Phase 6 sessions inherit the pointer.

### Tier 4 candidates — well-known structural references for the home discipline

The five candidates are evaluated for graph-shape value distinct from content value (per [ADR 0046](../adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md)). The content-value column is uniformly "low novel value (already parametrically accessible)" and is not repeated per candidate.

**Stanford Encyclopedia of Philosophy** ([plato.stanford.edu](https://plato.stanford.edu/), [info page](https://plato.stanford.edu/info.html))
- Tier: 4
- Graph-shape (load-bearing): high — peer-reviewed entries with extensive in-text cross-references; public Table of Contents and Chronological indexes; "Copyright of the Stanford Encyclopedia of Philosophy itself is held by the Metaphysics Research Lab at Stanford University. All rights are reserved." Crawling for indexing is explicitly permitted "subject to reasonable network usage constraints"; mirroring is permitted via listed mirror sites
- Content value: already parametrically accessible
- License posture (graph-shape extraction): consultable-only on prose; concept-inventory and cross-reference adjacency extraction is fact-shaped per Feist and explicitly supported by the publisher's crawl-for-indexing permission
- Form: long-form prose with explicit cross-references and an indexed entry catalog
- Coverage: philosophy (home-discipline native); ~1,800+ entries spanning every philosophy subdomain
- Depth disclosure: explicit (subject editors per area documented)
- Access-warrant disposition: free public access; no acquisition cost
- Verdict: **Tagged for Phase 5 philosophy sub-sessions as the primary structural reference** — every Phase 5 subdomain session (epistemology, ethics, metaphysics, philosophy of mind, philosophy of language, philosophy of science) consults SEP at boot for concept-inventory and cross-reference adjacency per [ROADMAP §5.2](../../ROADMAP.md). The existing posture in the "SEP as Structural Reference, Not Content Source" subsection above is unchanged; ADR 0046 extends it to the broader class

**Internet Encyclopedia of Philosophy** ([iep.utm.edu](https://iep.utm.edu/), [about page](https://iep.utm.edu/about/))
- Tier: 4
- Graph-shape (load-bearing): moderate — over 900 articles, indexed alphabetical browsing plus topical categorization (epistemology, ethics, etc.); peer-reviewed by 30 doctorate-holding editors; explicit cross-references between articles
- Content value: already parametrically accessible
- License posture: strict non-commercial — "free of charge and available to all users" with explicit prohibitions against for-profit republication; concept-inventory and cross-reference adjacency extraction is fact-shaped per Feist; bulk content extraction or republication forbidden
- Form: long-form prose with cross-references; A–Z and topic indexes public
- Coverage: philosophy (single-domain native); narrower than SEP but the entry-set overlaps with strong cross-reference density at the introductory layer
- Depth disclosure: explicit (editorial roster public)
- Access-warrant disposition: free public access; no acquisition cost
- Verdict: **Tagged for Phase 5 philosophy sub-sessions as a secondary structural reference** — IEP's coverage is narrower than SEP's but its introductory-tier entries are pedagogically calibrated in a way that complements SEP's research-tier depth. Cross-check entry-titles against SEP for every Phase 5 subdomain; surface candidate concepts that IEP carries and SEP does not, and vice versa.

**Routledge Encyclopedia of Philosophy** ([rep.routledge.com](https://www.rep.routledge.com/))
- Tier: 4
- Graph-shape (load-bearing): high — ~1,500 peer-reviewed entries with extensive cross-references; comprehensive scope across Western and non-Western philosophy traditions; publisher describes editorial-board oversight
- Content value: already parametrically accessible
- License posture: consultable-only — paywalled (subscription / institutional access); UK-published, so EU sui generis database rights additionally apply to the *compilation*; concept-inventory and cross-reference adjacency extraction from purchased / licensed access is fact-shaped per Feist with the additional UK/EU compilation-protection consideration; entry-titles publicly listed at the publisher's catalog
- Form: long-form prose with explicit cross-references; structured entry-headers (concept type, period, tradition tags)
- Coverage: philosophy (home-discipline native); broader than SEP on non-Western traditions
- Depth disclosure: explicit (each entry declares its scope and editorial calibration)
- Access-warrant disposition: requires acquisition (institutional library access, publisher subscription, or per-volume purchase). The graph-shape value is high enough to warrant pursuing legitimate acquisition for the Phase 5 sub-sessions covering non-Western and historical-period concepts SEP underweights
- Verdict: **Recommended pending acquisition** — pursue institutional access or licensed digital subscription before the Phase 5 sub-sessions covering non-Western traditions, history-of-philosophy concepts, or any subdomain where SEP coverage is thin. Adoption decision lands as an ADR in the consuming session

**Oxford Reference (philosophy titles)** ([oxfordreference.com](https://www.oxfordreference.com/), philosophy collection)
- Tier: 4
- Graph-shape (load-bearing): moderate-to-high — Oxford Reference aggregates dozens of Oxford-published philosophy dictionaries and companions (Oxford Companion to Philosophy, Oxford Dictionary of Philosophy, Oxford Handbook series); each title carries its own cross-reference structure; the union supports cross-title cross-references
- Content value: already parametrically accessible
- License posture: consultable-only — paywalled (subscription / institutional access); UK-published with EU sui generis database rights consideration; concept-inventory and cross-reference adjacency extraction from licensed access is fact-shaped per Feist with the compilation-protection caveat; title-list publicly browseable at oxfordreference.com
- Form: short-entry dictionary plus long-form companion / handbook prose
- Coverage: philosophy plus adjacent domains (the Tier 2 Oxford Reference recommendation for psychology, literature, etc. surfaces from the same platform)
- Depth disclosure: explicit per-title; uneven across the collection (handbooks deeper than dictionaries)
- Access-warrant disposition: requires acquisition (institutional library access or publisher subscription). Lower priority than Routledge for the home discipline because Oxford's strongest contribution is in adjacent-domain coverage (Tier 2 candidate role) rather than philosophy-specific depth beyond what SEP covers
- Verdict: **Recommended pending acquisition** — pursue institutional access if Tier 2 sub-sessions for psychology, literature, theology, or law are scheduled, since the same subscription unlocks the cross-domain coverage. Standalone philosophy-only acquisition is lower priority than Routledge

**Wikipedia** ([wikipedia.org](https://www.wikipedia.org/))
- Tier: 4
- Graph-shape (load-bearing): high in raw quantity, uneven in editorial discipline — every article has explicit cross-references (wiki-links) and structured sidebar metadata; cross-references include both pedagogically-meaningful "see also" links and incidental hyperlinks
- Content value: already parametrically accessible
- License posture: ingestable — Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0); structured datasets (Wikidata) under CC0; bulk dumps publicly available
- Form: long-form prose with structured cross-references and sidebar metadata; complementary structured-graph via Wikidata
- Coverage: cross-domain native; every academic discipline
- Depth disclosure: implicit — quality varies by article and language; Wikipedia documents its own editorial-quality grading (Featured, Good, B-class, etc.) per article
- Access-warrant disposition: free public access; no acquisition cost
- Verdict: **Tagged for Phase 5 consultation as a coverage cross-check** — when Phase 5 generative authoring proposes a concept inventory for a subdomain, cross-check the Wikipedia coverage to surface concepts the generative pass missed. Wikidata's structured cross-references are valuable for cross-domain edges (`006N`). Quality-grade per-article weighting matters; treat B-class-or-better articles as higher-trust signals than stub articles

### Phase 5 consumer pointer

Phase 5 seed-authoring sessions consult this survey at boot per [ROADMAP §5.2](../../ROADMAP.md) — Source approach. The per-tier verdicts above guide which sources each subdomain session reads first; per-candidate adoption decisions land as ADRs in the consuming session if they involve a non-trivial tradeoff (e.g., committing the project to a paid Routledge subscription for non-Western philosophy coverage). The survey is research and recording — adoption is contracted in-session at consumption time.

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
