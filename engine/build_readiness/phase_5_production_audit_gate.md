# Phase 5 production audit — warrant gate

> Authored by S-0081 per the approved plan at `~/.claude/plans/exploration-session-phase-5-flickering-newell.md`. The gate's purpose is to determine — with predeclared decision thresholds — whether the larger 14-session Phase 5 graph production audit is warranted, before committing to that session block on speculation. Output: a PROCEED / RESCOPE / CANCEL recommendation backed by 20 sampled edges + a topology pass + a threshold-rule application.
>
> This is the third class of `engine/build_readiness/*.md` artifact, alongside *gate* reports (per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md)) and *closeout* reports (per [phase_5_closeout.md](phase_5_closeout.md) precedent). Audit-warrant gates are a fourth class introduced here; the README index update is a small companion edit at the end of this session.

## Recommendation

**PROCEED with the full 14-session production audit.**

Threshold-rule outcome:

| PROCEED condition | Met? | Evidence |
|---|---|---|
| ≥3 substantive candidate findings from 20-edge sample | ✅ Strongly met | 7 of 15 cross-bridge edges (47%) have substantive findings; 0 of 5 within-domain edges (epistemology) have findings |
| ≥2 mis-typed cross-bridge predicates | ✅ Met | 4–5 cross-bridges encode *historical-not-pedagogical* relationships, fitting the plan's "thematic / correlational / historical" mis-typing description |
| ≥2 structural red flags from topology pass | ⚠ Met by spirit, not by named magnitudes | Dead-end-leaf proportion ~50% in major subdomains, discipline-label nodes acting as roots, empty `evidence` field across all 536 edges. None hit the named thresholds (hub degree >40, syllabus chain >25), but the patterns are structurally suspicious |

Two of three PROCEED conditions are met directly; the third is met in spirit. The 14-session production audit is justified.

**Additional findings the gate surfaced that the threshold rule did not predict** (worth preserving for the master-plan session):

- Universal empty `evidence` field — 0 of 536 edges (cross-bridge or within-domain) have any text in `evidence`. Audit-system input: a `gate-feasible` finding (validator soft-warn for empty evidence).
- Reversed edge: `propositional_attitude → proposition`. The summaries of the two nodes themselves contradict the edge direction. Audit-system input: a `gate-feasible` finding (validator soft-warn for prereq-direction inconsistencies detectable from summary text — though this would need NLP and is harder than the empty-evidence check).
- Coverage gap: no node for "free speech" / "free expression" — political philosophy lacks one of its canonical concepts. Audit-system input: `post-build-only` (coverage gaps require domain-knowledge comparison).
- Granularity-mismatch: discipline-label nodes (Political Philosophy, Metaphysics, Ontology) acting as roots in the syllabus traces — pedagogically these are discipline names, not concepts a freshman would master.
- "Service" subdomain mixes formal-tools (logic/math primitives, ~17 nodes) with history-of-philosophy nodes (~7 nodes — Greek Atomism, Scholasticism, Vienna Circle, etc.) per [ADR 0052 product](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md)'s "history terminators" sub-class. This is by design but is the source of the historical-not-pedagogical cross-bridge pattern.

Finding-density extrapolation: 7 findings in 15 cross-bridges (47%) projects to ~33 across all 71 cross-bridges. The plan's stopping rule ("if cross-bridge defect rate >15%, expand per-subdomain density to 35%") fires — the master-plan session should set per-subdomain sample density to 35% rather than the 25–30% baseline.

## Methodology

Per the approved plan, three pieces of evidence:

1. **Cross-bridge sample (15 of 71 edges, deterministic via md5 hash ordering)** — apply the SEP-anchored prompt template to each. Substantive candidate findings recorded with reasoning.
2. **Within-domain sample (5 edges from epistemology — densest subdomain at 72 edges)** — same SEP-anchored prompt.
3. **Topology pass (mechanical sweep)** — degree distributions per subdomain, top-10 hubs, dead-end leaf count, prerequisite-trace path lengths for three diagnostic targets.

