# Seed-graph QA census — closeout findings

> Authored by S-0182 (routine fire, T-SEED-QA / SQA-20) per the rubric and mandate at [`seed_qa_audit.md`](seed_qa_audit.md) ("Closeout (SQA-20)"). Class-3 audit closeout report. Aggregates the 19 per-shard evidence files at [`seed_qa_evidence/shard_NN.md`](seed_qa_evidence/) into a single overall view: per-criterion rates, per-subdomain breakdown, C1 drift comparison vs the production audit's 13% baseline, pattern clusters, and Phase 6 self-correction implications.
>
> **Anti-scope.** Aggregation only. No Issue filing, no ADR drafts, no migration corrections, no validator soft-warn proposals. Disposition is a follow-up interactive session's responsibility, matching the production audit's anti-scope.
>
> **Numbers in this report are computed from the per-shard tally tables and verdict lines in the 19 evidence files, which are the authoritative source.** Running-cumulative percentages narrated inline in late-batch shard evidence files (e.g., the "4.47% cumulative" claim in `shard_19.md`) carry arithmetic drift across sessions and are not reproduced here; the closeout recomputes from the per-shard primary data.

## 1. Population

Per the pinned sharding at [`seed_qa_evidence/shards.json`](seed_qa_evidence/shards.json), generated once at S-0156 by [`engine/tools/seed_qa_shard.py`](../tools/seed_qa_shard.py):

| Population | Count | Notes |
|---|---|---|
| `pedagogical_prerequisite` edges | **516** | Full census. The 17 `historical_influence` edges in the graph are out of scope per the rubric. |
| Nodes | **380** | All `status = active`. |
| Shards | 19 | Shards 01–03 carry 28 edges each; shards 04–19 carry 27 edges each. Every shard carries 20 nodes. |
| Cross-domain edges | 55 (10.7%) | Per the primary-domain-tag tally of `shards.json`. |
| Within-domain edges | 461 (89.3%) | |

The two methodology re-audits at [`shard_01_reaudit.md`](seed_qa_evidence/shard_01_reaudit.md) and [`shard_04_reaudit.md`](seed_qa_evidence/shard_04_reaudit.md) (S-0165, interactive build) rescored shards 01 and 04 with mandatory SEP anchoring per [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md). **Both re-audits AGREE with their originals on every C1, C2, and C3 verdict.** The originals' tallies stand; the closeout treats the re-audits as a methodology validation pass (the routine parametric-first rubric is producing the same verdicts as the SEP-anchored adversarial pass on a 2-shard / 55-edge / 40-node sample).

## 2. Headline rates

### C1 — prerequisite soundness (edges)

| Verdict | Count | % of edges |
|---|---|---|
| Sound | 461 | 89.3% |
| Defensible | 48 | 9.3% |
| **Reversed** | **7** | **1.36%** |
| **Weak-redundant** | **0** | **0.0%** |
| **Defect (Reversed + Weak-redundant)** | **7** | **1.36%** |

### C2 — `teaching_notes` traction (nodes)

| Verdict | Count | % of nodes |
|---|---|---|
| PASS | 380 | 100.0% |
| **FAIL** | **0** | **0.0%** |
| `teaching_notes` ABSENT | 0 | 0.0% |

Every one of the 380 nodes carries substantive `teaching_notes`. The shortest observed is 280 chars (shard 18 N-17 infinitism); the longest exceeds 3000 chars. No NULL / empty / placeholder cases; no trivial-restate-the-summary cases that scored FAIL on the rubric. C2 is the census's most stable criterion.

### C3 — summary cold-readability (nodes)

| Verdict | Count | % of nodes |
|---|---|---|
| PASS | 367 | 96.6% |
| **FAIL** | **13** | **3.4%** |

The 13 C3 fails concentrate by domain (see §4); the pattern is uniformly "load-bearing first sentence gated on undefined formal-apparatus vocabulary" — modal-logic notation, deontic-logic acronyms, Bayes-theorem formulas, Kantian framework terms (see §5.3).

