# Sub-concerns checklist (canonical reference)

> Derived from full read of both PDG papers. 66 sub-concerns across 5 lenses. Used by Phase B extraction agents (per-claim tagging) and Phase C lens-sweep agents (search list).
>
> **Every Phase B claim row must tag ≥1 sub-concern ID.** Every Phase C lens-sweep agent must address every sub-concern in its lens or justify absence explicitly.

## Lens 1 — Substrate / Schema (graph-level encoding)

The largest bucket. Concerns the papers raise about what the graph itself must represent. Current Paideia graph has the most underspecification here.

| ID | Concern |
|---|---|
| L1.1 | Edge type taxonomy beyond hard prerequisite: soft prerequisite, helpful bridge, co-requisite, contrastive link, misconception-remediation, example-of, supports, common-misconception-about, assessed-before, unlearning-required-before |
| L1.2 | Three-relation separation: pedagogical-dependence vs conceptual-relatedness vs historical-influence as **layered**, not flattened. Paideia currently has 1 and 3 but not 2 as a distinct layer. |
| L1.3 | Goal-relative dependency strength — the same edge has different necessity-level for different learning outcomes. Edge must be parameterized by `learning_outcome` or replicated per outcome. |
| L1.4 | Confidence model: `expert_confidence`, `trace_confidence`, `llm_confidence`, `disagreement_flag` — three independent sources, not a single property. |
| L1.5 | Provenance per edge: `source_text`, `course_context`, `version`, `reviewer`, `rationale`. |
| L1.6 | Provenance per node: `canonical_sources`, `approved_examples`, `mastery_evidence`. |
| L1.7 | Counterexamples as edge attribute — contestability mechanism. |
| L1.8 | Misconception encoding — as node-property OR distinct node-type. The current graph has nothing here. |
| L1.9 | Threshold-concept tag on nodes (transformative/troublesome marker). |
| L1.10 | Node-type taxonomy: threshold concept, bridge concept, disciplinary practice, text/excerpt, historical context, misconception, comparative lens, assessment task. |
| L1.11 | Audience/cohort tags per node: introductory, intermediate, advanced, majors/non-majors, multilingual. |
| L1.12 | Granularity tag on nodes (coarse / medium / fine). |
| L1.13 | Equity metadata per node: assumed background knowledge, jargon load, culturally specific references, language load. |
| L1.14 | Version history per node and per edge: date, course, cohort, revision notes. |
| L1.15 | Learner-state schema separate from graph: `mastery_probability`, `evidence_count`, `recent_errors`, `help_seeking_pattern`, `language_preference`. |
| L1.16 | Assessment linkage per node: `assessment_items`, `mastery_evidence`, link to formative checks. |
| L1.17 | Temporal / fade trajectory per scaffolding edge — guidance fades as mastery grows (expertise reversal). |
| L1.18 | Alternative-entry-route support — multiple legitimate paths to a node; the graph must not force one canonical sequence. |

## Lens 2 — Pedagogical Method (teaching use of the graph)

How the teaching application consumes graph structure to make pedagogical decisions.

| ID | Concern |
|---|---|
| L2.1 | Threshold concepts as load-bearing pedagogical primitives (Meyer & Land). |
| L2.2 | Bottleneck identification via Decoding the Disciplines (Middendorf & Pace) — student work / diagnostic discussion / Decoding interview surface bottlenecks BEFORE node/edge drafting. |
| L2.3 | Backward design ordering: outcomes → assessment → sequence — not field-survey ordering. |
| L2.4 | Scaffolding with explicit fade trajectory: contingent, fading, responsibility-transferring (Wood/Bruner/Ross + Vygotsky ZPD). |
| L2.5 | Novice-vs-expert differentiation: expertise reversal effect (Kalyuga) — same scaffold inverts in helpfulness as learner matures. |
| L2.6 | Misconception remediation as explicit pedagogy: e.g., "phenomenology = introspection", "deconstruction = anything goes", "historical perspective = sympathy with the past". |
| L2.7 | Unlearning commonsense meanings (Corrigan): disciplinary meanings of text/meaning/context/form/reading require active unlearning of folk meanings. |
| L2.8 | Multiple-entry-routes for ill-structured domains (Spiro cognitive flexibility) — single-lens sequencing is dangerous. |
| L2.9 | Recursive revisiting: humanities concepts are revisited at greater depth; the graph must support re-traversal not one-shot mastery. |
| L2.10 | Interdisciplinarity as bridge — short module on speech acts in a feminist-theory course is a bridge, not an origin. |
| L2.11 | Cognitive load management (Sweller): control element interactivity, isolate one threshold before adding another. |
| L2.12 | Formative assessment alignment per node — assessment is co-designed with the graph, not separate. |
| L2.13 | Goal-relative path selection: "explain X is not Y" vs "compare X and Y" select different prerequisite paths. |

## Lens 3 — LLM Integration & Architecture (LLM consuming the graph)

How an LLM interacts with the graph — system architecture, prompt discipline, role partitioning.

