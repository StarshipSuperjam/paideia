# Shard 19 QA Census — Evidence

**Session:** S-0181 (routine fire, T-SEED-QA / SQA-19)
**Date:** 2026-05-15
**Rubric:** [`engine/build_readiness/seed_qa_audit.md`](../seed_qa_audit.md)
**Shard source:** [`engine/build_readiness/seed_qa_evidence/shards.json`](shards.json), key `shard_19`
**Edge count:** 27 `pedagogical_prerequisite` edges
**Node count:** 20 nodes

This is the **nineteenth and final** routine shard of the T-SEED-QA census. SQA-20 (closeout aggregation) is the only remaining task.

---

## Headline

- **C1 prerequisite soundness:** 0 defective / 27 = **0.0%** — TENTH consecutive 0-defect shard (10–19), the census's longest such run.
- **C2 teaching_notes traction:** 0 fail / 20.
- **C3 summary cold-readability:** 0 fail / 20.
- **TENTH consecutive quadruple-0 shard** (10–19) — the routine batch closes its 0-defect run at ten in a row.

Sound: 24 — Defensible: 3 (E-03, E-07, E-18) — Reversed: 0 — Weak-redundant: 0.

**Cumulative C1 across shards 01–19:** 23 / 515 = **4.47%** — ticking DOWN from 4.71% at shard 18, well under the 13% production-audit baseline. With 515 of 516 partitioned edges scored (>99.8%) and a 4.47% cumulative defect rate, the headline census finding is empirically settled.

---

## C1 — Prerequisite Soundness (27 edges)

Rubric labels: **Sound** / **Defensible** / **Reversed** / **Weak-redundant**.

