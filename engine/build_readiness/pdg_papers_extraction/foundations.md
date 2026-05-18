# Foundational reading walkthrough — Session γ

> **Status:** Phase 6 pre-phase deliverable. Pre-Session-δ literature evidence for the four reading items kant_walkthrough.md §6.6 (F1-F4) carried forward. Quality-first posture; no Issues fire, no ADRs land, no decisions settled — Session δ adjudicates, this document supplies evidence.
>
> **Authoring session:** S-0201 (interactive build, 2026-05-17/18).
>
> **Voice precedent:** [`engine/build_readiness/phase_4_graph_validation.md`](../phase_4_graph_validation.md) (validation-document register); [`kant_walkthrough.md`](kant_walkthrough.md) §7 (per-deliverable structure).
>
> **Per-paragraph accountability:** every load-bearing claim carries an explicit evidence-tier marker — `[primary-verified]` (quoted from primary source via WebFetch), `[secondary-source]` (reliable secondary — SEP, university teaching centre, well-cited review — via WebFetch), `[model-knowledge]` (training-data summarization, no live verification this session), `[hedged]` (verification attempted, inconclusive). The taxonomy is operationalized epistemic honesty for downstream-Session-δ adjudication — claims without tier markers should be treated as `[model-knowledge]` by default but the absence is itself a defect.

## 1. Pre-walkthrough context

### 1.1 Why this session

Per [`HANDOFF.md`](../../../HANDOFF.md) "PDG papers extraction — pre-phase deliberation plan ready for interactive pickup": six pre-phase sessions land before any of the 17 synthesis-paper Issues fire. Sessions α and β are complete ([`adr_cross_reference_map.md`](adr_cross_reference_map.md) at S-0199; [`kant_walkthrough.md`](kant_walkthrough.md) at S-0200). Session γ is foundational reading — verify the synthesis paper's claims about Meyer & Land threshold concepts, Spiro cognitive flexibility, Middendorf & Pace bottleneck decoding, and Husserl's introspection-vs-phenomenology distinction against the underlying literature.