| ID | Concern |
|---|---|
| L3.1 | Instructional-spine-vs-adaptive-interface architecture: PDG carries pedagogical commitments, LLM operationalizes them, humans arbitrate. |
| L3.2 | Five-service architecture: graph store / content store / LLM orchestration / analytics / review layer. |
| L3.3 | Four sample workflows: instructor-authored core + LLM scaffolding / student-authored + LLM critique / adaptive-branching / trace-informed graph revision. |
| L3.4 | Role-checkpoint partitioning: instructor / LLM / student / reviewer roles with explicit checkpoint gates. |
| L3.5 | Prompt template discipline: JSON output, explicit "rules" section, "never mark an edge as required unless evidence supports instructional dependence". |
| L3.6 | Student-facing explainer template: one definition / one example / one contrast / one formative question / one why-this-matters sentence. |
| L3.7 | Hallucinated-STRUCTURE risk: false prerequisites silently mis-route learners; distinct from hallucinated facts. |
| L3.8 | Self-consistency for LLM output reliability (Pardos & Bhandari mitigation pattern). |
| L3.9 | No-silent-mutation rule: every LLM-proposed graph edit must be attributable, reviewable, reversible; logged with provenance. |
| L3.10 | Pre-registered edit policies: instructor pre-specifies which edit classes the system may suggest vs which require committee review. |
| L3.11 | LLM scoring as triage/drafting aid, NOT as unreviewed arbiter — consequential grading remains human. |
| L3.12 | Model-as-critic-not-judge framing in student-facing presentations. |
| L3.13 | Trace-informed candidate-edge generation with confidence + provenance + counterexamples + approval workflow. |
| L3.14 | Student-friendly subset exposure: local neighborhood only (target + immediate prereqs + misconceptions + assessments + alternative routes), NOT the full graph. |
| L3.15 | Tool-stack considerations: property-graph database (Neo4j) for rich edge attributes; the current Paideia stack (Postgres + Supabase) needs evaluation against schema-richness requirements. |

## Lens 4 — Adversarial / Governance / Bias / Equity

Failure modes, governance machinery, equity protections, regulatory alignment.

| ID | Concern |
|---|---|
| L4.1 | Cultural / canon bias: graph hardening one tradition's pathway as the default route; mitigation via alternative-pathway storage, tradition labels, contestation invitations. |
| L4.2 | Expert blind spot: experts forget that disciplinary meanings of common words are not obvious to students. |
| L4.3 | Multilingual fairness: LLM educational-task performance varies by language; lower-resource languages disadvantaged. |
| L4.4 | Subgroup-analysis discipline: differential gains by prior preparation, verbal ability, language background, major/non-major. |
| L4.5 | Anti-pathologizing-interpretive-styles: AI must not score legitimate alternative interpretive styles as "misconceptions". |
| L4.6 | FERPA/privacy/consent: minimize stored traces, separate identifiers from analytics, withdrawal-of-consent paths, retention limits. |
| L4.7 | NIST GenAI profile alignment: confabulation testing, source review, override monitoring, transparency reports. |
| L4.8 | Override logging: track when humans override AI decisions; publish periodic transparency reports on graph edits, override rates, subgroup discrepancies. |
| L4.9 | Contestability: every edge must be challengeable; provenance and counterexamples make contestability mechanically supported. |
| L4.10 | Opaque automation of curriculum authority: students must see when a path was altered by model inference vs instructor design. |
| L4.11 | Assessment distortion: AI scoring can smooth extremes, overscore, shift criteria; consequential decisions remain human. |
| L4.12 | Pluralism in humanities dependencies: distinguishing genuine bottlenecks from merely-traditional sequences is an open empirical problem — graphs should reserve room for legitimately divergent paths. |
| L4.13 | Connection to existing Paideia anti-bias mechanism per `feedback_anti_bias_implementation_discipline.md` and `feedback_audit_llm_inputs_for_bias.md`. |

## Lens 5 — Evaluation / Verification

Measurement discipline both for learner outcomes and for graph quality itself.

| ID | Concern |
|---|---|
| L5.1 | Learner-outcome measurement: threshold-concept tasks, comparative essays, transfer prompts, delayed retention, rubric dimensions tied to graph nodes. |
| L5.2 | Graph predictive validity: which predicted bottlenecks actually occurred, which "hard" edges proved unnecessary, where alternative paths worked. |
| L5.3 | Comparative experimental designs: PDG-only vs LLM-only vs PDG+LLM cluster-randomized or quasi-experimental. |
| L5.4 | Heterogeneity-of-treatment-effects analysis: differential gains by subgroup. |
| L5.5 | Process-quality measurement: discussion moves, causal explanation, argumentation, disciplinary vocabulary use, navigation patterns in LMS, annotation logs. |
| L5.6 | Design-based research as the realistic high-quality humanities design (rather than lab-controlled RCT). |
| L5.7 | Iterative cohort refinement: knowledge-space theory pattern — expert elicitation followed by empirical refinement, not frozen expert authoring. |
| L5.8 | Anomalous routing detection: instructor sees anomalous paths and can override routing decisions. |
| L5.9 | Validity criteria for the graph itself: expert agreement on edge labels, revision rates after review, disagreement concentrations by topic, downstream-learning improvement from trace-inferred edits. |
| L5.10 | Student-experience validity: perceived coherence, overload, agency, usefulness of optional bridges, sense of progression. |

---

**Coverage rule.** Every claim extracted in Phase B must tag ≥1 sub-concern ID. Every lens-sweep agent in Phase C must produce findings for every sub-concern in its lens, OR explicitly justify "no findings because…". Empty cells in either pass are visible defects.
