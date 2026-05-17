# Paideia Roadmap

> **A roadmap, not a contract.** Phase plans are tools — re-order if evidence warrants. When a phase plan changes, the prior version is marked superseded (per the ADR status conventions in `docs/operations/adr-authoring.md`), not deleted.

This document names every phase, its scope, its success criteria, and the architectural decisions it carries. Future sessions read this to know what's next without re-deriving the plan from history.

`STATE.md` names the *current* phase and the *next session's work item*. This file names the *whole arc*.

Phase headings carry **[ENGINE]** or **[PRODUCT]** markers per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md): engine phases author the AI build apparatus that constructs Paideia (session protocol, validators, build_plan scaffolding, infrastructure, tooling); product phases author Paideia content itself (seed graph, teaching layer prototype, UI). The repo is partitioned into `engine/` and `product/` subtrees per the same ADR.

---

## Phase 0 — Foundation **[ENGINE]**

**Setup, not build.** The session-protocol layer, industry-standard repo skeleton, decision-record discipline, and project memory get established. After Phase 0, every future session boots cold from `STATE.md` + the engine-memory substrate + the conventions in `CLAUDE.md` and `engine/operations/`.

**Three foundation sessions:**

- **S-0001** — structural foundation + retirement of obsolete pre-foundation source files. Top-level industry-standard files (this file, README.md, LICENSE, the engine state-of-record log layer (then `CHANGELOG.md`; renamed to `ENGINE_LOG.md` at S-0022 per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md); replaced by the per-session `engine/changelog/` directory at S-0198 per [ADR 0092](engine/adr/0092-per-session-changelog-directory.md)), SECURITY.md, STATE.md, HANDOFF.md), session/ + tools/ + pre-commit hook + slash command, supabase/migrations/ placeholders, repo reorganization into `docs/`.
- **S-0002** — procedural layer + memory-substrate indexing + CONTEXT.md split. CLAUDE.md + 11-file `docs/operations/` library + `docs/MISSION.md` + `docs/CROSS_REFERENCES.md`. (Original memory substrate replaced by engine_memory per ADR 0091 at S-0188 → S-0193.)
- **S-0003** — ADR collection (22 ADRs absorbing the 12 working commitments + the 8 entries from the transitional `design-reasoning.md` + 2 architectural decisions that emerged in the S-0001 plan conversation, ADRs 0016 and 0022). `adr/README.md` indexes the collection; full Nygard guidance and status conventions live in `docs/operations/adr-authoring.md`. `design-reasoning.md` retired at S-0003 close.

**Phase 0 closes when:** a fresh Claude Code session can type `Start Engine` (or `/start-engine`), boot cold from `STATE.md` + engine_memory, claim the next slot via the eager-claim ritual, do its work, and close cleanly with audit + commit + push — without human briefing.

---

## Phase 1 — Contract Lock **[ENGINE]**

**Output:** every remaining design ambiguity that would propagate into the seed graph is settled, audit-checked, and durable.

### 1.1 Prompt-pack sessions — all dispositioned at S-0041

The 14-session prompt pack at [`product/docs/prep-paideia-prompt-pack.md`](product/docs/prep-paideia-prompt-pack.md) (path moved from `docs/` to `product/docs/` in S-0024 per [ADR 0037](engine/adr/0037-engine-product-wall-and-changelog-rename.md)) was authored at S-0001 as a deliberation queue. Sessions 1-8 closed pre-Foundation. Per the S-0041 disposition pass:

- **~~Session 9 — Engagement Depth Aggregation.~~** Closed at S-0004 (consumed by [ADR 0023](product/adr/0023-engagement-depth-aggregation.md)).
- **~~Session 10 — Decay Parameter Verification.~~** Retired at S-0041 — superseded by Phase 7+ empirical verification once the learner model runs against real telemetry. The synthetic-arithmetic walkthroughs the prompt requested are lower-value than ongoing calibration against real event streams.
- **~~Session 11 — Historical Maximum Tracking.~~** Closed at S-0006 (consumed by [ADR 0025](product/adr/0025-historical-maximum-tracking.md)).
- **Session 12 — Fork Maintenance Timeline.** Open with concrete decide-trigger (S-0041 amendment): the first session where a DeepTutor-divergence question arises OR the first Phase 7 infrastructure session, whichever comes first. Tension entry remains in `product/docs/tensions.md`.
- **~~Session 13 — Gamification & Milestone Tone.~~** Closed at S-0016 (settled by [ADR 0033](product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](product/adr/0034-discovery-planning-engagement-triad.md), and the [ADR 0027](product/adr/0027-rendering-policy-prompt-layer-contract.md) S-0016 voice-discipline extension).
- **Session 14 — Media Edge Quality.** Open with phase-pinned decide-by trigger (S-0041 amendment): the first Phase 7 session that proposes adding media edges to the schema. Tension entry remains in `product/docs/tensions.md`.

**Net status (S-0041):** 12 of 14 prompts closed (8 pre-Foundation + 4 dispositioned in S-0004/S-0006/S-0016/S-0041). 2 prompts remain open with phase-pinned decide-by triggers (Sessions 12 and 14). The prompt-pack file is now historical reference plus a decide-trigger surface for the two open prompts; it does not appear on the active near-term work queue.

### 1.2 Author rendering policy and sibling commitments

