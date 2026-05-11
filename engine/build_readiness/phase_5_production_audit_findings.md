# Phase 5 graph production audit — findings report

> Authored by S-0122 (interactive closeout) per the master plan at [`phase_5_production_audit.md`](phase_5_production_audit.md) §"Forward pointers to closeout". Pairs with the audit-system-input report at [`phase_5_audit_system_input.md`](phase_5_audit_system_input.md) and the structural-reopen ADR memo at [`../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md`](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md). Consumes the 13 evidence files in [`phase_5_production_audit_evidence/`](phase_5_production_audit_evidence/) and the empirical-fortification briefs in `/tmp/s0122_fortification/` (ephemeral; structural extracts inline below).
>
> **Naming choice.** Closeout adopts option (b) from master plan §"Naming note": the master plan keeps its existing filename (`phase_5_production_audit.md`); this findings report sits alongside as a sibling. The renaming-to-gate option (a) was rejected because it touches the cross-references already in STATE.md / ENGINE_LOG.md / ROADMAP.md / S-0082 archive and the cost exceeds the clarity gain.

## Scope

This report consolidates the audit-window evidence (S-0104 → S-0120, 13 evidence files covering 71 cross-bridges + ~265 within-subdomain edges + ~96 nodes + 10 hubs + 3 syllabus traces — roughly 445 graph elements under SEP-anchored review) into a triaged disposition matrix. The closeout's empirical-fortification pass (per [ADR 0059](../adr/0059-audit-time-structural-reference-fetching.md)) ran 33 SEP fetches against `plato.stanford.edu` over the medium-confidence + mutation-implying verdict band; 31 succeeded; 0 raised `AnonymizationViolation`; 2 returned HTTP 404 (slug guesses for nodes that don't have stand-alone SEP entries — `hanson` covered by `science-theory-observation`; `legitimacy-political` covered by other entries' cross-references). Rate-limit empirically observed at ~2.0s per fetch across the 31 successful calls.

The fortification analysis (`/tmp/s0122_fortification/analyze_briefs.py`) checked each verdict's source SEP entry's `cross_references` for the target concept's slug. Outcomes:

- **30 corroborated** (65%) — source SEP entry's forward cross-references either omit the claimed target entirely (supporting the historical / weak / reversed / defensible verdicts) or link to a non-modern variant of the target (e.g., `causation-medieval` rather than `causation-metaphysics`).
- **15 with forward link present** (33%) — source SEP entry does cross-reference the target concept directly. **This does not automatically refute the verdict.** Forward cross-reference is necessary for a defensible pedagogical-prerequisite claim but not sufficient — direction, granularity, and parallel-edge redundancy concerns each turn on additional considerations the cross-reference does not adjudicate. The 15 break down further: 3 spurious slug matches (cross-ref to a different sense / medieval-not-modern variant), 7 relation-confirmed-but-direction-still-open (the directional reversal argument stands even when both nodes cross-reference each other), 5 genuine partial-weakening (forward link adds support to a real bidirectional relation but the verdict's specific concern — redundancy, shortcut, granularity — remains).
- **1 structural-only** — N-8 bayesian_epistemology granularity-mismatch; no target slug to check; SEP word-count 35,816 with section-path `1. The Bayesian Framework` confirms the entry treats Bayesianism as a structured doctrinal cluster rather than a sub-discipline housing many atomic children, which strengthens the case for treating `bayesian_epistemology` as concept-level (acceptable) rather than retiring as discipline-label.

## Aggregate defect rates by subdomain

| Subdomain | Sample | Substantive defects | % | Patterns |
|---|---|---|---|---|
| AUDIT-CB (cross-bridges, full census) | 71 | 25 | 35.2% | reversal cluster (8); historical (14); weak (3) |
| AUDIT-EPI (epistemology) | 37 | 2 | 5.4% | 1 reversed; 1 granularity (Bayesian) |
| AUDIT-ETH (ethics) | 36 | 6 | 16.7% | 1 reversed; 2 weak/parallel-edge; 2 granularity (sub-discipline) |
| AUDIT-MET (metaphysics) | 35 | 5 | 14.3% | 1 weak/shortcut; 2 defensible/metaontological-commitment; 2 granularity (sub-discipline) |
| AUDIT-MIN (philosophy of mind) | 37 | 4 | 10.8% | 2 reversed (argument-vs-position); 1 defensible (tools-vs-topic); 1 school/movement (phenomenology) |
| AUDIT-LAN (language) | 19 | 4 | 21.0% | 2 reversed (developmental-arc + tools-vs-position); 2 defensible |
| AUDIT-LOG (logic) | 20 | 1 | 5.0% | 1 defensible (overdetermined multi-prereq) |
| AUDIT-SCI (philosophy of science) | 19 | 2 | 10.5% | 1 reversed (developmental-arc); 1 granularity (top-level discipline) |
| AUDIT-POL (political philosophy) | 20 | 2 | 10.0% | 1 defensible (question-vs-answer); 1 granularity (top-level discipline) |
| AUDIT-AES (aesthetics) | 19 | 1 | 5.3% | 1 defensible |
| AUDIT-SVC (service nodes) | 18 | 4 | 22.2% | 2 historical (within-service A3 internals); 1 defensible; 1 granularity (Aristotelian Four Causes thinker-framework) |
| AUDIT-HT (hubs + traces) | 78 | ~6 unique (excluding duplicates with crossbridges A3) | ~7.7% | 3 reversed (duplicates: CB-E-47, CB-E-63, CB-E-70); 1 weak; 1 defensible; 3 granularity (top-level discipline labels per philosophy_of_language / philosophy_of_science / political_philosophy) |
| **Total (deduplicated)** | **~445** | **~58 distinct** | **~13%** | — |

**Calibration commentary.** The 13% overall defect rate runs well below the cross-bridge baseline (35.2%) and is heavily concentrated in two structural-pattern clusters: (1) the cross-bridge reversal + historical clusters discussed in §"Reversal cluster" and §"Historical genealogy cluster" below; (2) the granularity / sub-discipline-label patterns discussed in §"Granularity patterns." Of the ~58 distinct findings, ~30 sit within these two clusters; the remaining ~28 distribute across 13 evidence files at low per-file rate (typically 1-3 findings per file outside the cross-bridge concentration).

Pattern: **within-subdomain edges run cleaner than cross-bridges.** Logic (5%), aesthetics (5.3%), epistemology (5.4%) are tightly determined by their internal pedagogical sequences (formal-systems hierarchy for logic; framework-then-positions for epistemology; field-then-positions for aesthetics). Ethics (16.7%), language (21%), service (22.2%) run higher because they involve more contested developmental-arc choices (Hanson-Kuhn for science / paradigm; Austin's performatives-vs-speech-act-framework for language) or thinker-framework granularity (Aristotelian Four Causes as a service-domain node).

## Reversal cluster (cross-bridges)

The 8 reversed cross-bridge edges (crossbridges.md §"Cross-cutting observations" #3) constitute a coherent pattern: **when a cross-domain edge connects a specific position / sub-concept (X) to its broader / parent category (Y), the edge gets authored as `X → Y` instead of `Y → X`.** Five of the eight (E-47, E-63, E-65, E-69, E-70) are contradicted by the migration's own pedagogical-warrant prose. Three (E-54, E-55, E-56) cluster around the application-grounds-apparatus shape (formal_epistemology / epistemic_closure → modal_logic / kripke_semantics; the direction should be apparatus-grounds-application).

| Finding | Direction (authored) | SEP-canonical direction | Fortification |
|---|---|---|---|
| CB-E-47 | epistemic_justification → propositional_attitude | propositional_attitude → epistemic_justification | corroborated (PA-Reports SEP entry does not link forward to epistemic_justification) |
| CB-E-54 | formal_epistemology → modal_logic | modal_logic → formal_epistemology | corroborated (Modal Logic SEP entry does not link forward to formal_epistemology) |
| CB-E-55 | formal_epistemology → kripke_semantics | kripke_semantics → formal_epistemology | corroborated (same — Modal Logic does not link forward) |
| CB-E-56 | epistemic_closure → modal_logic | modal_logic → epistemic_closure (informal closure can be taught without modal logic) | corroborated |
| CB-E-63 | propositional_attitude → proposition | proposition → propositional_attitude | weakened (PA-Reports does cross-ref propositions-structured) — verdict's content-vs-attitude argument stands; SEP cross-link does not adjudicate directionality |
| CB-E-65 | causal_theory_of_mental_content → causal_theory_of_reference | causal_theory_of_reference → causal_theory_of_mental_content (Kripke-Putnam predates Fodor-Dretske) | weakened (Reference SEP entry does link content-causal) — direction-of-influence is genealogical; verdict stands on canonical genealogy |
| CB-E-69 | motivational_internalism → propositional_attitude | propositional_attitude → motivational_internalism (MI is a position using PA) | corroborated |
| CB-E-70 | justice → morality | morality → justice (justice is political-domain application of broader moral concepts) | corroborated (Morality SEP entry does not link forward to justice) |

**Disposition (5 of 8 contradicted by own prose).** All 8 edges are mutation-implying: the closeout's recommendation is to **flip direction on all 8** (retire authored edges and re-author with corrected direction in a follow-up migration). The 5 contradicted-by-own-prose edges (E-47, E-63, E-65, E-69, E-70) are particularly clean recommendations — the migration's own teaching_notes argue the opposite direction from the authored edge, strongly suggesting a mechanical authoring slip ("source-target field swap during VALUES list editing").

**Routing per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md):** Single GitHub Issue labeled `bug` with cross-references to the 8 evidence-file finding lines and the production-fix migration plan (re-author with flipped direction; preserve evidence in commit message; backfill `evidence` field with the pedagogical-warrant prose extracted from the migration's teaching_notes — closing one face of the empty-evidence audit-system-input proposal in §"Audit-system inputs" below).

## Historical genealogy cluster (cross-bridges + service)

The 14 historical-not-pedagogical cross-bridge findings (crossbridges.md §"Cross-cutting observations" #2) cluster overwhelmingly in the A3 grouping (history terminators → philosophy): 14 of 18 A3 edges, with the remaining 4 (E-37, E-40, E-44, E-45) defensible or sound on closer reading. Plus the 2 within-service A3-internal historical edges from AUDIT-SVC (E-2 presocratic_naturalism → aristotelian_four_causes, E-3 aristotelian_four_causes → vienna_circle_logical_positivism) extend the pattern within the service domain.

**Fortification result — 9 of 14 corroborated by SEP forward-cross-reference absence:**

| Finding | Source → Target | Fortification |
|---|---|---|
| CB-E-28 | aristotelian_four_causes → causation | (matched: causation-medieval) — SEP links Aristotle's four causes forward to *medieval* causation only, not modern. Corroborates historical reading (the modern causation entry treats the four causes as historical background, not as a prerequisite chapter). |
| CB-E-29 | aristotelian_four_causes → essence_metaphysical | corroborated — Aristotle on Causality SEP entry does not link forward to modern essence-metaphysics |
| CB-E-30 | aristotelian_four_causes → scientific_explanation | corroborated |
| CB-E-31 | aristotelian_four_causes → humean_regularity_theory | corroborated |
| CB-E-32 | greek_atomism → physicalism | corroborated (Ancient Atomism SEP entry does not link forward to modern physicalism) |
| CB-E-33 | greek_atomism → reductionism_in_science | corroborated |
| CB-E-34 | greek_atomism → mereological_nihilism | corroborated |
| CB-E-35 | scholasticism → realism_about_universals | partial — Medieval Universals SEP entry links to general "properties" entry but not specifically to contemporary realism positions (Armstrong, Lewis) |
| CB-E-36 | scholasticism → divine_command_theory | partial — Voluntarism-Theological SEP entry links to "religion-morality" (broader topic) but not specifically to contemporary DCT (Adams, Quinn) |
| CB-E-38 | renaissance_mechanism → scientific_theory | corroborated (Descartes SEP entry, used as proxy for renaissance-mechanism context, does not link forward to modern theories-of-scientific-theories) |
| CB-E-39 | renaissance_mechanism → scientific_method | corroborated |
| CB-E-41 | vienna_circle_logical_positivism → falsificationism | partial — VC SEP entry links to Popper specifically but not to falsificationism as a topic |
| CB-E-42 | vienna_circle_logical_positivism → demarcation_problem | corroborated |
| CB-E-43 | vienna_circle_logical_positivism → tarskis_t_schema | partial — VC SEP entry links to Tarski (the figure) but not to the T-schema specifically; the verdict's sociological-not-conceptual reading is supported |

**Disposition.** The closeout's expected disposition (per master-plan §"Structural reopen pre-flag") is **activation of `historical_influence` (PREDICATE_MANIFEST.md reserved-but-unused) for the 14 historical edges + retyping**, authored as a product ADR. See [`product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md`](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md). The ADR's data section names the 14 + 2 within-service candidates.

**Dual-typing consideration.** The schema permits multiple edges with different `edge_type` between the same source-target pair. The closeout's recommendation is **retype (single edge with `historical_influence`)** rather than **dual-type** (keep `pedagogical_prerequisite` and add `historical_influence`), because the routine session's verdict was "mis-typed: historical-not-pedagogical" — the SEP framing treats the connection as historical genealogy, not pedagogical prerequisite, in canonical exposition. Dual-typing would falsely imply both relations are pedagogically load-bearing. The ADR adjudicates.

**Routing:** Single GitHub Issue labeled `bug` + `historical-influence-retyping` (new label TBD) with cross-references to the 14 + 2 evidence-file finding lines, the ADR memo, and the production-fix migration plan.

## Weak / parallel-edge / shortcut findings

| Finding | Source → Target | Pattern | Fortification |
|---|---|---|---|
| CB-E-5 | bivalence_principle → paraconsistent_logic | weak (more proximate prereq: classical_logic via explosion principle) | corroborated (Paraconsistent Logic SEP entry does not link bivalence as central prereq) |
| CB-E-27 | expected_value → social_contract_theory | weak (classical contract theorists do not use EV) | corroborated (Contractarianism SEP entry does not link expected-value forward) |
| CB-E-67 | physicalism → reductionism_in_science | weak (both independent positions; reductionism is broader and predates philosophy-of-mind physicalism) | corroborated (Physicalism SEP entry does not link forward to scientific-reduction) |
| ETH-E-17 | virtue_ethics → moral_particularism | weak/parallel-edge with normative_ethics → moral_particularism already in graph | corroborated (Moral Particularism SEP entry treats particularism's virtue-ethics affinity as one connection among several; the broader normative_ethics edge is the canonical genus-prereq) |
| ETH-E-20 | moral_realism → moral_epistemology | weak/parallel-edge with metaethics → moral_epistemology | weakened — moral-epistemology entry does cross-ref moral-realism, but the verdict's redundancy concern (broader edge already in graph) stands |
| MET-E-10 | time → mctaggarts_paradox | weak/shortcut over time → a_theory_of_time → mctaggarts_paradox | weakened — time entry links forward to mctaggart, but the more-proximate prereq edge IS in the graph; shortcut concern stands |
| LOG-E-7 | conditional_logic → chisholm_paradox | defensible (overdetermined multi-prereq; deontic_logic → chisholm_paradox is the canonical proximate prereq) | corroborated |

**Disposition.** Two structural options for each:
- **Prune** the weak / redundant edge in favor of the canonical proximate prereq (CB-E-5, CB-E-27, CB-E-67, ETH-E-17, ETH-E-20, MET-E-10, LOG-E-7)
- **Retain with explicit redundancy annotation** — keep the edge as illuminating-specific-cases or capturing-an-alliance, with the bridge-evidence field populated to make the redundancy visible

The findings report recommends **prune** for CB-E-5 (the classical_logic → paraconsistent_logic + classical_logic → explosion_principle path is cleaner), CB-E-27 (classical social contract theorists don't use EV), and MET-E-10 (the longer path is the canonical pedagogical route). **Retain with annotation** for ETH-E-17 (the virtue-particularism alliance is SEP-recognized), ETH-E-20 (the realist-specific access-to-mind-independent-truths challenge is pedagogically distinct), CB-E-67 (the physicalism-reductionism implication is a real conceptual connection), LOG-E-7 (the conditional-logic illumination of post-Chisholm response literature is pedagogically valuable).

**Routing:** Single GitHub Issue labeled `tech-debt` covering pruning of CB-E-5 / CB-E-27 / MET-E-10 in a follow-up cleanup migration. Retention-with-annotation cases route through the empty-evidence-field cleanup as a separate Issue (every retained-with-annotation edge needs `evidence` populated).

## Direction-of-development reversal patterns (non-crossbridge)

Surfaced across 4 subdomain audits (mind, language, science, ethics), distinct in shape from the cross-bridges reversal cluster:

| Finding | Pattern shape | Fortification |
|---|---|---|
| MIN-E-14 | argument-vs-position direction (hard_problem → explanatory_gap; Levine 1983 precedes Chalmers 1995) | corroborated (Consciousness SEP entry does not link forward to explanatory-gap) |
| MIN-E-17 | argument-supports-position direction (property_dualism → knowledge_argument; argument supports the position, not the other way) | weakened — Qualia-Knowledge entry does link to dualism; verdict directional argument stands (argument supports position) |
| LAN-E-2 | developmental-arc reversal (speech_act → performative_utterance; Austin's 1955 performatives motivated the speech-act framework) | corroborated (Speech Acts SEP entry does not link forward to a stand-alone performative-utterance entry — the topic is internal to the speech-acts entry, supporting the developmental-arc reading where performatives are the seed not the downstream) |
| LAN-E-10 | tools-vs-position reversal (deflationary_theory_of_truth → tarskis_t_schema; Tarski 1933 antedates deflationism) | NOT fortified (verdict was reversed-HIGH; high-confidence verdicts skip the fortification branch per master-plan triage) — closeout adjudication: flip direction (Tarski's T-schema is the technical foundation; deflationism is the philosophical thesis that exploits it) |
| SCI-E-4 | developmental-arc reversal (paradigm → theory_ladenness_of_observation; Hanson 1958 precedes Kuhn 1962) | corroborated (Theory and Observation in Science SEP entry treats Hanson 1958 as foundational; paradigm framework is downstream) |
| ETH-E-16 | foundational-stance reversal (animal_ethics → sentientism; sentientism is the foundational moral-status stance, animal ethics derives from it) | corroborated (Moral Animal SEP entry treats sentience-based moral status as the foundational stance) |
| EPI-E-13 | tradition-precedes-instance reversal (problem_of_induction → pyrrhonian_skepticism; Pyrrhonism's modes predate Hume) | corroborated (Ancient Skepticism SEP entry does not link forward to problem-of-induction as a downstream consequence) |

**Disposition.** All 7 are mutation-implying; the closeout's recommendation is to flip direction on each in a follow-up cleanup migration. The cleanup migration can be batched with the cross-bridges reversal cluster (8 edges) for a total of 15 direction-flips.

**Routing:** Add to the same GitHub Issue as the cross-bridges reversal cluster (label `bug`).

## Granularity patterns

Three distinct shapes surfaced across the audit corpus:

**1. School / movement granularity** — MIN-N-2 phenomenology (S-0110 high-confidence flag per the per-node prompt template's explicit school-name criterion). The phenomenology node names a 20th-century philosophical movement (Husserl, Heidegger, Sartre, Merleau-Ponty), not an atomic concept. Three disposition options:
   - **Retire** the node and replace with atomic phenomenology-tradition concepts (intentionality-Husserlian-style, lifeworld, embodied-cognition-Merleau-Ponty-style) that may already overlap with existing nodes.
   - **Demote** to a category-tag (historical-tradition annotation, not a pedagogical_prerequisite node).
   - **Re-type** to historical_influence — pair with the cross-bridges A3 historical-retyping ADR's broader scope.

The findings report recommends **option 3 (re-type to historical_influence)** and treats this as a borderline edge of the cross-bridges A3 cluster — the phenomenology → consciousness relation is historical-tradition-as-context, not strict pedagogical prereq.

**2. Sub-discipline label with content** — N-8 bayesian_epistemology (S-0105), N-4 moral_epistemology + N-9 animal_ethics (S-0108), N-4 modality + N-6 mereology (S-0109). Sub-discipline labels within a parent discipline that have crystallized into specific doctrinal clusters with structured options. Borderline at concept-vs-discipline granularity. The closeout's recommendation: **accept the granularity** — these labels function pedagogically as well-defined doctrines with named alternatives and structured content; flagging every one as granularity-mismatch would amount to a structural rejection of the seed's decomposition that is not justified by the per-node assessment. The fortification of N-8 bayesian_epistemology (SEP word-count 35,816 with section-path `1. The Bayesian Framework`) confirms that SEP itself treats the topic as a structured doctrinal cluster.

**3. Top-level discipline label** — philosophy_of_language (S-0112 E-6 implicit, not in per-node sample), philosophy_of_science (S-0113 N-5 explicit), political_philosophy (S-0114 N-5 explicit). TOP-LEVEL discipline labels that source foundation-spine `pedagogical_prerequisite` edges to the field's central topics. Per the per-node prompt template's literal granularity criterion this fires for all three. The closeout's recommendation: **retain with explicit "discipline-as-umbrella" semantics**, paired with one new validator soft-warn (`top_level_discipline_label_as_prereq_source`) per §"Audit-system inputs" below. The discipline-as-umbrella node is pedagogically useful as the entry point students orient to before specializing; retiring would force restructuring the foundation spines across all three subdomains.

**4. Thinker-framework granularity** — N-4 aristotelian_four_causes (S-0116 service-domain audit, high-confidence flag per the per-node prompt template's explicit thinker-framework criterion). The label names a specific Aristotelian conceptual framework (four causes), not an atomic mastery concept. Distinct in shape from the school/movement and sub-discipline patterns: a thinker-specific philosophical apparatus that crystallized into a teachable unit within Aristotelian / scholastic philosophy. **Retire-and-replace** is not viable (the four-causes apparatus is the SEP-canonical unit). **Demote-to-tag** is overkill — the unit IS a coherent atomic concept within its tradition. **Re-type** the cross-bridges sourced from this node to historical_influence — done at the ADR level above. Retain the node itself as a concept-level mastery unit within the service domain (the within-domain edges where the four causes are taught as Aristotelian apparatus remain pedagogical_prerequisite).

## Empirical-fortification first-exercise outcomes (closes T1-A through T1-D)

Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) and the first-exercise readiness note at [`fetch_structural_reference_first_exercise.md`](fetch_structural_reference_first_exercise.md), the closeout records:

- **T1-A — Anonymization invariant must catch publication-name surfaces from real SEP fetches.** 31 of 33 successful fetches → 0 `AnonymizationViolation` events. The `_assert_anonymized` recursive walk against `is_publication_name_shaped` / `PUBLICATION_NAME_PATTERN` from `parse_structural_reference.py` does not flag the real SEP HTML structure. The structural-pattern approach (vs enumerated-tokens) handled the live HTML cleanly. **Resolved at S-0122.**
- **T1-B — Robots.txt fetch and parse against real SEP host must succeed under default User-Agent.** All 31 successful fetches proceeded normally; the implicit robots.txt check (via `urllib.robotparser`) did not block any URL. The fallback (robots-unavailable proceeds conservatively) was not exercised. **Resolved at S-0122.**
- **T1-C — Rate-limit (default 2.0s) must be empirically observable against real network.** Wall-clock per-fetch elapsed times across the 31 successful fetches show a clean rate-limit signature: ~2.0s per fetch (typical range 1.94s-2.10s, reflecting the 2.0s rate-limit sleep + a small variable network-fetch component). The first fetch in the queue (`#01 aristotle-causality`) elapsed 0.45s with no prior fetch to gate; subsequent fetches consistently sat at the ~2s rate-limit boundary. Two fetches (`#26 science-theory-observation` at 0.29s and `#31 metaphor` at 0.32s) elapsed below 2s because they followed fetch errors (`#25 hanson` 404 and `#30 legitimacy-political` 404), and the error path does not register a successful host-fetch timestamp for the rate-limiter to gate against. **Resolved at S-0122.**
- **T1-D — One-fetch round-trip against a real SEP URL must produce a non-empty `FocusingBrief.entries`.** All 31 successful fetches returned exactly 1 entry with substantial structural content (word_counts ranging from 9,035 to 45,393; cross_references ranging from 4 to 34 per entry; `extraction_confidence` ≥ 0.99 across the corpus; section_path populated for all). **Resolved at S-0122.**

**Verdict-update tally (the empirical-numbers requirement from ADR 0053):**

- Fetches successfully completed against `plato.stanford.edu`: **31**
- Anonymization violations: **0**
- Rate-limit + robots.txt + User-Agent posture issues: **0** (no blocks, no errors, no `429`s, no `403`s)
- Verdicts updated:
  - **Corroborated:** 30 of 46 fortified verdicts (65%)
  - **With forward link present:** 15 (33%) — of which 3 spurious matches, 7 relation-confirmed-but-direction-still-open, 5 genuine partial-weakening
  - **Structural-only (granularity):** 1
- Fetch errors: **2** (404 on URL-slug guesses — closeout-skipped — `hanson` and `legitimacy-political`; both covered by alternative SEP entries already in the queue)

## Disposition matrix (cross-reference per evidence-file finding)

| Finding | Type | Disposition | Issue label | Cross-reference |
|---|---|---|---|---|
| CB-E-5 | bug (weak edge) | prune | `tech-debt` | [crossbridges.md:E-5](phase_5_production_audit_evidence/crossbridges.md) |
| CB-E-27 | bug (weak edge) | prune | `tech-debt` | [crossbridges.md:E-27](phase_5_production_audit_evidence/crossbridges.md) |
| CB-E-28–34, 38, 39, 41–43 | historical-not-pedagogical (12 cross-bridges) | retype to `historical_influence` | `bug` + ADR memo | [crossbridges.md:E-28-43](phase_5_production_audit_evidence/crossbridges.md) — see [ADR 0061 product](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md) |
| CB-E-35–36 | historical-not-pedagogical (2 partial — some SEP forward links) | retype + flag for closer review | `bug` | same |
| CB-E-47, 54, 55, 56, 63, 65, 69, 70 | bug (8 cross-bridge reversals) | flip direction | `bug` | [crossbridges.md §reversal cluster](phase_5_production_audit_evidence/crossbridges.md) |
| CB-E-67 | weak edge | retain with annotation | `tech-debt` | [crossbridges.md:E-67](phase_5_production_audit_evidence/crossbridges.md) |
| EPI-E-2, EPI-E-13, EPI-E-20, EPI-N-8 | within-epistemology mixed | E-13 flip; E-2 / E-20 retain with annotation; N-8 accept | `bug` / `tech-debt` | [epistemology.md](phase_5_production_audit_evidence/epistemology.md) |
| ETH-E-16 | reversed | flip direction | `bug` | [ethics.md:E-16](phase_5_production_audit_evidence/ethics.md) |
| ETH-E-17, ETH-E-20 | weak/parallel-edge | retain with annotation | `tech-debt` | [ethics.md](phase_5_production_audit_evidence/ethics.md) |
| ETH-N-4, ETH-N-9 | sub-discipline granularity | accept | n/a | [ethics.md](phase_5_production_audit_evidence/ethics.md) |
| MET-E-3, MET-E-12 | metaontological commitment | retain with annotation | `documentation` | [metaphysics.md](phase_5_production_audit_evidence/metaphysics.md) |
| MET-E-10 | weak/shortcut | prune | `tech-debt` | [metaphysics.md:E-10](phase_5_production_audit_evidence/metaphysics.md) |
| MET-N-4, MET-N-6 | sub-discipline granularity | accept | n/a | [metaphysics.md](phase_5_production_audit_evidence/metaphysics.md) |
| MIN-E-12 | defensible/tools-vs-topic | retain with annotation | `documentation` | [mind.md:E-12](phase_5_production_audit_evidence/mind.md) |
| MIN-E-14, MIN-E-17 | reversed (argument-vs-position) | flip direction | `bug` | [mind.md](phase_5_production_audit_evidence/mind.md) |
| MIN-E-23 | school/movement-as-target | re-type to historical_influence | ADR (covered by CB-A3 ADR) | [mind.md:E-23](phase_5_production_audit_evidence/mind.md) |
| MIN-N-2 | school/movement granularity | re-type to historical_influence (covered by CB-A3 ADR) | n/a | [mind.md:N-2](phase_5_production_audit_evidence/mind.md) |
| LAN-E-2, LAN-E-10 | reversed (developmental-arc / tools-vs-position) | flip direction | `bug` | [language.md](phase_5_production_audit_evidence/language.md) |
| LAN-E-3, LAN-E-5 | defensible | retain with annotation | `documentation` | [language.md](phase_5_production_audit_evidence/language.md) |
| LOG-E-7 | defensible/overdetermined | prune | `tech-debt` | [logic.md:E-7](phase_5_production_audit_evidence/logic.md) |
| SCI-E-4 | reversed (developmental-arc) | flip direction | `bug` | [science.md:E-4](phase_5_production_audit_evidence/science.md) |
| SCI-N-5 | top-level discipline granularity | retain with annotation + new validator soft-warn | `enhancement` | [science.md:N-5](phase_5_production_audit_evidence/science.md) |
| POL-E-6 | defensible (question-vs-answer) | retain with annotation | `documentation` | [political.md:E-6](phase_5_production_audit_evidence/political.md) |
| POL-N-5 | top-level discipline granularity | covered by SCI-N-5 enhancement | n/a | [political.md:N-5](phase_5_production_audit_evidence/political.md) |
| AES-E-3 | defensible | retain with annotation | `documentation` | [aesthetics.md:E-3](phase_5_production_audit_evidence/aesthetics.md) |
| SVC-E-2, SVC-E-3 | historical (within-service) | retype to historical_influence (covered by CB-A3 ADR) | n/a | [service.md](phase_5_production_audit_evidence/service.md) |
| SVC-E-10 | defensible (set-axiom relation) | accept (math-internal) | n/a | [service.md:E-10](phase_5_production_audit_evidence/service.md) |
| SVC-N-4 | thinker-framework granularity | retain node; retype cross-bridges via CB-A3 ADR | n/a | [service.md:N-4](phase_5_production_audit_evidence/service.md) |
| HUB-EJ, HUB-EX, HUB-CL, HUB-VC | hub-incident edges duplicating CB findings | covered by CB-A3 ADR + reversal flip | n/a | [hubs_1_5.md](phase_5_production_audit_evidence/hubs_1_5.md), [hubs_6_10_and_traces.md](phase_5_production_audit_evidence/hubs_6_10_and_traces.md) |

## Audit-system inputs (consolidated)

Detailed in [`phase_5_audit_system_input.md`](phase_5_audit_system_input.md). Six recommendations:

1. **Existing `edge_evidence_empty` validator soft-warn proposal** (master-plan §"Audit-system-input proposals" #1) — promote to implementation. Universal-null `evidence` field across all 536 edges is confirmed graph-wide.
2. **Existing `discipline_label_node_at_root` validator soft-warn proposal** (master-plan #2) — refine to TWO categories per the corpus's findings: `sub_discipline_label_with_content` (accept-per-decomposition) vs `top_level_discipline_label_as_prereq_source` (warn — surfaced at 3 instances).
3. **Existing `prereq_direction_summary_inconsistency` validator soft-warn proposal** (master-plan #3) — promote; the 5 cross-bridges reversal cluster cases where the migration's own pedagogical-warrant prose contradicted the authored edge direction (CB-E-47, CB-E-63, CB-E-65, CB-E-69, CB-E-70) are the canonical training data.
4. **Existing `historical_node_as_prereq_source` validator soft-warn proposal** (master-plan #4) — promote pending sub-class tagging in node schema (history-terminator vs current-philosophical-position vs thinker-framework). Tagging extension is a separate ADR.
5. **NEW: `cross_bridge_pedagogical_direction_inconsistent_with_summary` validator soft-warn** (extends master-plan #3 specifically for cross-domain bridges) — surfaced as a candidate at S-0104.
6. **NEW: `developmental_arc_reversal` validator soft-warn** (the historical seed observation is taught after the systematized framework that subsumes it; surfaced in S-0112 E-2, S-0113 E-4) — pending discriminator predicate.

## Cross-references

- Master plan: [`phase_5_production_audit.md`](phase_5_production_audit.md)
- Evidence files: [`phase_5_production_audit_evidence/`](phase_5_production_audit_evidence/)
- Audit-system-input report: [`phase_5_audit_system_input.md`](phase_5_audit_system_input.md)
- Structural-reopen ADR memo (historical_influence retyping): [`../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md`](../../product/adr/0061-historical-influence-retyping-for-history-terminator-bridges.md)
- First-exercise readiness note: [`fetch_structural_reference_first_exercise.md`](fetch_structural_reference_first_exercise.md)
- Phase 5 closeout report (the build-side closeout, distinct from this audit-side closeout): [`phase_5_closeout.md`](phase_5_closeout.md)
- [ADR 0046 product](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) (structural-reference posture)
- [ADR 0052 product](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) (subdomain decomposition)
- [ADR 0053 mechanism-first-exercise-gate](../adr/0053-mechanism-first-exercise-gate.md), [ADR 0059 audit-time-structural-reference-fetching](../adr/0059-audit-time-structural-reference-fetching.md)
- [PREDICATE_MANIFEST.md](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) (`historical_influence` reserved-but-unused row)