All data pulled directly from live Supabase (paideia-dev project, PostgreSQL 17.6) via MCP tool `execute_sql`. The audit reads the consumed-graph state, not the migration source.

## Cross-bridge sample findings (15 of 71 edges)

Sample drawn deterministically: `ORDER BY md5(source_id || '|' || target_id)`. Edge classification key:
- ✅ Sound: SEP framing supports the prereq direction and the prereq-shape semantics.
- ⚠ Reversed/weak: direction questionable, or the prereq is more proximate elsewhere.
- ❌ Mis-typed (historical-not-pedagogical): edge encodes a thematic / historical / influence relationship rather than a `pedagogical_prerequisite` claim.

| # | Edge | Domains | Verdict | Reasoning |
|---|---|---|---|---|
| 1 | Expected Value → Social Contract Theory | service → political | ⚠ weak | Social contract theory (Hobbes 1651, Locke, Rousseau) historically predates Expected Value's formalization. EV is relevant to Rawlsian decision-theoretic framings but not to the general social-contract idea. SEP "Social Contract Theory" doesn't list EV as a prereq. |
| 2 | Counterexample → Gettier Problem | service → epistemology | ✅ sound | Gettier 1963 IS structured as a counterexample to JTB. Direction correct. |
| 3 | Principle of Bivalence → Dialetheism | service → logic | ✅ sound | Dialetheism is a denial of bivalence (true contradictions). Prereq direction correct. |
| 4 | Physicalism → Reductionism in Science | mind → science | ⚠ reversed/weak | Scientific reductionism (Nagel 1961, Oppenheim & Putnam 1958) has its own history that doesn't depend on philosophy-of-mind physicalism. The arrow may be reversed; physicalism in mind builds on or parallels scientific reduction, not the other way. |
| 5 | Scholasticism → Divine Command Theory | service → ethics | ❌ historical | Aquinas/Ockham scholastic context shaped DCT historically, but DCT is intelligible without scholasticism (Plato's Euthyphro is the classical anchor and predates scholasticism). The edge encodes a historical-influence relation, not a pedagogical prereq. |
| 6 | Expected Value → Dutch Book Argument | service → epistemology | ✅ sound | Computing the Dutch book loss requires EV. Prereq direction correct. |
| 7 | Inference Rule → Propositional Logic | service → logic | ✅ sound | Inference rules ARE the operative units of propositional logic. Direction correct. |
| 8 | Propositional Attitude → Proposition | mind → language | ❌ **REVERSED** | Per the node summaries themselves: a proposition is "what is asserted, believed, doubted"; a propositional attitude is "an agent's standing in a particular attitude... toward a proposition." Propositions are the antecedent concept; attitudes are toward them. The edge direction is pedagogically backwards. |
| 9 | Principle of Bivalence → Paraconsistent Logic | service → logic | ⚠ weak | Paraconsistent logic rejects the explosion principle (`P ∧ ¬P ⊢ Q`), not bivalence directly. Some paraconsistent logics retain bivalence; some are dialetheist. The closer prereq is `explosion_principle` (which exists in the graph). |
| 10 | Greek Atomism → Mereological Nihilism | service → metaphysics | ❌ historical | Greek atomism is a distant historical precursor of mereological nihilism. SEP "Mereology" / "Composition" doesn't structure the topic via Greek atomism. Pedagogically, modern mereological nihilism (Dorr, Sider, van Inwagen) is approached via composition, simples, and the Special Composition Question, not via Democritus. Historical-influence relation, not pedagogical. |
| 11 | Social Contract Theory → Contractualism | political → ethics | ✅ sound | Contractualism (Scanlon 1998) builds on the social contract tradition; the moral-theory variant requires the political-theory tradition's framework. Direction correct. |
| 12 | Vienna Circle / Logical Positivism → Tarski's T-Schema | service → language | ❌ historical | Tarski 1933's T-schema was developed in dialogue with Vienna Circle but is self-contained as a formal-semantic construction. SEP "Tarski's truth definitions" frames it via formal semantics, not via logical positivism specifically. Historical context, not pedagogical prereq. |
| 13 | Greek Atomism → Physicalism | service → mind | ❌ historical | Same shape as #10. Greek atomism is distant historical precursor of contemporary physicalism. The pedagogical chain to physicalism runs through mind-body problem and Cartesian dualism, not through the Presocratics. Historical-influence relation. |
| 14 | Aristotelian Four Causes → Essence (metaphysical) | service → metaphysics | ✅ sound (defensible) | Aristotelian formal cause is closely related to the essence/accident distinction; the four causes is one canonical entry point to the concept of essence. SEP frames essence as standalone but acknowledges Aristotelian heritage. Defensible as a prereq. |
| 15 | Set (Mathematical) → Kripke Semantics | service → logic | ✅ sound | Kripke semantics for modal logic uses possible worlds modeled as sets. Set theory is a real prereq. Direction correct. |

**Tally**: 6 sound + 1 defensible + 1 reversed + 4 historical-not-pedagogical + 3 weak/questionable = **8 substantive findings out of 15** (53%). The PROCEED threshold of ≥3 is exceeded by 2.7×.

**Pattern observation — cross-bridges from history-of-philosophy service nodes consistently encode historical-influence relations rather than pedagogical prerequisites.** Of the 4 historical-not-pedagogical cross-bridges in the sample (#5, #10, #12, #13), all four originate from "service" subdomain nodes that are themselves history-of-philosophy entities (Scholasticism, Greek Atomism, Vienna Circle). This is structural: the "service" subdomain mixes formal-tools (logic/math primitives) with "history terminators" per ADR 0052 product, and the history-terminator class is the source of the pattern.

This finding directly bears on the structural reopen for `cross_domain_dependency` (S-0075 rejection). The 4 of 15 historical-not-pedagogical cross-bridges projects to ~19 across all 71 — well above the plan's ≥10 ADR-warranting threshold for that memo. The master-plan session should expect to author a fresh ADR proposing either (a) a new edge predicate `historical_influence` (already reserved per PREDICATE_MANIFEST.md) be activated and these edges retyped, or (b) the service-subdomain history-terminator sub-class be split out (its own subdomain or removed from the prereq predicate's domain).

## Within-domain sample findings (5 of 72 epistemology edges)

| # | Edge | Verdict | Reasoning |
|---|---|---|---|
| 1 | Epistemic Justification → Coherentism | ✅ sound | Coherentism is a theory of justification; need the latter to understand the former. |
| 2 | Knowledge → Fallibilism | ✅ sound | Fallibilism is a thesis about knowledge — knowledge as concept is the prereq. |
| 3 | Epistemic Skepticism → Agrippan Trilemma | ✅ sound | Trilemma is a specific skeptical argument; skepticism is the framing. |
| 4 | Epistemic Justification → Epistemic Skepticism | ✅ sound | Skepticism challenges JTB; needs the justification concept. |
| 5 | Testimonial Knowledge → Social Epistemology | ✅ sound | Testimony is one canonical entry topic to social epistemology. |

**Tally**: 5 of 5 sound. **0 substantive findings.**

The contrast with cross-bridges is sharp: within-domain epistemology edges look clean; cross-bridges look problematic. This calibrates the audit's per-subdomain expectations — the master-plan session may rationally expect cross-bridges to be where defects concentrate.

## Topology pass

### Per-subdomain degree distribution

| Subdomain | Nodes | Avg in | Max in | Avg out | Max out | Dead-end leaves | Roots |
|---|---|---|---|---|---|---|---|
| mind | 57 | 1.39 | 4 | 1.32 | 8 | 26 (46%) | 1 |
| ethics | 56 | 1.29 | 3 | 1.23 | 8 | 28 (50%) | 1 |
| epistemology | 54 | 1.46 | 4 | 1.54 | 11 | 27 (50%) | 3 |
| metaphysics | 52 | 1.38 | 4 | 1.38 | 10 | 28 (54%) | 1 |
| language | 28 | 1.36 | 4 | 1.11 | 7 | 15 (54%) | 1 |
| political | 28 | 1.25 | 2 | 1.29 | 6 | 15 (54%) | 1 |
| aesthetics | 27 | 1.19 | 2 | 1.19 | 6 | 12 (44%) | 1 |
| science | 27 | 1.74 | 5 | 1.11 | 5 | 14 (52%) | 1 |
| logic | 26 | 2.08 | 6 | 1.35 | 5 | 9 (35%) | 0 |
| service | 25 | 1.12 | 3 | 2.92 | 7 | 0 (0%) | 4 |

**Observations**:

1. **Zero isolated nodes** across all subdomains — graph is connected per subdomain. No isolated-cluster red flag.
2. **Max degree never exceeds 11** (epistemic_justification's out-degree). The PROCEED threshold's "hub with degree >40" is comfortably not met. Graph is shallow-but-broad rather than hub-and-spoke.
3. **Dead-end leaf rates are uniformly ~50%** in major subdomains. Half of every subdomain's nodes are terminal (in-degree>0, out-degree=0). Pedagogically suspicious — in a healthy concept graph, terminal concepts exist but 50% feels high. Either (a) the graph has good leaf-coverage and these are appropriate end-of-chain concepts, or (b) the graph under-connects advanced concepts to their further dependents. The audit should test which.
4. **Service subdomain is the inverse** — 0% dead-end leaves, avg out-degree 2.92 (vs 1.1–1.5 elsewhere). Confirms service nodes are doing their work as widely-cited prerequisites.
5. **Logic has the highest avg in-degree (2.08)** — multiple subdomain concepts depend on common logic primitives. Healthy pattern.

### Top 10 hubs by total degree

| Rank | Node | Domain | In | Out | Total |
|---|---|---|---|---|---|
| 1 | Epistemic Justification | epistemology | 3 | 11 | 14 |
| 2 | Existence | metaphysics | 1 | 10 | 11 |
| 3 | Propositional Knowledge | epistemology | 3 | 8 | 11 |
| 4 | Causation | metaphysics | 4 | 6 | 10 |
| 5 | Physicalism | mind | 2 | 8 | 10 |
| 6 | Classical Logic | logic | 6 | 3 | 9 |
| 7 | Meaning (Linguistic) | language | 2 | 7 | 9 |
| 8 | Normative Ethics | ethics | 1 | 8 | 9 |
| 9 | Vienna Circle and Logical Positivism | service | 3 | 6 | 9 |
| 10 | Aristotelian Four Causes | service | 1 | 7 | 8 |

Hubs make pedagogical sense at first glance — the foundational concept of each subdomain shows up. Two service-subdomain history-of-philosophy nodes appear (Vienna Circle, Aristotelian Four Causes), which corroborates the historical-not-pedagogical cross-bridge pattern: history-of-philosophy nodes are routed to as cross-bridge sources for a non-trivial fraction of cross-domain edges.

The full audit should review each hub's incident edges (the plan's "hub audit" task in the hubs+traces evidence session) — an error in a hub propagates further than a leaf error.

### Three diagnostic syllabus traces

#### 1. "Understand Gettier counterexamples to JTB" (target = `gettier_problem`, epistemology)

Prereq tree (10 unique nodes, max depth 4):

| Depth | Nodes |
|---|---|
| 1 | Counterexample, Justified True Belief |
| 2 | Argument (Logical), Principle of Bivalence, Propositional Knowledge |
| 3 | Belief, Epistemic Justification, Truth, Truth Value |
| 4 | Evidence |

**Verdict**: Sound trace. Both depth-1 prereqs (Counterexample, JTB) are exactly what SEP "The Analysis of Knowledge" names as the antecedent concepts. The trace walks up through belief, justification, truth, propositional knowledge — the canonical cluster. 10 nodes, depth 4 — well within healthy range (5–20 nodes per the plan's threshold).

#### 2. "Understand modal realism" (target = `modal_realism`, metaphysics)

Prereq tree (7 unique nodes, max depth 5):

| Depth | Nodes |
|---|---|
| 1 | Possible Worlds |
| 2 | Abstract Object, Modality, Set (Mathematical) |
| 3 | Existence |
| 4 | Ontology |
| 5 | Metaphysics |

**Verdict**: Mostly sound, one issue. Possible_worlds is the right depth-1 prereq; modality, abstract objects, and set theory at depth 2 are reasonable. The trace bottoms out at "Metaphysics" (the discipline-label node) at depth 5 — granularity-mismatch finding (the trace treats a discipline name as a foundational concept rather than as a containing category).

#### 3. "Understand free speech" — TARGET ABSENT

Free speech / free expression has no node in the graph. Search returned only `speech_act` (philosophy of language). Substituted target: **`justice`**.

Justice prereq tree (1 unique node, depth 1):

| Depth | Nodes |
|---|---|
| 1 | Political Philosophy |

**Verdict**: TWO findings.

(a) **Coverage defect**: free speech absent. SEP has dedicated entries on "Freedom of Speech"; political philosophy with 28 nodes lacks one of its canonical topics. (Issue-class: enhancement.)

(b) **Graph-shape defect for substitute target `justice`**: Justice has only ONE upstream prereq, and that prereq is "Political Philosophy" — a discipline-label node. Justice's own summary calls itself "the central evaluative concept of political philosophy" yet does not depend on `equality_political`, `liberty_political`, `human_rights`, `desert_theory_political`, `distributive_justice`, or any of the other concepts SEP positions as logically prior to or constitutive of the concept of justice. The trace is suspiciously sparse for a major concept.

Bonus finding: Justice's ONLY *outbound* edge points to `morality` — i.e., the graph claims justice is a prerequisite to morality. SEP frames the relationship the other way: morality is the broader normative domain, justice is one major topic within it (especially political). Likely **REVERSED**.

## Audit-system input — what the build-time gates didn't catch

The Phase 5 build authors zero hard-fails across 16 routine sessions. The graph audit's 7 soft-warn categories (`undeclared_predicate`, `attribute_shape_inconsistency`, `missing_rigor_score`, `render_readiness_violation`, `synthetic_review_queue`, `orphan_leaf`, `suspicious_cross_domain_ratio`) all sat silent except `missing_rigor_score` (366 — expected per Phase 6 calibration). That clean signal is *evidence the gates weren't probing pedagogical fitness*, not evidence the graph is pedagogically sound. This gate session has now demonstrated that — at sample resolution.

`gate-feasible` audit-system findings the master-plan session should consider proposing as new validator soft-warns:

1. **Empty `evidence` field on edges** — 0 of 536 edges (cross-bridge or within-domain) carry any evidence text. The schema permits it, the migration discipline never required it, no soft-warn fired. Proposed soft-warn: `edge_evidence_empty` — fires per-edge when `evidence IS NULL` AND the edge is cross-domain (cross-domain edges carry higher pedagogical-claim load, per the plan's analysis).
2. **Discipline-label nodes acting as graph roots** — Political Philosophy, Metaphysics, Ontology act as terminal upstream prereqs in syllabus traces. Proposed soft-warn: `discipline_label_node_at_root` — fires when a node whose label matches the canonical name of a subdomain (Political Philosophy, Ethics, Metaphysics, etc.) has zero in-edges and serves as a prereq to multiple subdomain concepts. Mitigation requires either splitting the discipline-label into the constituent foundational concepts or removing the discipline-label-as-prereq pattern.
3. **Reversed prereq direction detectable from summary text** — `propositional_attitude → proposition` is the canonical example. Proposed soft-warn: `prereq_direction_summary_inconsistency` — fires when target's summary mentions source as antecedent. Implementation harder (NLP), but the master-plan session should triage whether the cost of catching ~5–10 reversed edges out of 536 is worth the implementation. Possibly defer.
4. **History-tradition nodes as `pedagogical_prerequisite` sources to non-history concepts** — the pattern that Greek Atomism, Scholasticism, Vienna Circle, Aristotelian Four Causes all source historical-not-pedagogical edges. Proposed soft-warn: `historical_node_as_prereq_source` — fires when a node tagged with the "history terminator" sub-class sources a `pedagogical_prerequisite` edge to a concept whose subdomain isn't `service`. This is gate-feasible because the history-terminator sub-class is identifiable (the 7 nodes named in this report). Sub-class tagging would need to be added to the node schema first.

`post-build-only` audit-system findings (categorically can't be caught at build time):

5. **Coverage gaps** (e.g., free speech absent from political) — require domain-knowledge comparison against SEP/Routledge canon. The post-phase production-audit pattern is exactly what catches these.
6. **Pedagogical-claim soundness for individual edges** (the SEP-anchored review's main yield) — requires the per-edge SEP comparison the production audit is designed to perform.

`already-covered-but-missed` discoveries (existing gate exists but didn't fire):

None surfaced by this gate. The existing gates are all syntactic; none target pedagogical-claim semantics, so there's no gate to fail-fire here.

## Forward inputs to the audit master-plan session

The master-plan session should:

1. **Set per-subdomain sample density to 35%** rather than the 25–30% baseline — the cross-bridge defect rate of 47% triggers the plan's stopping rule for sample expansion (>15%).
2. **Pre-allocate findings to the 4 audit-system-input proposals above** — they don't require any of the 12 evidence sessions to surface, since they're already known. This frees evidence sessions to focus on per-subdomain content review.
3. **Fold the structural-reopen for cross_domain_dependency / historical_influence into AUDIT-CB (cross-bridge census) scope explicitly** — the gate finding of 4 historical-not-pedagogical cross-bridges in 15 sampled (extrapolating to ~19 of 71) already exceeds the ≥10 ADR-warranting threshold. The census should classify each cross-bridge as pedagogical-OR-historical and produce the predicate-decision input.
4. **Adjust diagnostic-target list**: replace "free speech" with a target that exists (e.g., free will, distributive justice, social contract, democracy). Use this gate's report to predeclare which substitution is made.
5. **Plan to commit ≥1 fresh ADR memo or proposal**: history-of-philosophy node sub-class handling (predicate vs subdomain split), discipline-label-node handling, and possibly philosophy-of-religion readmission criteria refinement.

Total session count: gate (this session, S-0081) + master-plan (1) + 12 evidence (12) + closeout (1, possibly 2) = **15 sessions** before Phase 6 master plan. Add 1 for the cadence-audit-cycle that fires partway through (slots_since=14 at S-0091 would fire `health_check_overdue`).

## What this gate did NOT do (and is intentionally out of scope)

- Full census of all 71 cross-bridges (only 15 sampled). The full census is the master-plan's AUDIT-CB evidence-session scope.
- SEP-anchored review of any subdomain other than epistemology (5 sample). Per-subdomain reviews are the master-plan's evidence-session work.
- Filing GitHub Issues for individual findings. Per the plan, the closeout adjudicates dispositions; the gate records candidate findings and lets the master-plan session and the closeout decide which become Issues.
- Proposing concrete new validator soft-warn implementations. The audit-system-input synthesis at closeout is where those crystallize.

## Verification

Mechanical checks:

- 15 cross-bridge edges sampled (matches plan).
- 5 within-domain edges sampled from densest subdomain (epistemology, 72 edges; matches plan).
- Topology pass complete: per-subdomain degree distribution, top-10 hubs, dead-end leaf count, three syllabus-trace lengths recorded.
- Threshold rule applied; PROCEED conditions documented.
- Gate report committed to `engine/build_readiness/phase_5_production_audit_gate.md`.

Editorial:

- The user spot-checks 5–10 of the 8 cross-bridge candidate findings against the cited reasoning. If spot-check rejects more than 30% as "the AI didn't actually engage," the gate is treated as RESCOPE (insufficient methodology) per the plan's anti-failure mitigation rather than as PROCEED.
- The user adjudicates whether the topology-pass spirit-met PROCEED condition is sufficient given that the named magnitudes (degree >40, chain >25) didn't fire.
- The user adjudicates whether the master-plan session should pre-allocate the 4 audit-system-input proposals or rederive them.