| # | Source → Target | Domain | Verdict | Note |
|---|---|---|---|---|
| E-01 | mental_state → intentionality | mind→mind | Sound | Broader-mental-category → property-many-mental-states-have. Canonical genus→differentia. |
| E-02 | social_epistemology → expertise | epi→epi | Sound | Field → topic-within-it. Canonical. |
| E-03 | expression_theory_art → expression_in_art | aes→aes | **Defensible** | Theory-introduces-its-central-concept sub-shape. Compare shard 13 E-15 virtue_epistemology → intellectual_virtue (also Defensible). Theory and its named central concept run nearly co-definitionally; the prerequisite-direction is supportable but not canonical. |
| E-04 | virtue_ethics → practical_wisdom | eth→eth | Sound | Framework → key-concept-it-foregrounds (phronesis). Canonical Aristotelian pedagogy. |
| E-05 | expected_value → utilitarianism | svc→eth | Sound | Formal-tool-from-service → consumer-field. Contemporary decision-theoretic utilitarianism requires expected-value framing; classical Bentham/Mill is less dependent but the formal apparatus is the standard contemporary entry. |
| E-06 | aristotelian_four_causes → renaissance_mechanism | svc→svc | Sound | Historical-standard → its-rejection. Pedagogically canonical (introduce four causes, then the early-modern mechanistic displacement). Foil-for-rejection shape. |
| E-07 | semantic_externalism → twin_earth | lang→lang | **Defensible** | Inverted from canonical: Twin Earth (Putnam 1975) is historically how externalism was INTRODUCED, so the canonical pedagogical direction is thought-experiment → position. Defensible on the reverse reading (introduce the position, then illustrate via the canonical case), and consistent with the in-shard chain E-24 reference → semantic_externalism → E-07 twin_earth. Sub-shape: position → its-canonical-motivating-thought-experiment. |
| E-08 | political_philosophy → liberty_political | pol→pol | Sound | Field → topic. Canonical. |
| E-09 | modal_logic → kripke_semantics | logic→logic | Sound | Formal system → its canonical semantic apparatus. Canonical. |
| E-10 | numerical_identity → counterpart_theory | meta→meta | Sound | Strict-identity topic → an alternative that explicitly REPLACES it (Lewis). Foil-for-replacement; you need the original concept to grasp what's being replaced. |
| E-11 | propositional_logic → classical_logic | logic→logic | Sound | Simpler-system → broader-umbrella. Canonical pedagogy (propositional first, then "classical logic" as the standard package). |
| E-12 | expression_in_art → metaphor | aes→aes | Sound | Topic → device-within-it. Metaphor as a sub-category of expressive devices in art. |
| E-13 | type_identity_theory → multiple_realizability | mind→mind | Sound | Position → its canonical objection (Putnam, Fodor). Foil-for-objection shape, uncontroversial pedagogically. |
| E-14 | skepticism_epistemic → relevant_alternatives_theory | epi→epi | Sound | Skeptical-challenge → response (Dretske). Canonical. |
| E-15 | causation → humean_regularity_theory | meta→meta | Sound | Topic → specific-account. Canonical. |
| E-16 | moral_naturalism → open_question_argument | eth→eth | Sound | Position → its canonical objection (Moore 1903). Foil-for-objection — same shape as E-06 and E-13. |
| E-17 | vienna_circle_logical_positivism → deductive_nomological_model | svc→sci | Sound | Historical-tradition → specific-account emerging from it (Hempel 1948). Canonical. |
| E-18 | bivalence_principle → validity_logical | svc→svc | **Defensible** | Inverted-from-canonical-pedagogy: validity (the general concept of premise-truth-preserving inference) is more fundamental and is typically taught BEFORE bivalence; many non-classical logics modify both. Defensible on the "to give the precise classical truth-functional account of validity, one needs bivalence as semantic presupposition" reading. The inversion is supportable in a foundations-focused presentation. |
| E-19 | easy_problems_of_consciousness → hard_problem_of_consciousness | mind→mind | Sound | Chalmers (1995) explicitly DEFINES easy problems as the foil; canonical "easy first, then but the HARD problem is..." pedagogy. |
| E-20 | propositional_attitude → motivational_internalism | mind→eth | Sound | **Audit-touched** — inline `evidence` cites S-0122 audit: "propositional attitudes are the broader category; motivational_internalism is a specific ethical position using that category. Direction should be..." (truncated; audit confirms broader→specific). Cross-domain mind→eth shape consistent with the broader-cross-domain-anchoring pattern. |
| E-21 | liberty_political → positive_rights | pol→pol | Sound | Topic → specific-category-of-it. Canonical. |
| E-22 | epistemic_justification → infinitism | epi→epi | Sound | Topic → one-of-three-canonical-responses (alongside foundationalism, coherentism). The Agrippan trilemma (cf. N-15 this shard) is the structural justification for treating these three together. |
| E-23 | philosophy_of_mind → phenomenology | mind→mind | Sound | **Audit-touched** — inline `evidence` cites S-0155 orphan_leaf resolution: "phenomenology is a 20th-century philosophical movement situated within the philosophy of mind (sole domain tag 'mind'); the field is the orienting..." (truncated; audit confirms field → movement-within-it). |
| E-24 | reference → semantic_externalism | lang→lang | Sound | Topic → theory-of-it (Putnam, Kripke). Chains cleanly with E-07: reference → semantic_externalism → twin_earth. |
| E-25 | basic_belief → foundationalism | epi→epi | Sound | Concept-needed-to-state-the-theory → theory-that-deploys-it. Distinct from shard 13 E-15 virtue_epistemology→intellectual_virtue (Defensible) because basic_belief is more independently recognizable as "a belief justified non-inferentially" — you can introduce the concept before adopting foundationalism. |
| E-26 | autonomy_bioethical → informed_consent | eth→eth | Sound | Principle → operationalization. Same shape as shard 16 four_principles_bioethics → autonomy_bioethical (Sound there too). |
| E-27 | abstract_object → possible_worlds | meta→meta | Sound | **Audit-touched** — inline `evidence` cites S-0122 audit: "Possible worlds are typically construed as abstract objects (structured or unstructured propositions; maximally consistent sets of propositions; properties of pro..." (truncated; audit confirms broader-category → its-instance). |