## 3. Per-shard rates

| Shard | Edges | Reversed | Weak-red. | Defective | Def. % | C2 fail | C3 fail | Defensible |
|---|---|---|---|---|---|---|---|---|
| 01 | 28 | 3 | 0 | 3 | 10.7% | 0 | 2 | 4 |
| 02 | 28 | 1 | 0 | 1 | 3.6% | 0 | 0 | 3 |
| 03 | 28 | 1 | 0 | 1 | 3.6% | 0 | 0 | 1 |
| 04 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 1 |
| 05 | 27 | 1 | 0 | 1 | 3.7% | 0 | 1 | 4 |
| 06 | 27 | 0 | 0 | 0 | 0.0% | 0 | 1 | 6 |
| 07 | 27 | 0 | 0 | 0 | 0.0% | 0 | 1 | 3 |
| 08 | 27 | 1 | 0 | 1 | 3.7% | 0 | 2 | 1 |
| 09 | 27 | 0 | 0 | 0 | 0.0% | 0 | 5 | 2 |
| 10 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 2 |
| 11 | 27 | 0 | 0 | 0 | 0.0% | 0 | 1 | 4 |
| 12 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 3 |
| 13 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 1 |
| 14 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 2 |
| 15 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 2 |
| 16 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 1 |
| 17 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 2 |
| 18 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 3 |
| 19 | 27 | 0 | 0 | 0 | 0.0% | 0 | 0 | 3 |
| **Total** | **516** | **7** | **0** | **7** | **1.36%** | **0** | **13** | **48** |

**Concentration.** All 7 C1 defectives sit in shards 01–08 (early routine batch). Shards 09–19 carried zero C1 defectives across 297 edges — eleven consecutive zero-C1-defect shards, the census's longest such run. Shard 01 alone carries 3 of the 7 Reversed verdicts (42.9%) and 2 of the 13 C3 fails (15.4%); it is the standing outlier of the routine batch.

C3 fails distribute differently: 11 of 13 sit in shards 05–09 (a denser early-mid-batch cluster), with one in shard 01 and one in shard 11. No C3 fail appears in shards 12–19 (eight consecutive zero-C3-fail shards).

## 4. Per-subdomain breakdown

### 4.1 Edge-source domain — C1

| Source domain | Edges scored | Reversed | C1 defect rate | Notes |
|---|---|---|---|---|
| mind | 76 | 3 | 3.95% | shard 01 E-5 (phenomenal_concept_strategy → type_b_materialism); shard 05 E-7 (property_dualism → philosophical_zombie); shard 08 E-4 (computational_theory_of_mind → turing_test) |
| service | 55 | 1 | 1.82% | shard 01 E-24 (set_mathematical → axiom_mathematical) |
| epistemology | 79 | 1 | 1.27% | shard 01 E-26 (knowledge_how → knowledge) |
| ethics | 69 | 1 | 1.45% | shard 02 E-15 (utilitarianism → hedonism) |
| metaphysics | 71 | 1 | 1.41% | shard 03 E-14 (perdurantism → temporal_parts) |
| language | 32 | 0 | 0.0% | — |
| logic | 37 | 0 | 0.0% | — |
| political | 35 | 0 | 0.0% | — |
| aesthetics | 32 | 0 | 0.0% | — |
| science | 30 | 0 | 0.0% | — |
| **All** | **516** | **7** | **1.36%** | |

**Structural observation.** Every one of the 7 Reversed edges is **within-domain** (source domain = target domain). The 55 cross-domain edges (10.7% of the population) carried zero defectives. The pre-census production audit had explicitly fortified the cross-bridges with a separate adversarial pass (audit subdomain AUDIT-CB scored 35.2% defective at the production audit; the follow-up migrations 0061–0065 fixed those), and the census's clean cross-domain finding empirically confirms that fortification holds at the post-fix graph.