- **`AGENT_INSTRUCTIONS.md`** — standalone rendering-policy file extracted from `docs/pedagogy.md`. Forbidden tokens (mastery-state names, prerequisite-edge framing, evidence-event references, scaffolding-distance language, weight/confidence/provenance exposure, graph_version references, tension-log mechanism, mastery-verification mechanic, machinery self-reference). Surviving tokens (concept names, domain-area names, thinker names, text titles, cross-domain connections). Citation rules (named structural units, no fabricated quotations). Uncertainty posture. Scope discipline (purpose-not-topic discrimination). Tension emission policy operationalizing the `pattern_observed` writing constraint. Worked example (gradeable test artifact for Phase 7 success criterion).
- **ADR 0027** — rendering policy as the prompt-layer contract. The output-side half of the bidirectional teaching-surface contract.
- **ADR 0028** — input-side scope is structural, not prompt-policed. The input-side half of the bidirectional contract. Three bounded input contexts (concept engagement, diagnostic, close reading); purpose-not-topic discrimination within bounded contexts; exit affordance as the structural alternative to general chat.
- **ADR 0029** — personal financial cost ceiling as operating constraint. Cost protection is a precondition (not a feature) for opening the system to non-builder users; mechanism mandated, ceiling value held in private operational configuration; soft walls degrade rather than terminate (preserving concept-engagement integrity).
- **Tension entries** opened for sub-decisions deferred to downstream phases: OQ-WALL-BEHAVIOR (soft-wall degradation ladder; decide-before Phase 8), OQ-CONTEXT-COMPRESSION (token-amplification mitigation; decide-before Phase 7), OQ-PEDAGOGY-INFERENCE-LOCUS (rule layer vs. distributed inference; revisit trigger pinned to inference-registry size and operational complaint surfacing).
- **[`docs/pedagogy/inferences.md`](product/docs/pedagogy/inferences.md)** — pedagogical inference registry stub. Cheap intermediate step before deciding whether to build a dedicated rule layer per OQ-PEDAGOGY-INFERENCE-LOCUS.

See also: [ADR 0026](product/adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0027](product/adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0028](product/adr/0028-input-side-scope-structural-not-prompt.md), [ADR 0029](product/adr/0029-personal-financial-cost-ceiling.md).

### 1.3 Add `confidence_level` to node schema

Add `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`) to the node schema in `docs/architecture.md`, orthogonal to existing `provenance` and numeric `confidence`. Synthetic nodes are first candidates for self-correction review.

### Phase 1 success criteria

- Sessions 9, 10, 11 closed; sessions 12-14 explicitly tagged deferred in `docs/tensions.md`
- `AGENT_INSTRUCTIONS.md` exists and a worked example passes when fed to Sonnet against a stub graph
- ADRs 0027 (rendering policy), 0028 (input-side scope structural-not-prompt), and 0029 (personal financial cost ceiling) land with Status: Accepted
- `confidence_level` column added to the node schema (architecture.md)
- All Phase 1 ADRs land in `adr/` with Status: Accepted

---

## Phase 1.5 — Mission Realignment Overhaul **[ENGINE]**

**Output:** the contract layer is realigned around the project's core value claim — *filling the gap where a self-learner has no teacher* — by dropping the globe / mastery-glow / cross-domain-tendrils / trophy / "knowledge as a world" UI metaphor that was drifting attention away from the discovery / planning / mastery-gating value, and committing the replacement product structure (Discovery → Planning → Engagement triad) plus the broadened Apple platform scope (iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad). This is **realignment, not rebuild** — the pedagogical dependency graph, the AI instructor model, the bring-your-own-book close reading, the mastery model, the privacy posture, and the cost ceiling all survive intact.

### 1.5.1 Mission realignment and globe/reward closure

- ADR 0033 contracts the mission realignment: structured guidance for self-learners. Records the corruption vector (the globe and reward systems were UI-layer optimizations that drifted attention away from the discovery / planning / mastery-gating value claim) and closes obsolescence of globe-as-home, mastery-glow, cross-domain-tendrils, trophy framing, and "knowledge as a world" metaphor. Names the survivors explicitly: graph + instructor; BYOB; bounded engagement contexts; mastery model.
- ADR 0018's flat-domain-tags + community-detection algorithm is retained as a graph-analysis primitive (discovery-surface concept clustering, syllabus organization heuristics, graph-quality audits); the globe-rendering use case is removed from its Decision and Consequences.
- `docs/MISSION.md` "What this is" is framed around the structured-guidance gap. Cross-domain porosity preserved.

### 1.5.2 Discovery / Planning / Engagement triad architecture

- ADR 0034 contracts the Discovery / Planning / Engagement triad as the primary product structure. Discovery-side affordances: AI conversational onboarding parallel with a browseable concept catalog organized by domain/topic. Planning-side affordances: syllabus-as-plan, prerequisite gating, quiet completion markers, current/active syllabus view. Explicit foreclosures: no separate trophy surface, no globe, no game-world rendering, no library/bookshelf as a third primary surface (mastered concepts surface contextually within syllabi).
- `docs/ui-architecture.md` carries Discovery Surface, Planning Surface, and Engagement Surface sections. Cross-domain edges remain first-class graph data; their UI rendering is **bridge surfacing in context** during engagement and planning.
- `docs/session-lifecycle.md` preserves Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, and Mastery Verification Through Downstream Teaching's organic-escalation framing. Concurrent Syllabus Limit (hard cap of five) remains.

### 1.5.3 Multi-platform Apple expansion

- ADR 0035 contracts the multi-platform Apple expansion. Commitment 1 reads: *Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. No Android, no web app, no native AppKit/Catalyst Mac app.* Commitments 2–6 hold the personal-project disposition: cost-priced subscription, no free tier, builder eats API costs, no BYOK / no institutional regime, fixed annual operating subsidy budget, polish-static / maintenance-minimum. *(Phase 1.5 historical narration of what ADR 0035 contracted at the time. [ADR 0035](product/adr/0035-multi-platform-apple-expansion.md) was superseded by [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) at S-0128 — commitments 1 and 6 preserved; commitments 2 and 4 inverted; commitments 3 and 5 retired with the cost-ceiling mechanism. The current operative disposition lives in ADR 0065 and is summarized in the Strong working commitments item 2 at the bottom of this file.)*
- ROADMAP Phase 9 success criteria carry the triad + multi-platform plan; cost-cap mechanism, no general chat surface, exit affordance, delete-account, and data-export are first-class UI primitives.
- `docs/business.md` Pricing and Distribution row reads "Apple App Store. iPhone + iPad first-class; Mac via Designed-for-iPad."

### 1.5.4 Rendering policy revision and secondary docs sweep

- ADR 0027's forbidden-token enumeration covers globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language in agent output.
- `AGENT_INSTRUCTIONS.md` mirrors the extended enumeration; the worked example is consistent.
- ADR 0012 names the freshman-defaults builder-bias-protection role explicitly; ADR 0014 carries no residual cohort framing.
- Secondary docs (`docs/pedagogy.md`, `docs/architecture.md`, `docs/learner-model.md`, `docs/CROSS_REFERENCES.md`, `README.md`, `docs/prep-paideia-prompt-pack.md`, `docs/pedagogy/inferences.md`, `docs/infrastructure.md`) carry no residual globe / mastery-glow / tendril / trophy / colored-trail / "knowledge as a world" references. Tension entries for globe/trophy carry `Resolved` markers per the project's tension-resolution discipline.