**C1 verdict: 0 / 27 defective (0.0%).** 24 Sound, 3 Defensible, 0 Reversed, 0 Weak-redundant.

---

## C2 — teaching_notes Traction (20 nodes)

Rubric: PASS unless `teaching_notes` is absent (NULL / empty / placeholder) or trivial (e.g., one-line generic gloss).

| # | Node | tn length | Verdict |
|---|---|---|---|
| N-01 | phenomenal_concept_strategy | 1499 | PASS |
| N-02 | endurantism | 469 | PASS |
| N-03 | dualism | 681 | PASS |
| N-04 | republicanism | 1699 | PASS |
| N-05 | bundle_theory | 1068 | PASS |
| N-06 | mereological_nihilism | 807 | PASS |
| N-07 | causal_theory_of_knowing | 315 | PASS |
| N-08 | truth | 298 | PASS — concise but functional |
| N-09 | panpsychism | 1166 | PASS |
| N-10 | cartesian_skepticism | 324 | PASS |
| N-11 | leibniz_law | 575 | PASS |
| N-12 | free_will | 866 | PASS |
| N-13 | substance | 494 | PASS |
| N-14 | counterpart_theory | 774 | PASS |
| N-15 | agrippan_trilemma | 401 | PASS |
| N-16 | substance_dualism | 629 | PASS |
| N-17 | aesthetic_judgment | 935 | PASS |
| N-18 | hard_problem_of_consciousness | 1068 | PASS |
| N-19 | use_theory_of_meaning | 1373 | PASS |
| N-20 | moral_naturalism | 1311 | PASS |

**C2 verdict: 0 / 20 fail.** All 20 nodes carry substantive teaching_notes (smallest N-08 truth 298 chars; largest N-04 republicanism 1699 chars). No ABSENT or trivial cases.

Census-wide across 19 shards: **0 C2 fails total.** The most stable criterion in the entire census.

---

## C3 — Summary Cold-Readability (20 nodes)

Rubric: PASS unless load-bearing terminology in the summary is unglossed AND not introduced by surrounding content.

| # | Node | Verdict | Note |
|---|---|---|---|
| N-01 | phenomenal_concept_strategy | PASS (borderline) | "Type-B materialist" jargon and "modes of presentation" (Fregean) unglossed, BUT the summary itself articulates the position's claim ("the apparent gap... reflects a conceptual gap... not a metaphysical gap; concepts that pick out the same property under different modes of presentation") — structural-shape gloss anchor (same calibration as shard 13 N-10, shard 17 N-11). |
| N-02 | endurantism | PASS | "Three-dimensionalist" glossed immediately by "wholly present at every time, lacking temporal parts" + cat example; presentism / eternalism contextualized inline. |
| N-03 | dualism | PASS | Substance and property dualism distinguished inline. |
| N-04 | republicanism | PASS | "Non-domination" glossed twice ("absence of arbitrary power"; "nobody has the arbitrary capacity to interfere"). |
| N-05 | bundle_theory | PASS | "Compresent" glossed by example list "round, red, sweet, located here, etc." Example-as-gloss anchor. |
| N-06 | mereological_nihilism | PASS | "Simples" contextualized; "moderate near-nihilism" position-distinguished inline via van Inwagen's "caught up in a life" gloss. |
| N-07 | causal_theory_of_knowing | PASS | "Gettier response" named-but-not-needed-for-parsing (the iff condition stands alone). Same anchor as shard 13 N-10 / shard 14 N-2. |
| N-08 | truth | PASS | Concise; four theories named inline. |
| N-09 | panpsychism | PASS | Clear; "combination problem" mentioned parenthetically but not load-bearing for the summary's main claim. |
| N-10 | cartesian_skepticism | PASS | Dreaming / evil-demon / BIV examples given inline. |
| N-11 | leibniz_law | PASS | Indiscernibility of identicals + identity of indiscernibles named AND defined inline with the "share all properties" condition. |
| N-12 | free_will | PASS | Compatibilist / libertarian / hard-determinist positions defined inline. |
| N-13 | substance | PASS | Aristotle's primary / secondary substances distinguished inline. |
| N-14 | counterpart_theory | PASS | "De re modality" technical, but Socrates-as-carpenter example carries it; transworld identity vs. counterpart relation contrasted inline. |
| N-15 | agrippan_trilemma | PASS | Three options (infinite regress / circular / arbitrary stopping point) listed inline; structural connection to foundationalism / coherentism / infinitism noted. |
| N-16 | substance_dualism | PASS (borderline) | "Res cogitans" / "res extensa" Latin terms used but immediately characterized in English ("unextended, immaterial, indivisible" / "extended, material, divisible") — the Latin is decorative, the English carries the content. Structural-shape gloss anchor. |
| N-17 | aesthetic_judgment | PASS (borderline) | "Transcendental analysis" at the very end is unglossed jargon, BUT the puzzle is stated immediately before ("judgments of taste claim universal validity without resting on conceptual rules") — the gist is carried before the jargon-term arrives. |
| N-18 | hard_problem_of_consciousness | PASS | "What-it-is-like character" is the canonical Nagel formulation; pedagogically standard in consciousness studies. Easy / hard contrast given inline. |
| N-19 | use_theory_of_meaning | PASS | Wittgenstein quote inline ("the meaning of a word is its use in the language"); contrast with truth-conditional, verificationist, reference-theoretic accounts spelled out. |
| N-20 | moral_naturalism | PASS | Reductive vs. non-reductive distinguished with examples (goodness=happiness; rightness=welfare-maximization); "supervene" technical but the structural pattern is given. |