### 4.2 Node-domain — C3

| Node domain | Nodes scored | C3 fails | C3 fail rate | Failing nodes (jargon-gate) |
|---|---|---|---|---|
| logic | 26 | 6 | **23.1%** | curry_paradox (01), ross_paradox (05), accessibility_relation (08), chisholm_paradox (09), modal_systems_hierarchy (09), conditional_logic (11) |
| aesthetics | 27 | 2 | 7.4% | aesthetic_experience (01), free_play_imagination_understanding (07) |
| mind | 57 | 3 | 5.3% | phenomenal_intentionality (08), causal_exclusion_argument (09), representationalism_perception (09) |
| service | 25 | 1 | 4.0% | bayes_theorem (09) |
| epistemology | 54 | 1 | 1.9% | conditionalization (06) |
| ethics | 56 | 0 | 0.0% | — |
| metaphysics | 52 | 0 | 0.0% | — |
| language | 28 | 0 | 0.0% | — |
| political | 28 | 0 | 0.0% | — |
| science | 27 | 0 | 0.0% | — |
| **All** | **380** | **13** | **3.4%** | |

**Structural observation.** C3 failures cluster sharply in the **logic** subdomain (6 of 26 logic nodes, 23.1%). The shared failure shape is uniform: the load-bearing first sentence of the summary deploys formal-logic apparatus (modal operators, deontic-logic acronyms, accessibility relations, axiomatic notation) without inline gloss, and the surrounding sentences depend on the same apparatus. The mind cluster (phenomenal intentionality, causal exclusion, representationalism of perception) and the service / epistemology singletons (Bayes's theorem; conditionalization) carry the same shape with different content — formal apparatus or technical-term-of-art front-and-center in the load-bearing sentence.

### 4.3 Node-domain — C2 and `teaching_notes` ABSENT

Zero `teaching_notes` ABSENT cases across all 380 nodes. Zero C2 fails. Per-domain breakdown is uniformly 100% PASS.

## 5. C1 drift comparison vs the production audit's 13% baseline

### 5.1 The two studies have different sampling shapes

The production audit ([`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md), S-0082 → S-0122) used a stratified-sampling approach with subdomain audits and a separate cross-bridge full-census, deduplicated to ~445 elements with ~58 substantive defects = **13.0%**. The census re-validates the same C1 question against the **full edge population (516 edges) at the post-fix graph**, after the audit's follow-up migrations 0061–0065 landed (per the rubric, the census is positioned to detect drift, not to repeat the audit).

This means the census's C1 rate is **not** apples-to-apples with the audit's 13% — they measure two different populations with two different selection methods, and the audit's findings were largely fixed before the census ran. The rubric's framing ("apples-to-apples comparable") expressed the goal that the verdict taxonomy match (it does — both use Sound / Defensible / Reversed / Weak-redundant). It does not mean the rates measure the same defect prevalence.

### 5.2 Observed rates

| Study | Population | Defectives | Rate |
|---|---|---|---|
| Production audit (S-0082 → S-0122) | ~445 deduplicated sample (cross-bridges + 9 subdomain audits + hubs/traces) | ~58 substantive | **~13.0%** |
| QA census (S-0158 → S-0182, post-fix) | 516 full edge population | 7 Reversed + 0 Weak-redundant | **1.36%** |

The census's 1.36% is **~9.5× below** the production audit's 13.0%. Per the audit's subdomain table, the audit's per-subdomain rates ranged from 5.0% (AUDIT-LOG) to 35.2% (AUDIT-CB cross-bridges). Cross-bridges drove most of the audit's headline rate; the audit's largest-sample subdomains (EPI 5.4%, LOG 5.0%, AES 5.3%) sat well below 13%.

### 5.3 Drift interpretation

Two complementary explanations of the gap, both supported by structural evidence:

1. **The audit follow-up migrations (0061–0065) worked.** The audit found and fixed the highest-density defect locus (cross-bridges, 35.2% pre-fix). The census measures the post-fix graph. The cross-bridge defect rate observed by the census is **0.0%** (0 / 55 cross-domain edges) — a complete sweep at the audit's most concentrated finding cluster. This is consistent with the audit's fixes being correctly applied and durable.

2. **Within-domain edges are well-vetted in the seed corpus.** Of the 461 within-domain edges, only 7 are Reversed (1.52%). This is below the audit's lowest per-subdomain rate (LOG 5.0%, AES 5.3%, EPI 5.4%) — and the census scored the *full population* of within-domain edges, not a stratified sample. The within-domain authoring pass that produced the seed graph was evidently meticulous on direction at the level of routine pedagogical relationships (genus / species, framework / concept, position / objection); the residue is concentrated in a handful of edge cases (notably the mind domain at 3.95%, where four distinct authoring directions remain contested by the census).

The census thus produces a **headline finding of 1.36% C1 defect rate at the post-fix seed graph**, with no Weak-redundant cases. This is the operational drift measurement Phase 6 needs.

### 5.4 What was NOT a drift signal

The pre-census production audit reported per-subdomain rates as high as 22.2% (AUDIT-SVC service nodes). The census's service-domain edge rate is **1.82%** (1 / 55). The audit's high service rate was driven by historical-tradition edges (within-service A3 internals) that 0061–0065 partly addressed. The census does not see those residues, which is consistent with the audit's fixes having been applied.

The audit reported a 21.0% rate for the language subdomain (AUDIT-LAN). The census's language-source rate is **0.0%** (0 / 32). Same explanation: the audit's two reversed (developmental-arc + tools-vs-position) findings were addressed by the follow-up migrations.

## 6. Pattern clusters

### 6.1 Reversed cluster — within-domain reversal at the post-fix graph

All 7 Reversed verdicts are within-domain (§4.1). They fall into three structural sub-shapes:

**Sub-shape A: theory → its constitutive concept (4 instances).** Knowledge-How → Knowledge (shard 01 E-26); Utilitarianism → Hedonism (shard 02 E-15); Perdurantism → Temporal Parts (shard 03 E-14); Computational Theory of Mind → Turing Test (shard 08 E-4). The shape: an edge running from a *named theory* to a *concept the theory deploys or builds on*. The pedagogical direction runs the other way — the constituent concept is needed to grasp the theory.

**Sub-shape B: specific position → defining thought-experiment / sub-position (2 instances).** Phenomenal Concept Strategy → Type-B Materialism (shard 01 E-5); Property Dualism → Philosophical Zombie (shard 05 E-7). The phenomenal-concept strategy is downstream of type-B materialism (it is a *response* within the position); philosophical zombies are the canonical motivating case for property dualism. Both run the inverse of pedagogical priority.

**Sub-shape C: derived service-node → its foundational service-node (1 instance).** Set (Mathematical) → Axiom (Mathematical) (shard 01 E-24). Axioms of geometry / arithmetic predate and are independent of set theory; if anything, axiomatic set theory presupposes the notion of an axiom.

The cluster is small (7 / 516) and the sub-shapes are pedagogically clean — these are tractable rather than structural defects. Three of the four Sub-shape A instances and both Sub-shape B instances are in shards 01 / 05 / 08, which is also where the early routine batch concentrated its over-Defensible counts (per §6.2).

### 6.2 Defensible cluster — a taxonomy of supportable-but-non-canonical directions

The census carries **48 Defensible verdicts** (9.3% of edges). Defensible is not a defect, but the sub-shape taxonomy is the most analytically rich finding of the routine batch. Each evidence file's cross-cutting observations build toward a recurring set of sub-shapes:

| Sub-shape | Where it appears | Routine-batch frequency |
|---|---|---|
| **Specific-position → broader-field / topic** ("foothold into bigger field" or "foil-into-tradition") | shards 17 (E-5 testimonial_knowledge → social_epistemology, E-6 consequentialism → supererogation); shard 18 (E-13 biocentrism → animal_ethics, E-19 temporal_parts → mereology, E-25 political_obligation → conservatism); shard 19 (E-18 bivalence_principle → validity_logical) | 6+ exemplars |
| **Framework → key concept it foregrounds** | shards 13 (E-15 virtue_epistemology → intellectual_virtue); 14 (E-17 framework→concept); 19 (E-03 expression_theory_art → expression_in_art) | 3 exemplars |
| **Position → its canonical motivating thought-experiment** | shard 19 (E-07 semantic_externalism → twin_earth) | 1 exemplar |
| **Audit-touched / canonical-direction-inversion at 0064 retain-with-annotation cluster** | shards 14, 15, 16 | 3+ exemplars |
| **Co-fundamental / near-co-equal category** | shard 16 (E-25 co-fundamental); shard 02 (animal vs environmental ethics) | 2+ exemplars |
| **"Target is more general / more foundational"** (held at Defensible on the concrete-entry-point reading; the recurring rubric-calibration question) | shards 05, 06, 07, 08, 09 (≥6 exemplars: shard 05 — flagged; shard 06 — E-12, E-17, E-21; shard 07 — E-9 climate_ethics → future_generations, E-26 scientific_theory → law_of_nature; shard 08 — E-11 free_will → determinism; shard 09 — E-2 modus_ponens → propositional_logic, E-26 propositional_knowledge → knowledge) | ≥9 exemplars |

The **"target is more general"** sub-shape is the most frequent (≥9 exemplars across shards 05–09) and is the standing rubric-calibration question the routine batch surfaced for the disposition session: should this shape tip Defensible → Reversed, given the canonical pedagogy is genus-before-species? Each routine session held the verdicts at Defensible per the rubric's literal "supportable on an alternative reading" criterion, but flagged the cluster repeatedly. **The disposition session adjudicates the threshold — this closeout enumerates, not adjudicates.**

### 6.3 C3 cluster — load-bearing first sentence gated on undefined formal apparatus

All 13 C3 fails share the same structural shape: the summary's load-bearing first sentence deploys formal-apparatus vocabulary (modal-logic notation, deontic-logic acronyms, accessibility relations, Bayesian / probabilistic notation, Kantian framework terms) without inline gloss, and the surrounding prose depends on the same apparatus.

| C3-fail class | Nodes | Domain |
|---|---|---|
| Modal-logic apparatus (accessibility / modal hierarchy / Kripke semantics) | accessibility_relation (08), modal_systems_hierarchy (09), conditional_logic (11) | logic |
| Deontic-logic SDL acronym + axiomatic-notation | ross_paradox (05), chisholm_paradox (09) | logic |
| Logico-mathematical paradox (deduction theorem / contraction / formal trick) | curry_paradox (01) | logic |
| Probabilistic-notation gated | conditionalization (06), bayes_theorem (09) | epistemology, service |
| Phenomenal-intentionality / phenomenal-character / supervenience framework | phenomenal_intentionality (08), causal_exclusion_argument (09), representationalism_perception (09) | mind |
| Kantian third-Critique framework | free_play_imagination_understanding (07) | aesthetics |
| Borderline-circular / aesthetic-properties-leading | aesthetic_experience (01) | aesthetics |

The "logic" domain accounts for 6 of 13 fails (46.2%); the "mind" domain accounts for 3 of 13 (23.1%). Both clusters share the same authoring pattern: technical-term-of-art front-and-center in the load-bearing position. The logic cluster is uniformly formal-apparatus-driven; the mind cluster is technical-term-of-art-driven (phenomenal character, supervenience). The two singletons (Bayes / conditionalization) are notation-driven (formula first).

The shared remediation shape is identical: prepend a topic-handle sentence in plain language, then introduce the formal apparatus. Several adjacent passing nodes already do this. For example, **modal_logic** (shard 09 N-14) passes because its first sentence "The formal logic of necessity and possibility" gives a topic-handle before any apparatus arrives, whereas the sibling **modal_systems_hierarchy** (shard 09 N-19) opens with the K ⊂ T ⊂ S4 ⊂ S5 subset notation and fails. The 13 C3 fails are individually addressable by the same authoring pattern that the passing siblings already follow.

### 6.4 In-shard semantic-neighborhood clusters

Several shards surfaced tight in-shard pedagogical neighborhoods worth noting at the closeout (analytically interesting; not defect signal):

- **Shard 16:** four-edge position-and-rejection cluster around a single source.
- **Shard 17:** three-level applied-ethics ladder (applied_ethics > bioethics > research_ethics > informed_consent) constructed across shards 16–17.
- **Shard 18:** two-edge introduction-of-the-debate cluster on scientific_realism; two-edge sub-relation cluster on propositional_knowledge; two-edge paraconsistent-program cluster.
- **Shard 19:** foil-for-rejection three-edge cluster (E-06 / E-13 / E-16); mind-body 5-node cluster (dualism / substance_dualism / panpsychism / phenomenal_concept_strategy / hard_problem_of_consciousness).

These are evidence that the seed graph carries genuine pedagogical structure visible at the shard level. They are not defect findings; they are signal that the authoring produced coherent local neighborhoods, not just bag-of-edges.

### 6.5 Audit cross-reference workflow lesson

Across shards 13–19 (the late routine batch), the evidence sessions converged on a workflow rule for distinguishing genuine audit-touched edges from false-positive proximity hits: **inline `evidence` text on an edge is the necessary-and-sufficient gold signal that the edge was deliberately reasoned about by the production audit.** Proximity-against-migration-tuples without inline `evidence` produced uniformly false-positive hits across the late routine batch (≥10 false-positives narrowed out across shards 13–18 by per-hit exact-tuple inspection; shard 19 carried three audit-touched edges all directly identified via inline `evidence`).

The cross-reference workflow is **mature** for the seed-graph corpus as of the close of this census. The routine sessions' rolling note recommends that any future audit-cross-reference workflow rely exclusively on inline `evidence` text and treat proximity-without-evidence as a heuristic that consistently produces false positives. **The disposition session may want to capture this workflow lesson into the rubric or into [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md) if the workflow is expected to recur.** (Closeout flags only; not adjudicating.)

## 7. For Phase 6 self-correction

Phase 6 (the self-correction pipeline — tension log + Opus batch review per [ADR 0014](../../product/adr/0014-sonnet-teaches-opus-reviews.md)) needs real defect-rate calibration data. The census provides:

### 7.1 Defect-rate-driven calibration inputs

- **C1 prerequisite-direction error rate at the post-fix seed graph: 1.36% (7 / 516).** This is the operational baseline for Phase 6's tension log on edge-direction signals. The pipeline should not over-fire on prerequisite-direction tension events — at 1.36% prevalence, the false-positive cost of an aggressive direction-flagging signal would dominate the workflow.
- **C2 `teaching_notes` traction failure rate: 0.0% (0 / 380).** Phase 6 does not need to allocate review budget to `teaching_notes` traction at the seed level. The authoring pass produced uniformly substantive `teaching_notes`; future drift would be the signal to revisit.
- **C3 summary cold-readability failure rate: 3.4% (13 / 380), concentrated in `logic` (23.1%) and `mind` (5.3%) subdomains.** Phase 6 should weight C3-style summary-readability reviews toward these two subdomains, and toward nodes whose first sentence puts formal apparatus or technical-term-of-art in the load-bearing position.

### 7.2 Tension-log shape recommendations (closeout flags only)

The Defensible cluster (48 verdicts, 9.3% of edges) is the dominant category of "supportable-but-non-canonical" verdicts the census surfaces. Phase 6's tension log could productively distinguish:

- **High-prevalence Defensible sub-shapes** (especially "specific → broader" with ≥9 routine-batch exemplars across shards 05–09) — these are rubric-calibration questions, not defects. Phase 6's tension log should capture them as **calibration signals**, not as edge-fix candidates. A tension event saying "this looks like a Reversed but I held it Defensible" should mark a calibration data point rather than fire an Opus review.

- **Within-domain Reversed sub-shapes** (Sub-shapes A / B / C from §6.1) — these are tractable defects suitable for Phase 6's Opus review batch. Seven instances in this census is small enough to handle individually; the closeout does not propose specific corrections (per anti-scope) but Phase 6 may want to start its Opus-review evidence-base with these seven.

- **C3 formal-apparatus pattern** — uniform across 13 fails. Phase 6 could apply a single rewrite recipe (topic-handle sentence first, formal apparatus second) across the cluster as a batch operation rather than per-node manual edits. The passing siblings (modal_logic, deontic_logic, representationalism_consciousness) already exhibit the target shape.

### 7.3 What the census does NOT tell Phase 6

- **Rigor calibration** is out of scope per the rubric. The `missing_rigor_score` soft-warn (Phase 6's owner per [`engine/operations/code-discipline.md`](../operations/code-discipline.md)) is unchanged by this census.
- **The Defensible-shape taxonomy is enumeration, not adjudication.** The rubric-calibration question — should "specific → broader" tip toward Reversed? — is not answered by the census; it is flagged for the disposition session.
- **The census's verdicts are pinned to the rubric as authored in S-0156.** If Phase 6 revises the rubric (changes the Defensible / Reversed threshold, adds a fifth verdict, removes Weak-redundant as a verdict because the census found zero), the verdicts in this report are tied to the original rubric and cannot be re-scored without re-running the routine batch against the revised rubric.

### 7.4 One-paragraph summary

The seed graph at S-0182 close is, by the QA census measure, in substantially better shape than the production audit's 13% baseline suggested before the 0061–0065 fixes landed: **C1 1.36%, C2 0.0%, C3 3.4%** at full-population scoring. The remaining C1 defectives concentrate in within-domain mind / service / epistemology / ethics / metaphysics edges (cross-domain edges are clean — the audit's cross-bridge fortification durably worked). The dominant C3 cluster is the load-bearing-first-sentence-gated-on-formal-apparatus pattern, concentrated in the logic and mind subdomains. Phase 6's tension log can calibrate its edge-direction sensitivity around the 1.36% prevalence; its summary-readability sensitivity around the 3.4% prevalence with a logic / mind weighting; and its `teaching_notes` traction signal can be deprioritized at the seed level given the 0.0% failure rate.

## 8. Anti-scope reminder

The closeout is aggregation only. The disposition decisions — whether to file Issues for the 7 Reversed edges, whether to propose migration corrections, whether to revise the rubric on the "target is more general" Defensible sub-shape, whether to apply the C3 rewrite recipe to the 13 fails as a batch — all belong to a follow-up interactive session. The findings here are the disposition session's input; the disposition session is the surface that adjudicates.

## See also

- [`seed_qa_audit.md`](seed_qa_audit.md) — pinned rubric and closeout mandate.
- [`seed_qa_evidence/`](seed_qa_evidence/) — the 19 per-shard evidence files + 2 SEP-anchored re-audits.
- [`seed_qa_evidence/shards.json`](seed_qa_evidence/shards.json) — committed manifest, source of truth for the partition.
- [`phase_5_production_audit_findings.md`](phase_5_production_audit_findings.md) — the 13% baseline this census drift-checks against.
- [ADR 0014](../../product/adr/0014-sonnet-teaches-opus-reviews.md) — Phase 6 self-correction architecture (the closeout's downstream consumer).
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — routine-mode architecture; the apparatus that fired all 19 routine evidence sessions.
- [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md) — structural reference fetching; the S-0165 re-audits' anchoring mechanism.