### 1.5.5 Inward-document expression contract

- ADR 0036 contracts the project's second expression contract — kindred tool to AGENT_INSTRUCTIONS.md (the rendering policy in ADR 0027), separately scoped to inward-facing documentation. The contract's posture: governed documents describe present truth in present-tense declarative prose; cross-references to ADRs are bibliographic (end-of-section "See also" pointers); authorship history, supersession narration, and per-session revision markers belong in the four-layer trace system (ADRs, engine/changelog/ entries per ADR 0092, engine_memory, git).
- Operational surface lives at [`docs/operations/document-voice.md`](engine/operations/document-voice.md). Scope: the `docs/` tree, root-level project files, ADRs in non-Superseded status, AGENT_INSTRUCTIONS.md. Exempt: STATE.md, `engine/changelog/` entries, `session/archive/*`, ADRs in Superseded status, resolved `docs/tensions.md` entries. ROADMAP.md is governed with three-speech-acts handling: phase scope and commitments are governed; date-stamp markers and supersession narration migrate to the per-session changelog entry and git.
- `docs/business.md`, `docs/architecture.md`, `docs/MISSION.md`, `docs/content-strategy.md`, `AGENT_INSTRUCTIONS.md`, `docs/tensions.md` open entries, and `adr/README.md` orientation prose carry the contract's voice. ROADMAP.md (this file) carries the contract's voice with three-speech-acts handling; the four-layer trace carries the production trace.

### Phase 1.5 success criteria

- ADRs 0033, 0034, 0035, 0036 land at Status: Accepted; ADR 0032 Status reads `Superseded by ADR 0035`.
- `docs/ui-architecture.md` and `docs/session-lifecycle.md` carry no residual globe/glow/tendril references; `docs/MISSION.md` "What this is" is framed around structured guidance for self-learners.
- `git grep -i "globe\|mastery glow\|tendril\|trophy\|colored trail\|knowledge as a world\|Globe Navigation Model"` returns matches only where the term names what is foreclosed (ADR 0033, ADR 0027, ADR 0018), in superseded artifacts (ADR 0032), or in dated journal layers (`engine/changelog/`, `session/archive/*`).
- Phase 9 success criteria below carry the triad + multi-platform plan; Android / web references absent.
- Inward-facing project documents carry the document-voice contract; the four-layer trace carries date-stamps and supersession narration.
- Phase 2 (Build Plan Scaffolding) opens with the realigned, voice-clean contract as input.

See also: [ADR 0027](product/adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0033](product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](product/adr/0034-discovery-planning-engagement-triad.md), [ADR 0035](product/adr/0035-multi-platform-apple-expansion.md), [ADR 0036](engine/adr/0036-expression-contract-for-inward-documents.md), [`docs/operations/document-voice.md`](engine/operations/document-voice.md).

---

## Phase 2 — Build Plan Scaffolding **[ENGINE]**

**Output:** a `build_plan/` directory naming the chunked authoring sessions for Phases 3-9, and the working contract for each session. Plus the standing build-readiness gate protocol per [ADR 0040](engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md) that precedes every substantive build session from Phase 3 forward.

- `build_plan/MANIFEST.md` — orientation, session schedule, phase mapping
- `build_plan/00_preamble.md` — orienting prose
- `build_plan/00_session_schedule.md` — every session by ID with scope, source documents, output target, budget tier
- `build_plan/P_0_contract_lock.md` — retroactive Phase 1 record
- `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` — per-phase chunks
- `engine/build_readiness/<phase>_<chunk>.md` — build-readiness reports authored by gate sessions, consumed by build sessions at boot, per [ADR 0040](engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md).

This file (`ROADMAP.md`) names the phases at a high level. `build_plan/` names the per-session work within each phase. `engine/build_readiness/` carries the per-build-session decision input.

---

## Phase 3 — SQL Schema Implementation **[ENGINE]**

**Gated by** [`engine/build_readiness/phase_3_sql.md`](engine/build_readiness/phase_3_sql.md) — the build-readiness report that resolves Tier 1 decisions in advance and documents Tier 2 column shapes / constraint forms / indexes for the build session to implement without re-deciding. Per [ADR 0040](engine/adr/0040-build-readiness-gate-before-substantive-build-sessions.md), every substantive build session reads its gate report at boot.

**Output:** Postgres schema deployed to Supabase via versioned migrations.

Translate `docs/architecture.md` and `docs/learner-model.md` schemas into:

- `users` table — local mirror of `auth.users` (Supabase Auth) trigger-populated; FK target for every learner-state cascade per [ADR 0031](product/adr/0031-erasure-mechanism-and-individual-only-regime.md) (T1-A in the gate report)
- `nodes` table — id, label, domain[], summary, teaching_notes, aliases[], rigor_score_computed, rigor_score_adjustment, **confidence_level** (per Phase 1.3), confidence (numeric), provenance, status, superseded_by, graph_version_added, timestamps
- `edges` table — source_id, target_id, type, weight, confidence, provenance, evidence, graph_version_added
- `learner_events` table — event-sourced log per `docs/learner-model.md`
- `mastery_snapshots` table — cached mastery state
- `tension_log` table — per `docs/self-correction.md`; JSONB enum vocabularies per [`product/seed-graph/migrations/TENSION_VOCABULARY.md`](product/seed-graph/migrations/TENSION_VOCABULARY.md)
- `settings` — graph_version counter (initialized at 1; increment contract per ROUTING.md)

Stack: Supabase migrations at `product/seed-graph/migrations/0001_*.sql` and forward.

### Phase 3 success criteria

- `supabase db push` applies the migrations cleanly to dev DB
- `\d+ nodes` shows expected columns including `confidence_level` with CHECK constraint
- Migration rollback works (verified per the rollback test sequence in the gate report T2-H)
- `tension_log` and `learner_events` schemas conform to ADR 0026 (`exchange_summary` as JSONB-with-named-fields with v1 vocabularies enforced as CHECK constraints; `learner_events.context` as structured columns; no free-text grab-bags); RLS on with v1 policies for every learner-state table; OQ-PRIVACY-A erasure mechanism and OQ-PRIVACY-B institutional-regime column reservation already settled by [ADR 0031](product/adr/0031-erasure-mechanism-and-individual-only-regime.md)
- Every Tier 2 decision in [`engine/build_readiness/phase_3_sql.md`](engine/build_readiness/phase_3_sql.md) is implemented exactly as documented; the build session does not re-decide