Session β surfaced four specific reading questions at [`kant_walkthrough.md` §6.6](kant_walkthrough.md#66-specific-findings-for-session-γ-foundational-reading):

- **F1.** Does Meyer & Land's "threshold concept" definition cleanly distinguish phenomenology-as-movement from phenomenology-as-method? The §3.2.1 multi-typing finding for the `phenomenology` node depends on this distinction.
- **F2.** Is the proposed `bridge_concept` enum value grounded in the literature or is it the synthesis paper authors' coinage? The §3.2.1 candidate `bridge_concept` read for phenomenology depends on whether the term has a stable cross-tradition meaning.
- **F3.** Is the bottleneck-vs-threshold distinction (Middendorf & Pace vs Meyer & Land) substantive enough to warrant a separate `bottleneck` enum value alongside `threshold_concept` in the proposed Cluster 4 `node_type` enum?
- **F4.** Does primary-source evidence support [`kant_walkthrough.md` §5.2.1](kant_walkthrough.md#521-substantive-content-of-the-misconception)'s framing of the phenomenology-vs-introspection distinction? The `remediation_note` for misconception (a) — "phenomenology = introspection" — depends on this.

### 1.2 Source-access posture

User direction at session start: WebSearch + WebFetch + model knowledge (no PDF reading; the 3 PDFs in `~/Documents/Claude_Files/temp/` are NOT the foundational sources). Primary academic papers are frequently paywalled (Springer redirects; Routledge / Taylor & Francis behind auth); the workable access path is (a) open-access secondary sources — university teaching centres, SEP / Wikipedia, Frontiers / PMC open-access journals — and (b) accessible primary sources where present. The `[primary-verified]` tier is rare; the `[secondary-source]` tier carries most of the load.

### 1.3 Out-of-scope (deliberate non-outputs)

Per the Session β disposition pattern (`kant_walkthrough.md` §7.2) and the HANDOFF quality-first posture:

- **No Issues filed.** Issues fire only after Session ζ.
- **No ADRs drafted.** Session δ drafts; Session γ supplies literature evidence.
- **No decisions settled.** Adjudication is Session δ's job.
- **No migrations authored.** Cluster migrations land after Session δ.
- **No re-typing of existing edges or nodes.** Session β disposition holds.
- **No node-type enum proposals.** F1-F4 supply evidence; Session δ proposes.

### 1.4 Cross-session-internal references

This walkthrough cites Session β's [`kant_walkthrough.md`](kant_walkthrough.md) heavily — particularly §3.2.1, §3.4.1, §5.2.1, §6.6, §6.7. It cites Session α's [`adr_cross_reference_map.md`](adr_cross_reference_map.md) C4 / C5 cross-cluster sections. The synthesis substrate is [`synthesis.md`](synthesis.md) Clusters 2, 4, 5, 8; source-paper extractions are [`extraction_paper_1.md`](extraction_paper_1.md) (particularly L293 — the explicit reading list — and L301 — Zahavi SEP entry pointer) and [`extraction_paper_2.md`](extraction_paper_2.md).

---

## 2. F1 — Meyer & Land threshold concepts

### 2.1 The question (verbatim)

From `kant_walkthrough.md` §6.6:

> **F1.** Meyer & Land's "threshold concept" framing (synthesis.md cites paper_1 references; Session γ should read Meyer & Land 2003 directly) — Session γ should test whether the "threshold concept" definition cleanly distinguishes phenomenology-as-movement from phenomenology-as-method. The §3.2.1 multi-typing finding hangs on this distinction.

### 2.2 The literature

**Primary sources** (all paywalled or PDF-image-only; not directly accessed this session):

- **Meyer, J.H.F. & Land, R. (2003).** "Threshold concepts and troublesome knowledge: Linkages to ways of thinking and practising within the disciplines." ETL Project occasional paper, ESRC/TLRP Enhancing Teaching and Learning Environments project. [PDF link extant at ee.ucl.ac.uk/mflanaga/ISL04-pp53-64-Land-et-al.pdf](https://www.ee.ucl.ac.uk/mflanaga/ISL04-pp53-64-Land-et-al.pdf) — WebFetch returned binary-PDF stream this session; primary access failed.
- **Meyer, J.H.F. & Land, R. (2005).** "Threshold concepts and troublesome knowledge (2): Epistemological considerations and a conceptual framework for teaching and learning." *Higher Education* 49(3), 373-388. [Springer link](https://link.springer.com/article/10.1007/s10734-004-6779-5) — redirected to auth gate; primary access failed.
- **Land, R., Cousin, G., Meyer, J.H.F., & Davies, P. (2005/2006).** "Threshold concepts and troublesome knowledge (3): implications for course design and evaluation." Subsequent ETL working paper.

**Secondary sources** (accessed this session):

- Faculty Focus, ["Threshold Concepts: Portals to New Ways of Thinking"](https://www.facultyfocus.com/articles/teaching-and-learning/threshold-concepts-portals-new-ways-thinking/) — five-characteristic summary.
- Wikipedia, ["Threshold knowledge"](https://en.wikipedia.org/wiki/Threshold_knowledge) — bibliographic timeline + Philosophy example ("Personhood") + bottleneck cross-reference.
- WebSearch hit cluster — Bain & Bass "10 Threshold Concepts of Teaching and Learning"; Centre for Engaged Learning "Threshold Concepts in Pedagogical Partnership"; UofT Mississauga threshold-knowledge working group; Western Washington University teaching handbook.

### 2.3 The finding — five (later more) characteristics

The 2003 ETL paper introduced threshold concepts with three characteristics; the 2005 *Higher Education* paper expanded to five; subsequent ETL work extended further. The widely-cited canonical list `[secondary-source]`:

- **Transformative** — "creates a significant shift in perception" / "powerful change in how learners think about their discipline, themselves, or the world" `[secondary-source]` (Faculty Focus quoting Meyer & Land).
- **Irreversible** — once understood, the knowledge is retained; learners cannot easily revert to previous ways of thinking `[secondary-source]` (Faculty Focus).
- **Integrative** — "exposes the previously hidden interrelatedness of something" / "enables students to knit dissimilar elements of a subject together" `[secondary-source]` (Faculty Focus + WebSearch snippet quoting Meyer & Land 2003).
- **Bounded** — "thresholds border other thresholds and help define disciplinary territories" `[secondary-source]` (Faculty Focus). This is what makes "threshold concepts" plural — each defines a territory and abuts others.
- **Troublesome** — "difficult to understand initially; appears counter-intuitive, alien, or incoherent" `[secondary-source]` (Faculty Focus, citing Meyer & Land's appropriation of Perkins 1999 "troublesome knowledge").

Later characteristics extending the framework `[model-knowledge]`:

- **Discursive** — acquisition involves new ways of speaking / new disciplinary vocabulary (Meyer & Land 2005 onward).
- **Reconstitutive** — acquisition can involve a shift in learner identity, not just understanding (Meyer & Land 2005-2006).
- **Liminal** — the learner traverses a liminal space between pre-threshold and post-threshold understanding; the framework appropriates Turner's anthropological concept (Cousin 2006 onward).

### 2.4 The finding — does the framework distinguish movement-from-method?

The literature's own examples are mostly individual concepts, not movements or methods:

- **Economics:** opportunity cost, marginal utility `[model-knowledge]` — both are concepts.
- **Physics / engineering:** heat as energy transfer, limit (calculus) `[model-knowledge]` — both are concepts.
- **Philosophy (Wikipedia):** "Personhood" `[secondary-source]` — a concept.
- **Literature (Wikipedia):** "Deconstruction" `[secondary-source]` — this is ambiguous; "deconstruction" names BOTH a movement (post-structuralism) AND a reading practice. Wikipedia's classification of it as a threshold concept treats the practice-side, not the movement-side.
- **Law (Wikipedia):** "Legal Narrative" `[secondary-source]` — a practice / disciplinary frame.

The 2003 paper subtitle is `[secondary-source]` (WebSearch snippet): "Linkages to ways of thinking and practising within the disciplines." This explicitly extends threshold-concept framing to **ways of thinking and practising** — i.e., methods and disciplinary practices are admitted as threshold-shaped. The framework is broader than concept-only.

But the framework does NOT admit *movements* or *traditions* as threshold-shaped. Movements (the historical-period bundle of practitioners + works + chronology) are too coarse-grained to be transformative-for-an-individual-learner in the way the framework requires. A learner does not "cross a threshold" by becoming aware that phenomenology-as-movement existed — they cross a threshold by mastering a specific Husserlian concept (intentionality, the natural attitude, the phenomenological reduction) and finding their prior framing reorganized. `[hedged]` — the literature does not directly assert this exclusion, but the consistent example pattern (always concepts or methods, never movements/traditions) and the transformative-integrative-irreversible criteria (which apply to learner cognition, not to historical-period awareness) jointly imply it.

### 2.5 Application to the `phenomenology` node

Per [`kant_walkthrough.md` §3.2.1.A](kant_walkthrough.md#321-proposed-node_type-enum-candidates), the `phenomenology` node currently fits multiple proposed `node_type` enum values because the node-as-authored conflates phenomenology-as-movement (the 20th-century European tradition) with phenomenology-as-method (the phenomenological reduction / epoché).

The Meyer & Land framework cleanly distinguishes:

- **Phenomenology-as-method** (the phenomenological reduction, intentionality, bracketing) — **YES, this is threshold-concept-shaped.** It satisfies all five characteristics: transformative (reframes what counts as evidence about consciousness), irreversible (once a learner grasps the reduction, naive psychological framing no longer suffices), integrative (knits perception + judgment + language under a single methodological frame), bounded (distinct from analytic introspection-talk and from neuroscientific consciousness-talk), troublesome (the introspection misconception §5.2 is the canonical evidence). It is also "discursive" — phenomenological vocabulary (noematic, noetic, intentional act) is part of the threshold. `[model-knowledge]` (the application is reasoning, not direct quotation).
- **Phenomenology-as-movement** (the historical bundle of Husserl + Heidegger + Sartre + Merleau-Ponty + Levinas + chronology + institutional history) — **NO, this is NOT threshold-concept-shaped.** Awareness of the movement's existence is encyclopedic background, not transformative-for-the-learner. A learner can know all the movement's chronology and not have crossed any threshold; conversely, a learner can master the reduction without memorizing the movement's history. `[model-knowledge]`.

The §3.2.1.A multi-typing finding is therefore **partially explained** by movement/method conflation in the node-as-authored. **Splitting the phenomenology node** into a method-node (`phenomenology_method` or `phenomenological_reduction` — threshold-shaped) and a context-node (`phenomenology_movement` or `phenomenological_tradition` — not threshold-shaped, possibly `historical_context` or `tradition_label` per Cluster 4/8) is one resolution. **Multi-typing the existing node** is another — accept that the node carries content for both readings and the `node_type` field accommodates both via array-form.

The literature does not adjudicate between these two paths; it does adjudicate that the threshold-concept reading applies to method-content, not movement-content.

### 2.6 Feedback to Session δ

**D2 (single-valued vs multi-valued `node_type`) — empirical input.** The F1 finding strengthens the §3.2.1.A case for multi-typing OR node-splitting. Single-valued `node_type` with no further accommodation would force `phenomenology` to either lose its method-side semantic content (re-typed as `historical_context`/`tradition_label`) or lose its movement-side (re-typed as `threshold_concept`). Both losses degrade the data.

**D3 (`subfield` / `discipline_area` enum gap) — F1 supplies no direct input.** F1 is about the `threshold_concept` value; D3 is about the `philosophy_of_mind` node's no-fit problem (§3.4.1). The two are orthogonal.

**D1 (`historical_context` ADR 0008 read) — F1 supplies adjacent input.** If `phenomenology_movement` is split off and typed as `historical_context`, the ADR 0008 question (movements as nodes) fires the same way §3.5.B framed it. F1 does not resolve D1; F1 motivates the question.

**Recommendation for the Session δ ADR Decision section:** name the threshold-concept-vs-movement distinction as a worked example demonstrating that node-type enum values index DIFFERENT semantic dimensions of the SAME real-world referent (phenomenology). Whether the schema accommodates this via multi-typing, node-splitting, or secondary type-tags is the Session δ choice; F1 demonstrates the underlying semantic reality.

### 2.7 Carry-forward / open questions

- **Q1-F1.** Does the literature explicitly discuss "movement" vs "method" decomposition for threshold-concept-shaped historical entities? The hedged claim in §2.4 above (the literature does not directly assert the exclusion) deserves a primary-source check at the next session that can access Meyer & Land 2005 / Land et al. 2005 directly.
- **Q2-F1.** Are there discipline-specific threshold-concept lists for philosophy that the §3.2.1 analysis can audit `phenomenology` against? Corrigan's literary-studies threshold-concept list (per [`extraction_paper_1.md` L301](extraction_paper_1.md#L301)) suggests parallel philosophy lists likely exist in the literature. Session δ or later.

---

## 3. F2 — Spiro cognitive flexibility + `bridge_concept` grounding

### 3.1 The question (verbatim)

From `kant_walkthrough.md` §6.6:

> **F2.** Spiro et al. on cognitive flexibility theory — Session γ should test whether the proposed `bridge_concept` enum value is grounded in the literature or is the synthesis authors' coinage. The §3.2.1 `bridge_concept` candidate read for phenomenology depends on whether the term has a stable cross-tradition meaning.

### 3.2 The literature

**Primary sources** (paywalled or PDF-image; not directly accessed this session):

- **Spiro, R.J., Feltovich, P.J., Jacobson, M.J., & Coulson, R.L. (1991/1992).** "Cognitive flexibility, constructivism, and hypertext: Random access instruction for advanced knowledge acquisition in ill-structured domains." *Educational Technology* 31(5), 24-33. — Semantic Scholar entry extant, paper itself paywalled.
- **Spiro, R.J., Coulson, R.L., Feltovich, P.J., & Anderson, D.K. (1988).** "Cognitive flexibility theory: Advanced knowledge acquisition in ill-structured domains." Tenth Annual Conference of the Cognitive Science Society. — Original CFT statement; not directly accessed.

**Secondary sources** (accessed this session):

- ScienceDirect, ["Cognitive Flexibility Theory — an overview"](https://www.sciencedirect.com/topics/psychology/cognitive-flexibility-theory) — CFT foundational definitions.
- InstructionalDesign.org, ["Cognitive Flexibility Theory (Spiro, Feltovich & Coulson)"](https://www.instructionaldesign.org/theories/cognitive-flexibility/) — pedagogy summary.
- Multiple secondary sources accessed via WebSearch on `"bridge concept" pedagogy education "threshold concept"` — none yielded "bridge concept" as a named pedagogical category. Hits exclusively used the term metaphorically (e.g., Hudson's [Medium / GOA piece on "Threshold Concepts: A Bridge Between Skills and Content"](https://medium.com/@ejhudson/threshold-concepts-a-bridge-between-skills-and-content-54331b2bacd)) — threshold concepts ARE bridges, not threshold concepts vs bridge concepts.

### 3.3 The finding — Spiro's actual vocabulary

Cognitive Flexibility Theory's named constructs `[secondary-source]`:

- **Ill-structured domains** — domains where knowledge cannot be reduced to a single set of organizing principles applicable across all cases.
- **Cognitive flexibility** — "the ability to spontaneously restructure one's knowledge, in many ways, in adaptive response to radically changing situational demands."
- **Multiple knowledge representations** — instruction induces "multiple and... flexible representations of the knowledge, which can be applied in many different contexts."
- **Criss-crossing the conceptual landscape** — revisiting the same material at different times, in rearranged contexts, for different purposes, from different perspectives.
- **Crossroads cases** — illustrative cases at the intersection of multiple conceptual themes.
- **Conceptual variability** — exposure to many cases varying in surface features but unified by underlying principles.

**The term "bridge concept" does not appear in CFT's canonical vocabulary** `[hedged]` — the secondary sources accessed do not use it; WebSearch returned zero results for "bridge concept" in conjunction with Spiro / CFT. Primary-source verification (accessing Spiro et al. 1988/1991 directly) would be needed to assert this strictly, but the secondary literature's silence is strong evidence.

What CFT *does* support that is adjacent to a "bridge concept" function `[model-knowledge]`:

- **Knowledge-as-criss-crossing** suggests that some concepts SERVE a connecting / linking function across multiple conceptual perspectives. CFT's epistemology is that ill-structured-domain mastery requires holding multiple frames simultaneously, and certain pivot-concepts enable that holding.
- **Crossroads cases** are the case-level analog of bridge concepts — concrete instances where multiple themes intersect. A graph encoding "crossroads-case-shaped nodes" would be CFT-aligned; whether it would be called `bridge_concept` is a coinage choice, not a literature-grounded label.

### 3.4 The finding — where else does "bridge concept" appear?

A WebSearch for `"bridge concept" pedagogy education "threshold concept"` returned hits where the term is used metaphorically (threshold concepts described as bridges) but not as a distinct named pedagogical category `[secondary-source]`. Specifically:

- **Hudson (Medium / GOA), "Threshold Concepts: A Bridge Between Skills and Content"** — Hudson treats threshold concepts AS bridges; "bridge concept" is not Hudson's own coinage as a distinct category.
- **Centre for Engaged Learning, "Threshold Concepts in Pedagogical Partnership"** — bridges identity to disciplinary knowledge; metaphorical usage.

**Adjacent terms that DO appear in the literature** `[model-knowledge]`:

- **"Linking concept"** — used in science-education research (Klausmeier 1970s, Novak 1980s concept-mapping tradition) to denote concepts that connect propositions in a concept map. Different framework from CFT / threshold-concept work.
- **"Hinge concept"** / **"Pivot concept"** — used in some math-education and design-education literature for concepts whose mastery unlocks several adjacent concepts. Closer to CFT's crossroads-case function but still not a stabilized term.
- **"Boundary concept"** / **"Boundary object"** (Star & Griesemer 1989; Akkerman & Bakker 2011) — sociology-of-science / educational-research term for concepts that mediate across disciplinary or community boundaries. Closest to what `bridge_concept` could mean if defined to span discipline-traditions; but "boundary" is the canonical term, not "bridge."

### 3.5 The finding — verdict on `bridge_concept` as enum value

The synthesis paper's `bridge_concept` enum value (per [`synthesis.md` Cluster 4 L151](synthesis.md)) is **a synthesis-paper coinage**, not a literature-grounded category `[hedged on absence-of-evidence; reasonably-confident on positive coinage attribution]`. The grounding in CFT is partial — CFT's epistemology supports the EXISTENCE of bridge-function concepts but does not name them as a category. Adjacent literature uses "linking," "hinge," "pivot," or (most rigorously) "boundary" — none of which are `bridge_concept`.

**Three readings for Session δ:**

- **(a) Rename the enum value** to a literature-grounded term — `boundary_concept` (per Star & Griesemer / Akkerman & Bakker) is the strongest candidate. Pros: lit-grounded, citation-able, distinct from `threshold_concept`. Cons: "boundary" has STS connotations that may not match the synthesis paper's intent (cross-disciplinary mediation vs cross-tradition pedagogical bridging).
- **(b) Keep `bridge_concept` as a coinage** but document it as such in the migration's contract block — name the CFT alignment, name the absence of a literature-stabilized term, name the choice. Pros: preserves the synthesis paper's framing; Cons: adds a non-citable term to the schema.
- **(c) Drop the enum value** and accommodate the bridge-function via secondary tags (e.g., `audience_tags: ['bridges_analytic_continental']`) or via cross-tradition edges (`comparative_lens` is already in the enum). Pros: avoids the grounding question; Cons: loses node-type clarity.

The §3.2.1 finding that `phenomenology` plausibly fits `bridge_concept` (bridging analytic-continental traditions) is empirical regardless of which path Session δ chooses — the data ARE bridge-shaped; the question is what to call the type.

### 3.6 Feedback to Session δ

**D2 (single-valued vs multi-valued `node_type`) — empirical input.** F2's finding that `bridge_concept` is a coinage strengthens (rather than weakens) the case for explicit enum-value provenance documentation in the resulting ADR. If Session δ chooses (b) — keep `bridge_concept` as coinage — the ADR's Decision section should name the CFT-adjacent grounding AND the absence of a literature-stabilized term, so downstream sessions don't mistake the enum value for a citable category.

**D8 (per-layer enums as open-for-revision lists) — F2 directly supports.** The `node_type` enum is exactly the kind of "open-for-revision list" §6.7 D8 names. F2's finding (one enum value is a coinage, not literature-grounded) is empirical evidence that the enum SHOULD carry explicit revision procedures and version-tracking — not be treated as a closed contract.

### 3.7 Carry-forward / open questions

- **Q1-F2.** Should Session δ consult the **boundary-objects** literature (Star & Griesemer 1989; Akkerman & Bakker 2011) directly before settling the `bridge_concept` enum value? If `boundary_concept` is the lit-grounded replacement, the BO literature carries the definitional precision Session δ would inherit.
- **Q2-F2.** Are there CFT-derived node-typing proposals in the broader concept-mapping / knowledge-representation literature (post-2010, post-Spiro)? F2's primary-source access was blocked this session; a later session with access could close the question.
- **Q3-F2.** If Session δ chooses path (c) — drop the enum value — does the existing `comparative_lens` enum value already cover the bridge-function semantically? F2's framing suggests yes-but-imperfectly: `comparative_lens` operates between traditions; `bridge_concept` IS one of the bridged elements. The distinction is real but fine-grained.

---

## 4. F3 — Middendorf & Pace bottleneck decoding

### 4.1 The question (verbatim)

From `kant_walkthrough.md` §6.6:

> **F3.** Middendorf & Pace on "bottleneck" decoding (a sibling concept to threshold) — Session γ should test whether bottleneck-shaped concepts deserve a separate enum value (proposed Cluster 4 enum doesn't include `bottleneck`).

### 4.2 The literature

**Primary sources** (paywalled or PDF-image; not directly accessed this session):

- **Middendorf, J. & Pace, D. (2004).** "Decoding the Disciplines: A model for helping students learn disciplinary ways of thinking." *New Directions for Teaching and Learning* 98, 1-12. — Wiley/Jossey-Bass volume; paywalled.
- **Pace, D. (2017).** *The Decoding the Disciplines Paradigm: Seven Steps to Increased Student Learning.* Indiana University Press. — Book-length statement; not directly accessed.
- **decodingthedisciplines.org** — the project's home page (active 2026); decoding wiki extant at decodingthedisciplines.de.

**Secondary sources** (accessed this session):

- Georgetown CNDLS, ["Bottlenecks and Thresholds"](https://cndls.georgetown.edu/resources/bottlenecks-and-thresholds/) — explicit comparison.
- decodingthedisciplines.de wiki entry on threshold concept.
- WebSearch hit cluster — Rowan U "Bottlenecks of Information Literacy" chapter; NRPA SCHOLE journal article on bottlenecks.

### 4.3 The finding — definitions

**Bottleneck** (Pace & Middendorf) `[secondary-source]` (Georgetown CNDLS): a place where "students get stuck" on "concepts or skills that consistently seem to stymie students." The framework emphasizes precise identification — vague ("Students cannot interpret texts") vs precise ("Students skip the observation stage before interpreting").

**Threshold concept** (Meyer & Land) `[secondary-source]` (Georgetown CNDLS quoting Meyer & Land): "Ideas that are fundamental to progressing beyond elementary thinking in a discipline" — functioning "like passing through a portal, from which a new perspective opens up" enabling "a transformed way of understanding" that is "without which the learner cannot progress."

### 4.4 The finding — categorical relationship

Two related secondary sources converge on the categorical relationship `[secondary-source]`:

- **Georgetown CNDLS:** "There may be some challenging ideas or skills which students must master in order to succeed in the course but which aren't gateways to a new way of thinking particular to your discipline; in other cases, students need to master more centrally important things." This implies threshold concepts are a **subset** of bottlenecks — specifically, those with deeper disciplinary significance.
- **Wikipedia "Threshold knowledge":** "The notion of threshold concept is related to the notion of bottleneck in the Decoding the Disciplines framework. **It can be considered a special case of the latter.**"
- **WebSearch snippet:** "In categorical terms, **every threshold concept is a bottleneck while not every bottleneck is a threshold concept.**"

The literature's positive claim: **threshold concepts ⊂ bottlenecks**. Bottlenecks are the broader category; threshold concepts are the proper subset whose mastery is transformative (per F1's five characteristics).

### 4.5 The finding — bottleneck-type partition

Pace & Middendorf distinguish two bottleneck-types requiring different pedagogical interventions `[secondary-source]` (Georgetown CNDLS):

- **Cognitive bottlenecks** — comprehension or thinking issues. Intervention: break tasks into explicit mental components; use modeling and practice opportunities. Statistics example: students choosing wrong tests need decision trees ("How many groups?") and step-by-step instruction.
- **Emotional bottlenecks** — resistance, discomfort, negative emotional reactions. Intervention: focus on motivation and articulating importance; create space for concerns. "Students in distress have trouble learning."

This bipartition is not present in the threshold-concept framework — threshold concepts have transformative/integrative/troublesome characteristics, but the troublesome characteristic does not subdivide into cognitive vs emotional.

### 4.6 Application to the proposed `node_type` enum

The proposed Cluster 4 `node_type` enum (per [`synthesis.md` Cluster 4 L151](synthesis.md)) carries `threshold_concept`, `bridge_concept`, `disciplinary_practice`, `text_excerpt`, `historical_context`, `misconception`, `comparative_lens`, `assessment_task` — **eight values, no `bottleneck`**.

Three readings for whether to add `bottleneck`:

- **(a) Add a single `bottleneck` value.** Treats bottlenecks as a node-type peer of threshold concepts. Pros: lit-grounded; admits non-transformative-but-stuck-on places into the graph. Cons: per F3's finding, threshold concepts ARE bottlenecks (the subset relation), so a node typed `bottleneck` is implicitly disjoint from `threshold_concept` — but that breaks the literature's subset relationship.
- **(b) Add `cognitive_bottleneck` and `emotional_bottleneck` values.** Preserves the Decoding-the-Disciplines bipartition. Pros: more specific; aligns with the emotional-bottleneck literature (Diaz, Middendorf, Pace 2008 — emotional bottleneck in history classroom). Cons: doubles the enum width; the emotional bottleneck question is pedagogical-process, not concept-structure, and may not belong on the NODE.
- **(c) Treat bottleneck as an EDGE property or NODE flag, not an enum value.** Per the literature's subset relation (threshold ⊂ bottleneck), every node could carry an `is_bottleneck` boolean (defaults to TRUE for `threshold_concept`-typed nodes; admits TRUE for nodes that aren't threshold-shaped but are still stuck-on). Pros: respects the subset relation; doesn't bloat the enum. Cons: another bool field where the enum is already crowded.
- **(d) Decline to encode bottleneck-shaped nodes structurally; defer to authoring discipline.** Bottleneck identification is the Decoding-the-Disciplines step 1, but the structural representation in the Paideia graph could be implicit — flagged by the authoring-pass per [`synthesis.md` Cluster 6](synthesis.md) (the Decoding-the-Disciplines authoring discipline). Pros: keeps the schema lean; recognizes that bottleneck is a discovery-mode predicate, not a stable node-type. Cons: loses the structural representation; bottlenecks become discoverable only through authoring metadata.

### 4.7 The finding — emotional-bottleneck question

The emotional-bottleneck partition is a substantive question Session δ should consider explicitly. Paper_1 and paper_2 do not surface emotional bottlenecks specifically; the synthesis paper's Cluster 5 (misconceptions) covers cognitive-bottleneck content (folk misconceptions that block learning) but does NOT cover emotional bottlenecks (resistance, discomfort, identity-threat). `[hedged on absence]`

If emotional bottlenecks are admitted into the schema (per reading (b) above), the implications cascade `[model-knowledge]`:

- New node-type `emotional_bottleneck` with examples like "discomfort with religious content in religious studies courses" or "resistance to critical race theory in U.S. history."
- New edge type `triggers_emotional_response` or `requires_affective_preparation` (Cluster 2 extension).
- Phase 7+ teaching-app integration with student affective-state monitoring (substantial substrate commitment).

If emotional bottlenecks are NOT admitted (per readings (a), (c), or (d)), the Paideia schema implicitly treats all bottlenecks as cognitive — which is the existing posture but worth making explicit.

### 4.8 Feedback to Session δ

**D2 (single-valued vs multi-valued `node_type`) — F3 supplies adjacent input.** If reading (b) above is chosen, the enum doubles; if multi-typing is also adopted (per F1 / F2 feedback), the schema becomes substantially more expressive. Session δ should consider the joint cost.

**D3 (`subfield` / `discipline_area` enum gap) — F3 indirectly bears.** Both D3 and F3's reading (a/b/c) options expand the enum. If Session δ is conservative about enum expansion, both should be denied; if expansive, both can be admitted in a single migration.

**D8 (per-layer enums as open-for-revision lists) — F3 reinforces.** Adding `bottleneck` (or `cognitive_bottleneck` / `emotional_bottleneck`) post-hoc is exactly the kind of revision the D8 procedure should make easy. The enum being open-for-revision is what allows the literature-evolution to flow into the schema.

**Recommendation for the Session δ ADR Decision section:** state explicitly which of readings (a)/(b)/(c)/(d) the schema adopts. If declining to add `bottleneck` (reading d), name the Decoding-the-Disciplines authoring-discipline (Cluster 6) as the alternative locus for bottleneck identification — the schema delegation should be explicit.

### 4.9 Carry-forward / open questions

- **Q1-F3.** Pace 2017's full seven-step Decoding-the-Disciplines paradigm is the latest authoritative statement; Session δ should access it directly if available. The seven steps may suggest additional schema additions beyond bottleneck-typing (e.g., the modeling-of-expert-thinking step at step 3 may motivate node-property additions).
- **Q2-F3.** Does the existing Cluster 6 authoring-discipline ops doc draft (the Decoding-the-Disciplines authoring discipline) already prescribe a bottleneck-identification step? If yes, reading (d) becomes the natural posture; if no, Cluster 6 needs extension.
- **Q3-F3.** Is the cognitive-vs-emotional bipartition a node-property or an edge-property? An emotional bottleneck might be better encoded as an edge type (`affective_blocking_prerequisite`) rather than a node type — the emotional response is RELATIONAL (between the learner and the content) rather than structural (a property of the content).

---

## 5. F4 — Husserl primary-source verification

### 5.1 The question (verbatim)

From `kant_walkthrough.md` §6.6:

> **F4.** Husserl's own writings on the phenomenological reduction — Session γ should verify the §5.2.1 framing of the introspection / phenomenology distinction. The author's notes on this point should be cited in the misconception (a) `remediation_note` field.

The §5.2.1 framing under verification (verbatim from `kant_walkthrough.md` §5.2.1):

> The misconception holds that phenomenology IS introspection — i.e., the project of looking inward at one's own mental states and reporting what one finds. The reality (per Husserl 1900, 1913): phenomenology is a method (the phenomenological reduction / epoché) for studying conscious experience AS IT IS GIVEN, bracketing questions of metaphysical reality. The reduction is methodological, not psychological. Introspection produces psychological reports; phenomenology produces structural descriptions of conscious experience.

### 5.2 The literature

**Primary sources** (cited via SEP entry; direct access not attempted this session):

- **Husserl, E. (1900-1901).** *Logical Investigations* (*Logische Untersuchungen*). The first formulation of phenomenology; initially termed "descriptive psychology" — a label Husserl later regretted.
- **Husserl, E. (1913).** *Ideas Pertaining to a Pure Phenomenology and to a Phenomenological Philosophy, First Book* (*Ideen I*). Introduces the epoché / phenomenological reduction; explicitly distances phenomenology from psychology.
- **Husserl, E. (1931).** *Cartesian Meditations* (*Cartesianische Meditationen*). Presents epoché and reduction as methodological requirements; emphasizes transcendental reflection on consciousness-world correlation.
- **Husserl, E. (1937 letter).** Cited in SEP entry: explicit rejection of Brentano's "descriptive psychology" framing.

**Secondary sources** (accessed this session):

- Stanford Encyclopedia of Philosophy, ["Edmund Husserl"](https://plato.stanford.edu/entries/husserl/) — primary verification target (explicitly named in [`extraction_paper_1.md` L301](extraction_paper_1.md#L301)).
- Frontiers in Psychology (Tewes 2018), ["Husserlian Phenomenology as a Kind of Introspection"](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.00896/full) — dissenting / refining view.
- WebSearch hit cluster — Notre Dame Philosophical Reviews on Zahavi's *Husserl's Legacy*; PhilPapers entry on Zahavi's *Husserl's Phenomenology*; Wikipedia Dan Zahavi.

### 5.3 The finding — majority view

The majority of phenomenology scholars treat phenomenology and introspection as fundamentally distinct `[secondary-source]` (Frontiers paper acknowledging the majority position, citing Thomasson, Smith and Thomasson, Zahavi, Staiti, Fuchs).

The SEP entry (the explicit Session β citation target) confirms this `[secondary-source]`:

- The phenomenological reduction (epoché) "is by no means a suspension of the being of the world... rather, it is the path leading to the discovery of correlational judgements" (Husserl, Hua 15/366, quoted in SEP).
- Husserl "rejected characterizing phenomenology as 'descriptive psychology' after his initial formulation, coming to 'regret this as a serious mischaracterization.'"
- Husserl's 1937 letter: his thinking "was a totally different one from that of Brentano" and Brentano's psychology never grasped "the proper problems of intentionality."
- The SEP entry "treats 'phenomenology = introspection/psychology' as a persistent misconception worth correcting."

### 5.4 The finding — minority / refining view

There is an active scholarly debate. The Frontiers paper (Tewes 2018) argues `[secondary-source]`:

> The thesis of this article is that Husserl's proposed method for intuitively exploring the essential or a priori laws of consciousness IS a kind of introspection.

The argument: Husserl's epoché is methodological refinement of introspection, not a wholesale rejection. The systematic methodology — bracketing existential commitments, focusing on how-of-givenness, distinguishing essential from idiosyncratic features — addresses precisely the pitfalls of "naive introspection" (uncontrolled scope of awareness, false prejudices, idiosyncratic-vs-general confusion). What remains after the refinement IS introspection, just disciplined.

Tewes notes Husserl himself was ambivalent — "occasionally characterized [phenomenology] as introspection" in *Logical Investigations* and *Ideas I* — supporting the refined-introspection reading.

### 5.5 The finding — verdict on §5.2.1 framing

The §5.2.1 framing is **substantively correct on the majority reading** `[secondary-source-supported]`, but **incomplete on the scholarly nuance** `[hedged]`.

Specifically:

- **Substantively correct:** Phenomenology IS NOT *naive* introspection — the project of "looking inward at one's own mental states and reporting what one finds" without method. Husserl rejects this framing. The phenomenological reduction (epoché) IS a methodological commitment that distinguishes Husserl's method from psychological introspection. Primary-source support: *Ideas I* 1913 introduces the reduction explicitly; Husserl's 1937 letter rejects the Brentano framing; SEP entry treats the conflation as a "persistent misconception."
- **Incomplete on nuance:** The framing "Introspection produces psychological reports; phenomenology produces structural descriptions of conscious experience" is true on the majority reading but admits a refining counter-position (Tewes and others) that treats phenomenology as REFINED introspection. A `remediation_note` that asserts categorical distinctness without acknowledging the refined-introspection reading omits an active scholarly debate. Different downstream sessions/audiences may find one or the other framing more useful.

The most defensible `remediation_note` shape for Paideia `[model-knowledge applying the literature finding]`:

> Phenomenology is not naive introspection (the unmediated project of looking inward at one's mental states). Husserl introduces the phenomenological reduction (epoché) as a methodological commitment — bracketing existential claims, focusing on how-of-givenness — that distinguishes phenomenology from psychological introspection. The majority scholarly reading (Zahavi, Smith and Thomasson) treats phenomenology and introspection as categorically distinct; a minority refining reading (Tewes 2018) treats phenomenology as systematically-refined introspection rather than its opposite. For introductory pedagogical purposes, the categorically-distinct reading is sufficient; advanced learners should be exposed to the scholarly debate. Primary sources: Husserl 1900-1901 (Logical Investigations — initial "descriptive psychology" framing, later regretted), 1913 (Ideas I — introduces epoché), 1931 (Cartesian Meditations — methodological codification).

### 5.6 Feedback to Session δ

**D6 (Cluster 5 `unlearning_required_before` endpoint) — F4 supplies adjacent input.** Whether the misconception node `phenomenology_is_introspection` points at the `phenomenology` concept (the broad reading) or at a more specific learning-task ("master the phenomenological reduction") affects how the remediation_note operates. F4's nuance (naive vs refined introspection) suggests the misconception's TARGET should be "phenomenology-as-naive-introspection" specifically, not "phenomenology" simpliciter — pointing at a more granular learning-task or sub-concept rather than the field-name node.

**D7 (Cluster 5 seed-orphaned misconception handling) — F4 is the one of three seeds with a non-orphan target.** Phenomenology IS a node in the graph (§5.5.A); the misconception encoding can proceed regardless of which of D7's two options Session δ chooses. F4's depth supports the lightweight-encoding-fits-cleanly finding from `kant_walkthrough.md` §5.2.2.A.

**Recommendation for the Session δ ADR Decision section:** name the F4-derived nuance — the misconception is about NAIVE introspection specifically — in the remediation_note authoring discipline. Don't allow the simpler "phenomenology ≠ introspection" framing to land without the methodological qualification.

### 5.7 Carry-forward / open questions

- **Q1-F4.** Should Tewes 2018 (or its successors) be added to the canonical_sources for the `phenomenology` node? The dissenting view is part of the scholarly conversation; including only the majority reading produces an incomplete `canonical_sources` field for advanced learners. Session δ-or-later canonical-source-authoring pass.
- **Q2-F4.** The Frontiers article framing — "Husserl's method IS a kind of introspection, refined" — suggests a downstream-learner question: at what point in a phenomenology course does the refined-introspection nuance get introduced? This is a teaching-task design question (Cluster 11 / 12) rather than a Cluster 4/5 schema question.
- **Q3-F4.** What is the status of the analogous question for the OTHER two seeded misconceptions (deconstruction = anything goes; historical perspective = sympathy with the past)? F4's pattern (majority view + refining minority) may recur — the deconstruction misconception in particular has a substantial Derridean defence literature suggesting the "anything goes" reading is more nuanced than a simple correction. F4's framework (categorically-distinct vs refined) might apply broadly.

---

## 6. (Bonus — context-budget-permitting) §F5 — Falmagne knowledge spaces

Per [`extraction_paper_1.md` L293](extraction_paper_1.md#L293), Falmagne et al. on knowledge spaces is named in the canonical foundational-reading list but does not appear in `kant_walkthrough.md` §6.6's F1-F4. Brief literature check `[model-knowledge]`:

**Falmagne, J.-C., Doignon, J.-P., et al.** developed knowledge space theory in the 1980s-1990s. The framework formalizes the prerequisite structure of a domain as a knowledge space — a collection of feasible knowledge states (subsets of items a learner could plausibly know). Key constructs: knowledge state, knowledge structure, learning paths (chains of inclusion between knowledge states), surmise relations (item A is a prerequisite for item B).

The framework underpins ALEKS (Assessment and LEarning in Knowledge Spaces) — a commercial adaptive-learning product that empirically refines prerequisite structures from learner-trace data.

**Relevance to Paideia** (per Session α's [`adr_cross_reference_map.md`](adr_cross_reference_map.md) Cluster 1 + Cluster 12):

- Knowledge spaces formalize what Paideia's `pedagogical_prerequisite` edges informally encode. The empirical-refinement-from-trace-data mechanism is exactly what `paper_1:L132` names: "making prerequisite assumptions explicit enables testing, revision, and adaptive use."
- The `trace_confidence` field design (Cluster 1) bears on the knowledge-space framework's central claim — that expert elicitation is a starting point, not a final verdict.
- Phase 7+ adaptive routing (Cluster 11) could borrow the surmise-relation formalism for principled multi-path navigation through the graph.

**Not a direct contribution to F1-F4.** F5 is a forward-pointer for Session δ-or-later canonical-source authoring (`canonical_sources` field for prerequisite-typed edges). No further authoring this session.

---

## 7. Findings synthesis

### 7.1 Cross-F observations

- **All four F-items reinforce the §6.7 D2 question (single-valued vs multi-valued `node_type`).** F1 (multi-typing for phenomenology), F2 (`bridge_concept` as coinage that may be admitted alongside other types), F3 (bottleneck-vs-threshold subset relation), F4 (misconception target granularity) jointly push toward either array-valued `node_type` OR explicit secondary-type fields. Single-valued enum without further accommodation is the position least supported by the literature.
- **F2 and F3 share a "literature evolves; schema must too" pattern.** F2's `bridge_concept` and F3's `bottleneck` are both cases where the synthesis paper's enum-as-authored doesn't quite match the literature's settled vocabulary. The D8 procedure (per-layer enums as open-for-revision lists with explicit revision procedures) is empirically warranted by both findings.
- **F1 and F4 share a "majority reading + nuance" pattern.** Both have a defensible primary framing (F1: threshold concepts are concepts/practices, not movements; F4: phenomenology is not introspection) AND a refining nuance (F1: the literature broadens to "ways of thinking and practising"; F4: refined-introspection minority reading). The schema and remediation-note authoring should preserve the nuance rather than collapse to the simpler framing.
- **F3 surfaces an unmodeled dimension: emotional bottlenecks.** Paper_1 / paper_2 / synthesis.md do not address emotional bottlenecks; the Decoding-the-Disciplines literature does. Session δ should decide explicitly whether to admit this dimension OR document the deliberate exclusion.
- **No F-item resolved its underlying §6.7 D-item; all four supply EVIDENCE for the D-items.** This is the intended Session γ output shape — Session γ supplies literature evidence; Session δ adjudicates.

### 7.2 Per-D-item bearing summary

| D-item | F1 | F2 | F3 | F4 |
|---|---|---|---|---|
| D1 (historical_context ADR 0008) | adjacent (motivates) | — | — | — |
| D2 (single vs multi-valued node_type) | direct | direct | adjacent | adjacent (target-granularity) |
| D3 (subfield / discipline_area gap) | — | — | adjacent (enum expansion) | — |
| D4 (tradition_label cardinality) | — | — | — | — |
| D5 (Layer-2 sub-type extensions) | — | — | — | — |
| D6 (unlearning_required_before endpoint) | — | — | — | direct |
| D7 (seed-orphaned misconception handling) | — | — | — | adjacent (F4 is the non-orphan seed) |
| D8 (per-layer enums as open-for-revision) | adjacent | direct | direct | — |

### 7.3 Two recommendations Session δ should weigh

Authored as recommendations FOR consideration, not as decisions:

- **Adopt multi-valued `node_type` (array form) in the Cluster 4 migration.** F1 + F2 + F3 + F4 jointly demonstrate the data carries multi-type semantic content. Single-valued enum with secondary-tag workarounds is feasible but loses the clarity that array-form provides. The literature's silence on schema-form for downstream PDG implementations means this is a Paideia-side design choice with literature evidence supporting expressiveness over single-typing.
- **Treat the `node_type` enum as open-for-revision per D8, with the first revision authored alongside the migration itself.** F2 (`bridge_concept` as coinage) and F3 (`bottleneck` as omitted) are already two suggested revisions before the migration even lands. The D8 procedure should be operational from migration day 1, not a future commitment.

---

## 8. Session γ disposition

### 8.1 Outputs

Per the empirical-validation posture stated in §1:

- **F1 answered** (§2): five-characteristics framework attested; movement-vs-method distinction supported by the literature's example pattern; recommendation for the phenomenology node split or multi-type.
- **F2 answered** (§3): `bridge_concept` is a synthesis-paper coinage, not literature-grounded as a distinct CFT category; three readings provided for Session δ.
- **F3 answered** (§4): bottleneck-vs-threshold is a subset relationship (every threshold is a bottleneck); cognitive-vs-emotional bipartition is well-attested; four readings provided for whether to add bottleneck-related enum values.
- **F4 answered** (§5): majority reading supports §5.2.1 framing; minority refining reading (Tewes 2018) provides nuance; recommended `remediation_note` text drafted.
- **Bonus §F5** (§6): brief Falmagne knowledge-spaces context for Session δ-or-later canonical-source authoring.
- **Per-D-item bearing summary** (§7.2): cross-reference table.
- **Two D-item recommendations** (§7.3): multi-valued node_type; D8 procedure operational on day 1.

### 8.2 Non-outputs (explicit no's)

- **No Issues filed.** Per HANDOFF quality-first posture; Issues fire only after Session ζ revision pass.
- **No ADRs drafted.** Session δ drafts; Session γ supplies literature evidence.
- **No decisions settled.** All adjudication is deferred to Session δ; Session γ's findings supply evidence, not verdicts.
- **No migrations authored.** Cluster 4/5 migrations land after Session δ adjudicates.
- **No re-typing of existing edges or nodes.** Session β disposition holds.
- **No canonical-sources backfill on existing nodes.** Q1-F4 (add Tewes 2018 to `phenomenology` node's canonical_sources) is flagged for Session δ-or-later, not actioned.

### 8.3 Cross-references

- Plan file: [`~/.claude/plans/radiant-jumping-peach.md`](~/.claude/plans/radiant-jumping-peach.md)
- Session α deliverable: [`adr_cross_reference_map.md`](adr_cross_reference_map.md) — particularly C4 / C5 / C8 sections.
- Session β deliverable: [`kant_walkthrough.md`](kant_walkthrough.md) — particularly §3.2.1 / §3.4.1 / §5.2.1 / §6.6 / §6.7.
- Synthesis: [`synthesis.md`](synthesis.md) — Clusters 2, 4, 5, 6, 8.
- Source papers: [`extraction_paper_1.md`](extraction_paper_1.md) (L293 reading list; L301 Zahavi SEP pointer); [`extraction_paper_2.md`](extraction_paper_2.md).
- Voice precedent: [`engine/build_readiness/phase_4_graph_validation.md`](../phase_4_graph_validation.md).
- Primary literature pointers (not directly accessed this session):
  - Meyer, J.H.F. & Land, R. (2003), (2005); Land et al. (2005); Meyer, Land & Baillie eds. (2010) *Threshold Concepts and Transformational Learning*.
  - Middendorf, J. & Pace, D. (2004); Pace, D. (2017).
  - Spiro, R.J., Feltovich, P.J., et al. (1988, 1991/1992); Jacobson & Spiro (1995).
  - Husserl, E. (1900-1901, 1913, 1931); Zahavi, D. *Husserl's Phenomenology* (2003) and SEP entry; Tewes (2018) [Frontiers in Psychology].
  - Falmagne, J.-C., Doignon, J.-P., et al. (1980s-1990s knowledge-space theory).
- Secondary sources accessed this session (full URLs):
  - https://www.facultyfocus.com/articles/teaching-and-learning/threshold-concepts-portals-new-ways-thinking/
  - https://en.wikipedia.org/wiki/Threshold_knowledge
  - https://www.sciencedirect.com/topics/psychology/cognitive-flexibility-theory
  - https://www.instructionaldesign.org/theories/cognitive-flexibility/
  - https://cndls.georgetown.edu/resources/bottlenecks-and-thresholds/
  - https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2018.00896/full
  - https://plato.stanford.edu/entries/husserl/

### 8.4 Pre-phase progress (per HANDOFF.md PDG entry)

- ✅ Session α (S-0199) — cross-reference audit complete; [`adr_cross_reference_map.md`](adr_cross_reference_map.md) authored.
- ✅ Session β (S-0200) — Kant/phenomenology walkthrough complete; [`kant_walkthrough.md`](kant_walkthrough.md) authored.
- ✅ Session γ (S-0201) — Foundational reading complete; **this document.** Specific carry-forward items per §7 + per-F §X.7 sections.
- ⏳ Session δ — Four foundational ADRs. **Eight adjudication items (D1-D8) from kant_walkthrough.md §6.7 + per-F D-item bearings from this document §7.2.**
- ⏳ Session ε — Adversarial residue adjudication (19 deferred findings from Session α, not modified by Sessions β or γ).
- ⏳ Session ζ — Synthesis revision + Issue-draft revision. Issues fire only after Session ζ.