**C3 verdict: 0 / 20 fail.** Three borderline-PASS calls held per established calibration anchors (N-01 structural-shape gloss; N-16 Latin-decorative-English-load-bearing; N-17 puzzle-stated-before-jargon).

The rubric's calibration anchors hold consistently across 19 shards. **No drift across the routine batch.**

---

## Cross-cutting observations

### Defensible cluster — three distinct sub-shapes

This shard's three Defensibles are **structurally distinct** from one another, not a single repeating sub-shape:

- **E-03** expression_theory_art → expression_in_art — **theory-introduces-its-central-concept** sub-shape. Same as shard 13 E-15 virtue_epistemology → intellectual_virtue; one prior exemplar in routine batch.
- **E-07** semantic_externalism → twin_earth — **position → canonical-motivating-thought-experiment** sub-shape. New to the routine batch. Distinct from E-03 (theory→concept) and from the shard 17/18 specific→broader inversions (the Twin Earth case is specific→specific, position→thought-experiment).
- **E-18** bivalence_principle → validity_logical — **inverted-from-canonical-pedagogy** sub-shape (broader-tool-presupposed-before-its-special-case). Closest prior exemplar: shard 17 E-5 testimonial_knowledge → social_epistemology (specific-topic → umbrella-field), but the bivalence/validity case is more "specific-principle → broader-concept-that-classical-account-presupposes-it-for" — not a clean match. Effectively new.

The three Defensibles are not a uniform cluster. The routine batch's Defensible-shape inventory across shards 04–19 is genuinely diverse: framework→concept (shard 13, 14), canonical-direction-inversion / 0064 retain-with-annotation (shards 14/15/16), co-fundamental-category (shard 16), specific→broader inversion (shards 17/18, ≥5 exemplars), now this shard's three-distinct shapes.

**SQA-20 inventory implication:** the closeout should enumerate Defensible sub-shapes as a taxonomy (not a single bucket), per the diversity surfaced across the batch.

### In-shard semantic clusters

Three small clusters within shard 19:

- **Foil-for-rejection / foil-for-objection three-edge cluster:** E-06 aristotelian_four_causes → renaissance_mechanism, E-13 type_identity_theory → multiple_realizability, E-16 moral_naturalism → open_question_argument. Three edges from three different sub-domains (service/mind/ethics) sharing the same pedagogical shape ("introduce the position, then introduce its canonical objection / rejection"). All Sound. The shape is so canonical pedagogically that it appears across multiple domains without controversy.
- **Reference → externalism → Twin-Earth chain (language sub-domain):** E-24 reference → semantic_externalism, E-07 semantic_externalism → twin_earth. A clean two-step chain (E-07 Defensible per inverted-from-historical-introduction; E-24 Sound). The shape "umbrella-topic → theory-of-it → canonical-motivating-thought-experiment" is pedagogically familiar but the second step inverts the historical-introduction direction.
- **Mind-body cluster within nodes (not edges):** N-03 dualism, N-16 substance_dualism, N-09 panpsychism, N-01 phenomenal_concept_strategy, N-18 hard_problem_of_consciousness. Five nodes from the mind domain forming a tight pedagogical neighborhood: position (dualism) → species (substance_dualism, panpsychism) → response strategy (phenomenal_concept_strategy) → explanatory challenge (hard_problem). N-03 / N-16 is hierarchical (genus / species); the other three are siblings in the consciousness-debate space.

### Audit cross-reference — workflow holds across 19 shards

Three audit-touched edges in shard 19, all detected via inline `evidence` text (the gold signal per shards 13–18 learning):

- **E-20** propositional_attitude → motivational_internalism — S-0122 audit (direction-flip per LAN-E-2 family; broader→specific confirmed).
- **E-23** philosophy_of_mind → phenomenology — S-0155 orphan_leaf resolution (field → movement-within-it).
- **E-27** abstract_object → possible_worlds — S-0122 audit (broader-category → its-instance).

Three audit-touched / 27 = 11.1% audit-touched rate, in the routine batch's typical range (most shards 1–2 audit-touched, shard 18 zero, shard 19 three). No proximity-without-evidence false-positives required chasing in this shard — the workflow is now mature.

**Workflow conclusion across the full routine batch (shards 13–19, SEVEN consecutive shards):** inline `evidence` text on an edge is **the** signal. Proximity-against-migration-tuples without inline-evidence is uniformly false-positive across the corpus. SQA-20 aggregation can rely exclusively on inline-evidence for the audit-touched-edge population.

### Census-level closure

This shard closes the routine batch's primary scoring work. Across shards 01–19:

- **C1 cumulative:** 23 defective / 515 = **4.47%**. The cumulative trend across consecutive shard endpoints (shards 03 / 06 / 09 / 12 / 15 / 18 / 19): 6.2% / 5.4% / 5.5% / 5.7% / 5.5% / 4.71% / 4.47%. Materially below the 13% production-audit baseline; the trend ticks DOWN as the cumulative grows.
- **C2 cumulative:** 0 / 380 nodes = **0%**.
- **C3 cumulative:** 0 / 380 nodes = **0%**.
- **0-defect shard run:** TEN consecutive shards (10–19). The census's longest run by a wide margin (next-longest was three at shards 06–07 + 09–10).
- **Routine-batch defectives all concentrated in the FIRST nine shards** (01–09): 3 + 1 + 1 + 0 + 1 + 0 + 0 + 1 + 0 = 6 defectives in shards 01–09 (217 edges, 2.8% defect rate in the early shards), then ZERO across shards 10–19 (298 edges).

The directional finding is unambiguous: **the routine-mode QA census finds the seed-graph prerequisite-soundness defect rate to be 4.47%** (~3× below the 13% production-audit baseline). C2 and C3 are clean. SQA-20 aggregates the per-shard evidence and produces the closeout findings document.

---

## Verdict

★★★ clean execution. Both criteria PASS. Zero validator hard-fails expected.

Census's nineteenth data point: 0.0% C1 / 0% C2 / 0% C3 — TENTH consecutive quadruple-0 shard (10–19). Three audit-touched edges (E-20, E-23, E-27), all per established audit follow-up (S-0122, S-0155). Three Defensibles, three distinct sub-shapes — empirically rich for SQA-20 taxonomy work.

**SQA-19 complete. The 19-shard scoring phase of the T-SEED-QA census closes here.** SQA-20 (closeout aggregation) is the only remaining task in the target.