---

## Phase 4 — Graph Validation Utility (per ADR 0016) **[ENGINE]**

**Output:** real-time graph validation utility extending `tools/validate.py`'s extension point. Wired to the pre-commit hook so seed-authoring sessions cannot commit without passing audit.

### 4.1 Flesh out the extension point

`tools/validate.py`'s `validate_graph()` stub function becomes the live audit. Connects to the live Supabase DB via `psycopg`. Read-only.

**Hard-fail (exit 2):**
- Duplicate node IDs
- Dangling edge references (source_id or target_id not in nodes)
- Cycles in prerequisite-edge subgraph (SCC detection via Kosaraju)

**Soft-warn by category (printed to stderr):**
- Orphan leaves (zero outbound + zero inbound prerequisite edges)
- Missing `summary` or `teaching_notes`
- Suspicious cross-domain edge ratios (e.g., epistemology subdomain with > 40% cross-domain inbound — likely a missing service node)
- **Undeclared predicates** (edge.type not in the canonical PREDICATE_MANIFEST.md — catches schema drift across sessions)
- **Attribute-shape inconsistency** (nodes of same domain with materially different attribute coverage)
- Missing rigor score components (rigor_score_computed null when topology data is sufficient)
- Render-readiness violations (labels containing scaffolding tokens — "service_node", "synthetic", "stub")
- `confidence_level: SYNTHETIC` nodes flagged for review queue

**Modes:**
- `--validate-only` (default) — read-only DB queries, per-category counts, exit 0/1/2
- `--export-snapshot path/to/snapshot.json` — write current-state snapshot for offline review

No write-back. DB writes happen via migrations only.

### 4.2 Flesh out `supabase/migrations/ROUTING.md`

Numeric prefix scheme: `00NN` schema, `001N` epistemology, `002N` ethics, `003N` metaphysics, `005N` service nodes, `006N` cross-domain edges. Per-session narrative paragraphs (~200-400 words each) documenting what each migration added and why.

### 4.3 Flesh out `supabase/migrations/PREDICATE_MANIFEST.md`

Canonical edge-type registry: `prerequisite`, `enables`, `informed_by`, `cross_domain_dependency`, etc. Adding a new predicate is a material change recorded via a per-session changelog entry (`material_change_class: schema`), requiring a new manifest entry in the same session.

### 4.4 Flesh out `docs/operations/seed-chunked-authoring.md`

Per-session migration workflow: read SEP article → identify concepts at granularity principle → write `00NN_seed_<subdomain>_partN.sql` migration → `supabase db push` → `tools/validate.py` → fix in-session → commit.

### Phase 4 success criteria

- `validate.py --validate-only` runs end-to-end against the live DB in <3s on a 100-node test seed
- New predicate not in PREDICATE_MANIFEST.md surfaces as a soft warn
- Deliberately-broken edge ref triggers hard-fail with exit 2
- Pre-commit hook blocks seed-authoring commits that fail audit

---

## Phase 4.5 — Input Dataset Survey (for Phase 5 seed authoring) **[PRODUCT]**

**Output:** a tiered survey of external datasets useful as **cross-reference inventories and prerequisite-shape priors** for Phase 5 seed authoring. Lands as a new section in [`docs/content-strategy.md`](product/docs/content-strategy.md) ("Cross-Domain Reference Inventories — Survey") with per-candidate assessment against the five usability axes.

This phase **does not** revise the Generative Graph Independence position (`business.md`) or the SEP-as-structural-reference posture (`content-strategy.md`). Concept nodes and prerequisite edges remain generatively seeded; the survey gives that generation pass better starting inventories per domain and surfaces any prerequisite-shaped graph priors worth consulting.

### Five usability axes (constrain every candidate)

1. **Graph-shape orientation.** Prerequisite-shaped vs. influence / agreement / dialectical / citation / co-occurrence. Filter aggressively — influence-shaped data drags the modeler dialectical even when intended only as vocabulary.
2. **License.** "Consultable for personal use" is the operative bucket. The graph is generated parametrically; external sources serve as inventories and cross-reference checks consultable for personal use. Surveys note license terms for completeness but do not turn on an ingestable / mineable distinction, because nothing the project consumes is consumed for commercial purposes.
3. **Form.** Structured graph data vs. structured taxonomy/tags vs. long-form prose. Long-form prose has low novel value — already parametrically accessible to Sonnet/Opus.
4. **Coverage breadth.** Single-domain vs. cross-domain native. Cross-domain porosity makes cross-domain-native sources disproportionately valuable.
5. **Depth uniformity / methodology transparency.** Sources that disclose uneven depth (Önduygu's "some philosophers more beginner-level…") are higher-trust than sources that don't.

### Tiered survey scope (not exhaustive)

Decision-quality return plateaus quickly past the prerequisite-shaped tier. Survey depth is proportional to graph-shape value.

- **Tier 1 — exhaustive on prerequisite-shaped graphs.** Small, load-bearing, novel value. Known candidates to evaluate: Khan Academy knowledge map (math-dense, pedagogical-prerequisite, license verification needed); ConceptNet's `Prerequisite` relation (CC BY-SA); university CS curriculum prerequisite graphs (often JSON-public, narrow); Mathlib / Metamath dependency graphs (literally logical-prerequisite, math-only).
- **Tier 2 — comprehensive on per-domain cross-reference inventories outside philosophy.** For each non-philosophy domain Paideia plans (history, theology, literature, economics, poetry, political theory, law, psychology — per `docs/expansion.md`), identify the SEP/Oxford-dictionary equivalent. Per-domain license check.
- **Tier 3 — representative sample on bibliographies and citation graphs.** Önduygu's reference page (~800 works), Open Syllabus Project, Semantic Scholar / OpenAlex. Reading-list and co-occurrence priors, not content.
- **Tier 4 — minimal on long-form prose references already parametrically accessible.** SEP, IEP, Wikipedia. Note as *consult-during-validation*, not as survey targets.

### Önduygu philo-browser as worked example

Deniz Cem Önduygu's `denizcemonduygu.com/philo` (Western philosophy graph: ~800 works, ~400+ authors, propositions linked by green/red agree-or-disagree edges, twelve-year autodidact project) is the worked example that surfaced the axes. Specific to Paideia:

- **Propositions+edges layer is graph-shape-incompatible** (dialectical, not prerequisite). Consciously not consulted during seed authoring per the contamination caution in axis 1.
- **Tag layer (named -isms, theses, paradoxes) is usable as a concept-vocabulary checklist** during Phase 5 Western-philosophy authoring.
- **Reference list is usable as a starting reading list** — bibliographic facts are clean territory under the all-rights-reserved shield.
- **Author's own caveat** — "Browsing this visual summary cannot substitute reading a good book of history of philosophy" — is rhetorical prior art for [ADR 0011](product/adr/0011-no-hosted-copyrighted-material.md) and the BYO-book commitment.
- **Calibration evidence:** twelve disciplined autodidact years produced ~800 works at uneven depth. Phase 5 throughput projections should be set against this prior, not against optimistic LLM-augmentation assumptions.

### Phase 4.5 success criteria

- `docs/content-strategy.md` has a new "Cross-Domain Reference Inventories — Survey" section that names the five axes, the four tiers, and the per-tier candidate assessments
- Tier 1 (prerequisite-shaped) is exhaustive: every known candidate is named, license-checked, graph-shape-evaluated, and either tagged for Phase 5 consultation or explicitly excluded with reason
- Tier 2 has at least one named candidate per non-philosophy domain in `docs/expansion.md`
- The survey output cross-links to Phase 5.2 ("Source approach") so seed-authoring sessions consult it
- No survey finding requires revising "Generative Graph Independence" or the SEP-structural-reference posture; if one does, it lands as an ADR in this phase

### Phase 4.5 scope discipline

The survey is **research and recording**, not commitment. Specific dataset *adoption* decisions (e.g., "use ConceptNet's Prerequisite relation as Tier-1 input for the math service-node subdomain") are deferred to the Phase 5 sessions that consume them; if such a decision involves a non-trivial tradeoff, it lands as an ADR at that point. The Phase 4.5 deliverable is the inventory, not the bindings.

---

## Phase 5 — Seed Graph Build (parallelizable) **[PRODUCT]**

**Output:** concept-level seed graph across philosophy subdomains. Hundreds of nodes per subdomain. Cross-domain edges first-class.

Per the chunked-authoring + eager-claim discipline, multiple subdomain sessions run concurrently without merge conflicts. This is the **first natural parallel-work moment** and the **Paperclip orchestration trial moment.**

### 5.1 Subdomain sessions

The subdomain decomposition is settled by [ADR 0052](product/adr/0052-phase-5-philosophy-subdomain-decomposition.md): **9 subject subdomains plus service nodes plus cross-bridges plus closeout**. Per [ADR 0051](engine/adr/0051-routine-mode-and-engine-loop.md)'s routine-mode architecture, sub-sessions execute against [`engine/session/auto_target.json`](engine/session/auto_target.json) authored by the S-0045 master plan session.

**Subject subdomains:**

- **Epistemology** — start here; the deprecated v0.2 prototype was epistemology-focused so judgment is calibrated. Pre-split at master-plan time into core (P5-01a) and specialized (P5-01b) per [`auto_target.schema.md:149`](engine/session/auto_target.schema.md) session-sized-task discipline.
- **Metaphysics** — pre-split into core (P5-02a) and specialized (P5-02b)
- **Logic** — *philosophical logic* (modality, conditionals, paradox, vagueness, paraconsistent, deontic). Formal-logic primitives belong to service nodes.
- **Ethics** — pre-split into metaethics+normative (P5-04a) and applied (P5-04b)
- **Political philosophy**
- **Aesthetics**
- **Philosophy of mind** — pre-split into core (P5-07a) and consciousness/specialized (P5-07b)
- **Philosophy of language**
- **Philosophy of science**

**Operational tasks:**

- **Service nodes** (P5-10) — formal-logic primitives, mathematical prerequisites, history terminators
- **Cross-bridges** (P5-11) — cross-domain edges pass; depends on all 9 subject subdomain tasks plus service nodes; runs after subdomain interiors stabilize
- **Closeout** (P5-12) — Phase 5 close: per-session changelog entry + STATE.md update + `engine/build_readiness/phase_5_closeout.md` + optional close ADR

**Out of scope, deferred** (per [ADR 0052](product/adr/0052-phase-5-philosophy-subdomain-decomposition.md)):

- **Philosophy of religion** — historically a philosophy subdomain; cosmological-argument-shaped concepts fold into metaphysics for this MVP. Class-boundary admit-criterion in ADR 0052 governs future readmission.
- **History of philosophy as a separate subdomain** — per [ADR 0008](product/adr/0008-concept-nodes-not-thinkers.md), thinkers are not nodes; historical concepts surface across the 9 subdomains via the cross-bridges pass.

**16 explicit tasks total.** [`engine/session/auto_target.json`](engine/session/auto_target.json) carries the canonical task list with per-task `scope_lock`, `criteria`, and `depends_on`. `max_sessions: 18` (count + 2 for HANDOFF retries; tasks pre-sized to fit one routine session each since routine-mode has no live context-pressure signal — the discipline is task-sizing at master-plan time, not runtime adaptation).

### 5.2 Source approach

- **SEP** as **structural reference only** (concept inventory, cross-references) — not a content corpus. SEP does not become hosted text.
- **Wikipedia** for accessible summaries (CC BY-SA — permits use with attribution).
- **Generate first-pass prerequisite edges via Claude;** mark `confidence_level: INTERPRETED` until validated against learner outcomes or expert review.
- **Phase 4.5 survey output** ([`docs/content-strategy.md`](product/docs/content-strategy.md) "Cross-Domain Reference Inventories — Survey") names the per-domain inventories and any prerequisite-shaped graph priors worth consulting at session start. Sessions consult it as a checklist; specific adoption decisions land as ADRs in-session if they involve non-trivial tradeoffs.

### 5.3 Per-session migration workflow

Per `docs/operations/seed-chunked-authoring.md`:

1. Session reads target subdomain's SEP article structure, identifies in-scope concepts at the granularity principle (one mastery state per concept)
2. Session writes new migration file `00NN_seed_<subdomain>_partN.sql` with INSERT statements, `graph_version_added` set to current settings counter, explicit `confidence_level`
3. Session runs `supabase db push`
4. Session runs `tools/validate.py --validate-only` against post-push DB
5. Hard-fails fix in-session; soft-warns recorded in session outcome_summary per category
6. Session closes, commits the migration file (per-session changelog entry written under `material_change_class: schema`)

### 5.4 Routine-mode dispatch

Phase 5 sub-sessions run unattended via routine-mode per [ADR 0051](engine/adr/0051-routine-mode-and-engine-loop.md). The S-0045 master plan session authored [`engine/session/auto_target.json`](engine/session/auto_target.json); subsequent routine-mode sessions read it at boot, pick the next eligible task per `depends_on` ordering, run plan-then-scope-check, execute, and close. Paperclip orchestration was rejected at S-0044 (ADR 0051 Alternatives Considered); routine-mode replaces it.

### Phase 5 success criteria

- Each subdomain task closes with zero hard-fails from `engine/tools/validate.py`
- Soft-warn counts recorded per category in routine-session `outcome_summary`
- Migration files atomically attributable to the routine session that wrote them via the session's per-session changelog entry
- Cross-session schema drift detected by the predicate-manifest audit
- All 16 tasks in [`engine/session/auto_target.json`](engine/session/auto_target.json) reach `complete` status (or HANDOFF entries adjudicate the remainder if `max_sessions: 18` is reached)
- Phase 5 closeout task (P5-12) lands `engine/build_readiness/phase_5_closeout.md` summarizing per-subdomain coverage, soft-warn telemetry, and the predicate registry's final state

---

## Phase DEC.1 — Retrieval / Mastery-Inference Architecture Decisions **[ENGINE]**

**Sits between Phase 5 and Phase 6.** After the seed graph is mature, retrieval-shape decisions become testable; before the teaching layer is built, they're load-bearing.

**Decisions to settle** (each tracked as an open tension in `docs/tensions.md` from S-0001 onward):

- **OQ-DEC1-A:** Server-side mastery computation — confirm or revisit?
- **OQ-DEC1-B:** Two-hop neighborhood retrieval shape for teaching session context
- **OQ-DEC1-C:** Embedding strategy for entity resolution — pgvector + which embedding model
- **OQ-DEC1-D:** Chunk-resolver index for SEP onward-reading vs direct SEP URL pointers

Each decision lands as an ADR with Status: Accepted and a Phase-6 implementation tag.

---

## Phase 6 — Self-Correction Pipeline **[ENGINE]**

**Output:** tension log + Opus batch review pipeline operational.

Implements `docs/self-correction.md`:

- Tension log schema in Postgres (Phase 3)
- Sonnet teaching-side: emit tension records (`struggle_unresolved`, `unexpected_ease`, `spontaneous_connection`, `source_ineffective`, `mastery_contradiction`)
- Opus reviewer: scheduled batch job reads tension log, proposes graph edits via confidence-weighted pipeline, writes provisional ADR-status decisions
- Stability constraint: between review cycles the graph is read-only at the structural level — learners never encounter mid-session structural changes

---

## Phase 7 — Sonnet Teaching Layer (First Prototype) **[PRODUCT]**

**Output:** a callable teaching endpoint that produces learner-facing prose against the rendering policy from `AGENT_INSTRUCTIONS.md`.

- Sonnet system prompt = `AGENT_INSTRUCTIONS.md` verbatim
- Input: current concept node + prerequisite nodes (one-hop) + two-hop neighborhood for entity resolution
- Output: teaching turn in product voice, no scaffolding tokens
- DeepTutor fork (Apache 2.0) as infrastructure base per `docs/infrastructure.md`; pedagogical layer is the new Sonnet integration

### 7.1 Paperclip commit

If the Phase 5 trial proved Paperclip's fit, this is the moment to commit: Paperclip orchestrates teaching evaluation runs, enforces budget on API spend, dispatches comparative-evaluation tickets in Phase 8.

### Phase 7 success criteria

- Sonnet teaching prototype, given the `AGENT_INSTRUCTIONS.md` worked-example input, produces the pass-case voice
- Spot-check: 10 random concept queries, manually graded for forbidden-token leakage. **Zero leakage is the bar.**
- **OQ-CONTEXT-COMPRESSION** (per `docs/tensions.md`) settled with an ADR before the prototype runs sustained multi-turn engagements; the chosen strategy keeps typical concept-engagement cost inside the cost-ceiling per [ADR 0029](product/adr/0029-personal-financial-cost-ceiling.md) projections at a target user count

---

## Phase 8 — Evaluation Harness **[ENGINE]**

**Output:** the builder verifies the rendering-policy worked example holds against stock Sonnet without the policy, isolating the contribution of the prompt-layer contract. A small private TestFlight cohort cold-tests the success criterion "an app I would pay for if it weren't mine," including the in-app BYOK onboarding flow. App Store submission readiness lands here, not Phase 9, because the Apple Developer Program lead time forces it.

The cold-test cohort is 2–3 people who haven't seen the project, given the TestFlight build with no instructions. It is not market validation — it is the verification artifact for the personal-project disposition's success criterion, defending against the builder-bias failure mode (knowing how the system works obscures whether it's usable cold). The cohort is *small* and *private* by design — a Phase 9 verification, not an ongoing program. Under [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) the cold-test also exercises the BYOK onboarding flow — a freshman-defaults-calibrated user must succeed at obtaining and entering an Anthropic API key without external help.

**Apple Developer Program enrollment starts here** (2–4 week lead time per [`docs/business.md`](product/docs/business.md) Pricing and Distribution). Don't defer to Phase 9 — the lead time risks blocking the UI prototype.

### Phase 8 success criteria

- Stock-Sonnet-without-rendering-policy head-to-head baseline runs against the AGENT_INSTRUCTIONS.md worked example; the rendering policy's contribution is isolated and recorded.
- Apple Developer Program enrollment in flight or complete.
- **Privacy policy and Apple App Store privacy questionnaire answers exist and align with the privacy ADR collection before App Store submission.** Pins the privacy-policy authoring window against the Apple lead time so that submission is not blocked on policy work. Consumer App Store posture, not institutional — no DPA, no FERPA framing. The API credential answer is "data not collected" per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 8.
- **User-facing BYOK onboarding flow exists** per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 4. The user can configure their Anthropic API key in the onboarding surface; the key is stored in iOS Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`; a `/v1/messages` round-trip test validates the key client-side before onboarding completes. Freshman-defaults calibration per [ADR 0012](product/adr/0012-freshman-defaults-autodidact-ceiling.md) applies to the onboarding copy.
- **Force-crash pre-submission test confirms zero key material appears in the captured crash report** (per Apple App Store guideline 5.1.1; Sentry/Crashlytics integration must scrub Authorization headers from any captured outgoing request).
- **Milestone-bound repo-migration trigger.** The `StarshipSuperjam/paideia` GitHub repo migrates to an organizational GitHub account before first App Store submission per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 7. Phase 8 cannot close without the migration if App Store submission is on the imminent path; the migration is the Phase-9-entry gate the App Store identity rests on.
- **Small private TestFlight cohort cold-test** runs against the build the App Store would receive: 2–3 people who haven't seen the project, given the TestFlight build with no instructions; cold-test debrief recorded as the verification artifact for the "an app I would pay for if it weren't mine" success criterion. The cold-test exercises the BYOK onboarding flow alongside the teaching surface.

See also: [ADR 0026](product/adr/0026-persistent-learner-storage-structural-not-substantive.md), [ADR 0027](product/adr/0027-rendering-policy-prompt-layer-contract.md), [ADR 0031](product/adr/0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md).

---

## Phase 9 — UI Prototype **[PRODUCT]**

**Output:** the Discovery / Planning / Engagement triad surfaces, implemented as a **single SwiftUI codebase shipping to iPhone + iPad first-class plus Mac via Designed-for-iPad**, distributed through the Apple App Store. No Android, no web client, no native AppKit/Catalyst Mac app. The DeepTutor fork (per [`docs/infrastructure.md`](product/docs/infrastructure.md)) is consulted only for what serves the Apple-native target.

Per [`docs/ui-architecture.md`](product/docs/ui-architecture.md). Application code; **the per-session changelog + ADR discipline does not apply** to application code (state-of-record-only). Normal git history.

### Phase 9 success criteria

- **Discovery / Planning / Engagement triad surfaces implemented** per [`docs/ui-architecture.md`](product/docs/ui-architecture.md) and [`docs/session-lifecycle.md`](product/docs/session-lifecycle.md). Discovery surface carries a dual-path affordance: AI conversational onboarding bounded by the purpose-not-topic discipline, plus a browseable concept catalog whose organization may consume the flat-domain-tags + community-detection algorithm — both first-class. Planning surface carries syllabus-as-plan with prerequisite gating, current/active syllabus view (hard-cap-of-five preserved; the planning surface signals the cap directly when exceeded), quiet completion markers, mastered concepts visible in syllabus context (no separate trophy / library surface — foreclosed), cross-syllabus convergence noting at routing-after-concept-completion. Engagement surface inherits structurally three bounded contexts: concept engagement, diagnostic, BYOB close reading.
- **Platform target: iPhone + iPad first-class via a single SwiftUI codebase; Mac via Designed-for-iPad opt-in.** Size-class adaptive layout handles the form factor differences. Mac polish target is *modest*: Mac-idiom keyboard shortcuts (Cmd+arrow, Cmd+W, Cmd+, etc.), menu bar items where the surface naturally calls for them, window-resize handling consistent with macOS, and a polish pass on focus-ring / pointer-hover behaviors that the iPad codebase gets for free under iPadOS pointer support. *Not* a native AppKit/Catalyst Mac app; *not* full macOS idiom (multi-window state restoration, document-based architecture, custom menu bar beyond the iPad-app default are out of scope).
- **Bridge surfacing in context** is the cross-domain rendering convention across all three surfaces — cross-domain edges surface contextually during planning ("studying this concept advances your path toward [other target] as well") and during engagement (callback references that bridge between domains). No standalone cross-domain visualization surface; no globe; no game-world rendering; no mastery-glow / tendril / colored-trail visualization.
- **Exit affordance is a first-class UI primitive** — single visible control reachable in one action from any concept-engagement / diagnostic / close-reading surface that returns the user to the Planning surface (or to Discovery on exit from a diagnostic).
- **Delete-account affordance is a first-class UI primitive** — wired to the `ON DELETE CASCADE` discipline; satisfies Apple App Store guideline 5.1.1 (in-app account deletion) for the iPhone, iPad, and Mac-via-Designed-for-iPad builds. User confirmation step communicates that deletion is reliable and irreversible.
- **Data-export affordance is a first-class UI primitive** — preserves cancellation-discipline honesty: the project may be paused or cancelled at any point; user data exportability makes cancellation honest, not destructive. Sibling to delete-account; both surfaces required for Phase 9 close on every Apple target.
- **BYOK onboarding flow is a first-class UI primitive** per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md) commitment 4 — Anthropic account-creation walkthrough, key-entry surface, Keychain storage with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`, `/v1/messages` round-trip validation before onboarding completes. Freshman-defaults calibration per [ADR 0012](product/adr/0012-freshman-defaults-autodidact-ceiling.md) applies to the onboarding copy. Sibling to delete-account and data-export; all three surfaces required for Phase 9 close on every Apple target.
- **Pedagogical-degradation discipline operates against the production user-facing surface** per [ADR 0014](product/adr/0014-sonnet-teaches-opus-reviews.md) (as extended at S-0129 to absorb the principle from the retired cost-ceiling mechanism). Engagement integrity is preserved under context-amplification pressure by retrieval-window downshifts (two-hop neighborhood → one-hop) that respect the atomic-unit-of-teaching commitment.
- **No "general chat" surface exposed.** Free-form input only inside the three bounded contexts (concept engagement, diagnostic, close reading) and within the Discovery surface's bounded AI conversational onboarding affordance (which inherits the purpose-not-topic discipline).
- **Static polish only** — visual design, typography, animation, copy quality, layout, iconography, sound design, haptics. The Mac-via-Designed-for-iPad polish pass (keyboard shortcuts, menu bar items, window-resize handling, focus-ring / pointer-hover) is consistent with the static-polish discipline. **Dynamic-feature surfaces foreclosed** — no social, no sharing, no leaderboards, no streaks, no push notifications beyond auth/billing, no community, no in-app messaging, no "what's new" surfaces. The funnel-mechanic discipline binds against *user*-funnel-mechanic (retention nudges that bait users into more API spend on their own dime) alongside the *builder*-funnel-mechanic concerns the prior framing identified per [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md). Adding any dynamic-feature surface requires superseding [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md).
- **No primary surface outside the Discovery / Planning / Engagement triad.** Secondary surfaces (settings, account management, billing, delete-account, data-export, BYOK onboarding, parked-syllabus list, user library of uploaded texts) are accessed from menus within or alongside the primary surfaces. Two open-for-amendment-without-supersession items: a library/bookshelf surface (if cold-test surfaces a concrete need consistent with the no-trophy-spectacle discipline) and discovery dual-path narrowing (if cold-test evidence makes the case).
- No `cohort_id`-driven UI affordances; no institutional onboarding flow; no LMS integration.

See also: [ADR 0007](product/adr/0007-cross-domain-porosity.md), [ADR 0011](product/adr/0011-no-hosted-copyrighted-material.md), [ADR 0018](product/adr/0018-flat-domain-tags-community-detection.md), [ADR 0028](product/adr/0028-input-side-scope-structural-not-prompt.md), [ADR 0031](product/adr/0031-erasure-mechanism-and-individual-only-regime.md), [ADR 0033](product/adr/0033-mission-realignment-structured-guidance-for-self-learners.md), [ADR 0034](product/adr/0034-discovery-planning-engagement-triad.md), [ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md).

---

## Recurring — Project health checks (per ADR 0022)

**Not phase-anchored.** Every 10 sessions (configurable cadence; was every 30 from S-0001 to S-0032, tightened to 10 at S-0033 by user direction per ADR 0022 Consequences amendment), the project's own machinery is audited for fit / gaps / dead weight / bloat. The cadence trigger fires automatically at session boot when `next_id mod health_check_cadence == 0` — the slot about to be claimed is the cadence-numbered session, per [ADR 0043](engine/adr/0043-hook-architecture.md) which corrected the original `last_claimed` off-by-one at S-0031. User accepts (the session's work is the audit, per [`engine/operations/health-check.md`](engine/operations/health-check.md)) or defers.

**First check expected around S-0030.** `engine/tools/health_check.py` produces the audit report; trend telemetry reads the committed `engine/session/archive/*.json` per [ADR 0042](engine/adr/0042-soft-warn-lifecycle-archive-canon.md).

Telemetry hooks built in S-0001:
- `tools/validate-history.jsonl` (append-only, soft-warn category trends)
- `session/archive/S-NNNN.json` per session (started_at, closed_at, status, working_on, outcome_summary)
- ADR status field (counts of Accepted / Deprecated / Superseded over time)
- `engine/changelog/<YYYY>/S-NNNN-*.md` entries (per-session categorized engine changes per ADR 0092)
- engine_memory `exploration` and `decisions` rooms (per ADR 0091 — FTS5 + BM25 + recency rank over curated drawers + transcript auto-capture)

---

## Strong working commitments referenced throughout

The 12 working commitments and 10 architectural decisions that roadmap success criteria assume as load-bearing. Each is contracted in the named ADR; ADR Status fields carry any supersession chains.

1. Pedagogical edges, not historical ([ADR 0001](product/adr/0001-pedagogical-edges-not-historical.md))
2. Operating discipline must not corrupt pedagogy ([ADR 0065](product/adr/0065-oss-pivot-and-byok-disposition.md); chain preserved through superseded predecessors [ADR 0032](product/adr/0032-personal-project-disposition.md), [ADR 0035](product/adr/0035-multi-platform-apple-expansion.md), [ADR 0029](product/adr/0029-personal-financial-cost-ceiling.md))
3. Supplementary media as metadata, not structure ([ADR 0003](product/adr/0003-supplementary-media-as-metadata-not-structure.md))
4. Relational learner model ([ADR 0004](product/adr/0004-relational-learner-model.md))
5. Per-text interpretive outline ([ADR 0005](product/adr/0005-per-text-interpretive-outline.md))
6. Domain-agnostic architecture ([ADR 0006](product/adr/0006-domain-agnostic-architecture.md))
7. Cross-domain porosity ([ADR 0007](product/adr/0007-cross-domain-porosity.md))
8. Concept nodes, not thinkers ([ADR 0008](product/adr/0008-concept-nodes-not-thinkers.md))
9. Portable mastery ([ADR 0009](product/adr/0009-portable-mastery.md))
10. Continuous contextual assessment ([ADR 0010](product/adr/0010-continuous-contextual-assessment.md))
11. No hosted copyrighted material ([ADR 0011](product/adr/0011-no-hosted-copyrighted-material.md))
12. Freshman defaults, autodidact ceiling ([ADR 0012](product/adr/0012-freshman-defaults-autodidact-ceiling.md))

Architectural decisions:

- Mastery verification as organic escalation ([ADR 0013](product/adr/0013-mastery-verification-organic-escalation.md))
- Sonnet teaches, Opus reviews ([ADR 0014](product/adr/0014-sonnet-teaches-opus-reviews.md))
- Event-sourced learner model ([ADR 0015](product/adr/0015-event-sourced-learner-model.md))
- Graph construction needs live validation ([ADR 0016](engine/adr/0016-graph-construction-needs-live-validation.md))
- Postgres + recursive CTEs over OWL/RDF ([ADR 0017](product/adr/0017-postgres-recursive-ctes-over-owl-rdf.md))
- Flat domain tags + community detection ([ADR 0018](product/adr/0018-flat-domain-tags-community-detection.md))
- Two-column rigor score override model ([ADR 0019](product/adr/0019-two-column-rigor-score-override.md))
- Teaching notes separate from summary ([ADR 0020](product/adr/0020-teaching-notes-separate-from-summary.md))
- Node deprecation via status + superseded_by ([ADR 0021](product/adr/0021-node-deprecation-status-superseded-by.md))
- Periodic project health checks ([ADR 0022](engine/adr/0022-periodic-project-health-checks.md))
