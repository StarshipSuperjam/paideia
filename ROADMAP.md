# Paideia Roadmap

> **A roadmap, not a contract.** Phase plans are tools — re-order if evidence warrants. When a phase plan changes, the prior version is marked superseded (per the ADR status conventions in `docs/operations/adr-authoring.md`), not deleted.

This document names every phase, its scope, its success criteria, and the architectural decisions it carries. Future sessions read this to know what's next without re-deriving the plan from history.

`STATE.md` names the *current* phase and the *next session's work item*. This file names the *whole arc*.

---

## Phase 0 — Foundation (in progress)

**Setup, not build.** The session-protocol layer, industry-standard repo skeleton, decision-record discipline, and project memory get established. After Phase 0, every future session boots cold from `STATE.md` + MemPalace + the conventions in `CLAUDE.md` and `docs/operations/`.

**Three foundation sessions:**

- **S-0001** — structural foundation + retirement of obsolete pre-foundation source files. Top-level industry-standard files (this file, README.md, LICENSE, CHANGELOG.md, SECURITY.md, STATE.md, HANDOFF.md), session/ + tools/ + pre-commit hook + slash command, supabase/migrations/ placeholders, repo reorganization into `docs/`.
- **S-0002** — procedural layer + MemPalace indexing + CONTEXT.md split. CLAUDE.md + 11-file `docs/operations/` library + `docs/MISSION.md` + `docs/CROSS_REFERENCES.md` + MemPalace wing/rooms/drawers indexed against the relocated docs.
- **S-0003** — ADR collection (22 ADRs absorbing the 12 working commitments + the 8 entries from the transitional `design-reasoning.md` + 2 architectural decisions that emerged in the S-0001 plan conversation, ADRs 0016 and 0022). `adr/README.md` indexes the collection; full Nygard guidance and status conventions live in `docs/operations/adr-authoring.md`. `design-reasoning.md` retired at S-0003 close.

**Phase 0 closes when:** a fresh Claude Code session can type `Start Engine` (or `/start-engine`), boot cold from `STATE.md` + MemPalace, claim the next slot via the eager-claim ritual, do its work, and close cleanly with audit + commit + push — without human briefing.

---

## Phase 1 — Contract Lock

**Output:** every remaining design ambiguity that would propagate into the seed graph is settled, audit-checked, and durable.

### 1.1 Close pending prompt-pack sessions (9, 10, 11)

The 14-session prompt pack is at `docs/prep-paideia-prompt-pack.md`. Sessions 1-8 closed pre-Foundation. Sessions 9-14 remaining; ordered by blocking priority:

- **Session 9 — Engagement Depth Aggregation.** Blocks prototype work (composite engagement signal feeds mastery computation). Run as the first SA-tracked work session after Foundation closes.
- **Session 10 — Decay Parameter Verification.** Depends on Session 9.
- **Session 11 — Historical Maximum Tracking.** Small schema decision, independent of 9 and 10.
- **Session 12 — Fork Maintenance Timeline.** Deferred until after Phase 7 (DeepTutor fork is a Phase 7 prototype dependency; maintenance posture is a downstream concern).
- **Session 13 — Gamification & Milestone Tone.** Mostly resolved as a sensibility (per `docs/business.md` and `docs/pedagogy.md`). Re-open if a concrete gamification feature is proposed.
- **Session 14 — Media Edge Quality.** Deferred until Phase 5 surfaces concrete cross-domain cases that test the supplementary-media-as-metadata commitment.

### 1.2 Author rendering policy and sibling commitments
**Revised: 2026-04-29 (S-0008 — scope expanded by exploration-session commitments per the no-silent-drops feedback rule.)**

- **`AGENT_INSTRUCTIONS.md`** — standalone rendering-policy file extracted from `docs/pedagogy.md`. Forbidden tokens (mastery-state names, prerequisite-edge framing, evidence-event references, scaffolding-distance language, weight/confidence/provenance exposure, graph_version references, tension-log mechanism, mastery-verification mechanic, machinery self-reference). Surviving tokens (concept names, domain-area names, thinker names, text titles, cross-domain connections). Citation rules (named structural units, no fabricated quotations). Uncertainty posture. Scope discipline (purpose-not-topic discrimination). Tension emission policy operationalizing [ADR 0026](adr/0026-persistent-learner-storage-structural-not-substantive.md)'s `pattern_observed` writing constraint. Worked example (gradeable test artifact for Phase 7 success criterion).
- **[ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md)** — rendering policy as the prompt-layer contract. The output-side half of the bidirectional teaching-surface contract.
- **[ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md)** — input-side scope is structural, not prompt-policed. The input-side half of the bidirectional contract. Three bounded input contexts (concept engagement, diagnostic, close reading); purpose-not-topic discrimination within bounded contexts; exit affordance as the structural alternative to general chat.
- **[ADR 0029](adr/0029-personal-financial-cost-ceiling.md)** — personal financial cost ceiling as operating constraint. Cost protection is a precondition (not a feature) for opening the system to non-builder users; mechanism mandated, ceiling value held in private operational configuration; soft walls degrade rather than terminate (preserving concept-engagement integrity).
- **Tension entries** opened for sub-decisions deferred to downstream phases: OQ-BYOK-REGIME (institutional vs. consumer; decide-before consumer launch), OQ-WALL-BEHAVIOR (soft-wall degradation ladder; decide-before Phase 8), OQ-CONTEXT-COMPRESSION (token-amplification mitigation; decide-before Phase 7), OQ-PEDAGOGY-INFERENCE-LOCUS (rule layer vs. distributed inference; revisit trigger pinned to inference-registry size and operational complaint surfacing).
- **[`docs/pedagogy/inferences.md`](docs/pedagogy/inferences.md)** — pedagogical inference registry stub. Cheap intermediate step before deciding whether to build a dedicated rule layer per OQ-PEDAGOGY-INFERENCE-LOCUS.

### 1.3 Add `confidence_level` to node schema

Add `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`) to the node schema in `docs/architecture.md`, orthogonal to existing `provenance` and numeric `confidence`. Synthetic nodes are first candidates for self-correction review.

### Phase 1 success criteria

- Sessions 9, 10, 11 closed; sessions 12-14 explicitly tagged deferred in `docs/tensions.md`
- `AGENT_INSTRUCTIONS.md` exists and a worked example passes when fed to Sonnet against a stub graph
- ADRs 0027 (rendering policy), 0028 (input-side scope structural-not-prompt), and 0029 (personal financial cost ceiling) land with Status: Accepted
- `confidence_level` column added to the node schema (architecture.md)
- All Phase 1 ADRs land in `adr/` with Status: Accepted

---

## Phase 1.5 — Mission Realignment Overhaul
**Added: 2026-04-30 (S-0013 — opens Phase 1.5; sits between the closed Phase 1 and the queued Phase 2 because Phase 2 will scaffold per-session contracts for every downstream phase, and those scaffolds would lock in the wrong UI architecture and platform scope if Phase 2 ran before the realignment lands.)**

**Output:** the contract layer is realigned around the project's core value claim — *filling the gap where a self-learner has no teacher* — by dropping the globe / mastery-glow / cross-domain-tendrils / trophy / "knowledge as a world" UI metaphor that was drifting attention away from the discovery / planning / mastery-gating value, and committing the replacement product structure (Discovery → Planning → Engagement triad) plus the broadened Apple platform scope (iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad). This is **realignment, not rebuild** — the pedagogical dependency graph, the AI instructor model, the bring-your-own-book close reading, the mastery model, the privacy posture, and the cost ceiling all survive intact.

**The realignment is recorded as a phase, not as scattered amendments**, because (a) it touches the contract layer (ADRs + foundational docs), (b) the session protocol's two-layer decision-recording discipline requires the load-bearing artifacts to land coherently, (c) the work spans more session-budget than fits a single session, and (d) Phase 2 (Build Plan Scaffolding) is downstream and consumes the realigned contract.

### 1.5.1 Mission realignment + globe/reward closure (S-0013)

- **[ADR 0033](adr/0033-mission-realignment-structured-guidance-for-self-learners.md)** — Mission realignment: structured guidance for self-learners. Records the corruption vector (the globe and reward systems were UI-layer optimizations that drifted attention away from the discovery / planning / mastery-gating value claim) and formally closes obsolescence of globe-as-home, mastery-glow, cross-domain-tendrils, trophy framing, and "knowledge as a world" metaphor. Names the survivors explicitly (graph + instructor; BYOB; bounded engagement contexts; mastery model). Cites continuity with [ADR 0032](adr/0032-personal-project-disposition.md) (this is operating discipline that protects the mission, not a reversal).
- **Light revision of [ADR 0018](adr/0018-flat-domain-tags-community-detection.md)** — remove the globe-rendering use case from the Decision and Consequences. The flat-domain-tags + community-detection algorithm survives as a graph-analysis primitive (potential uses: discovery-surface concept clustering, syllabus organization heuristics, graph-quality audits) but no longer serves a globe-rendering surface. Status remains Accepted.
- **Light revision of [`docs/MISSION.md`](docs/MISSION.md) What this is** — reframe around the structured-guidance gap as the core value claim. Cross-domain porosity preserved. Drop any "exploring the territory of knowledge" framing if present.

### 1.5.2 Discovery / Planning / Engagement triad architecture (S-0014)

- **ADR 0034** — Discovery / Planning / Engagement triad as primary product structure. Cross-references [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md) (engagement-side bounded contexts preserved). Names the discovery-side affordances: AI conversational onboarding parallel with browseable concept catalog organized by domain/topic. Names the planning-side affordances: syllabus-as-plan, prerequisite gating, quiet completion markers, current/active syllabus view. Names the explicit foreclosures: no separate trophy surface, no globe, no game-world rendering, no library/bookshelf as a third primary surface (mastered concepts surface contextually within syllabi).
- **Substantial rewrite of [`docs/ui-architecture.md`](docs/ui-architecture.md)** — drop Globe Navigation Model and Level-of-Detail Rendering sections wholesale. Author Discovery Surface, Planning Surface, Engagement Surface sections. Cross-domain edges remain first-class graph data; their UI rendering is **bridge surfacing in context** during engagement and planning, not "tendrils on a globe."
- **Substantial rewrite of [`docs/session-lifecycle.md`](docs/session-lifecycle.md)** — drop Globe as Home Screen and the trophy/glow/tendrils framing in Mastery Verification. Preserve: Concept Engagement as Atomic Unit, Mode Transitions, Proficiency as Implied Transition, Routing After Concept Completion, Mastery Verification Through Downstream Teaching's organic-escalation framing per [ADR 0013](adr/0013-mastery-verification-organic-escalation.md). Concurrent Syllabus Limit (hard cap of five) remains.

### 1.5.3 Multi-platform Apple expansion + Phase 9 rewrite (S-0015)

- **ADR 0035** — Multi-platform Apple expansion. Supersedes [ADR 0032](adr/0032-personal-project-disposition.md) in full. Commitment 1 (revised) reads: *Apple platforms via App Store. iPhone + iPad first-class via a single SwiftUI codebase. Mac via Designed-for-iPad opt-in with modest keyboard/menu polish. No Android, no web app, no native AppKit/Catalyst Mac app.* Restates commitments 2–6 (cost-priced subscription, no free tier, builder eats API costs, no BYOK / no institutional regime, ADR 0029 reframed as fixed annual subsidy, polish-static / maintenance-minimum) verbatim from ADR 0032 — preserves the disposition spirit while broadening the platform scope.
- **Rewrite of [ROADMAP.md](ROADMAP.md) Phase 9 success criteria** — replace globe-as-home-screen + concept-engagement-surface with the Discovery / Planning / Engagement triad. Restate platform target as iPhone + iPad first-class via SwiftUI, Mac via Designed-for-iPad. Preserve: cost-cap mechanism, no general chat surface, exit affordance, delete-account, data-export.
- **Amendment to [`docs/business.md`](docs/business.md) Pricing and Distribution** — Distribution row becomes "Apple App Store. iPhone + iPad first-class; Mac via Designed-for-iPad." Other rows unchanged.

### 1.5.4 Rendering policy revision + secondary docs sweep (S-0016)

- **Revision to [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md)** — extend the forbidden-token enumeration to forbid globe / world / map / territory / exploration metaphors and reward / trophy / glow / mastery-visualization language in agent output. Status remains Accepted.
- **Revision to [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md)** — add the new forbidden tokens; update the worked example if it references dropped concepts.
- **Light revisions to [ADR 0012](adr/0012-freshman-defaults-autodidact-ceiling.md)** (strip residual market framing not removed by ADR 0032's MISSION.md rewrite; name the freshman-defaults builder-bias-protection role explicitly) and **[ADR 0014](adr/0014-sonnet-teaches-opus-reviews.md)** (strip residual cohort framing if present).
- **Sweep across secondary docs** — drop residual globe / mastery-glow / tendril / trophy / colored-trail / "knowledge as a world" references in `docs/pedagogy.md`, `docs/tensions.md`, `docs/architecture.md`, `docs/learner-model.md`, `docs/CROSS_REFERENCES.md`, `README.md`, `docs/prep-paideia-prompt-pack.md`, `docs/pedagogy/inferences.md`, `docs/infrastructure.md`. Tension entries for globe/trophy resolved with `Resolved: 2026-04-30` markers per the project's tension-resolution discipline (not deleted).

### Phase 1.5 success criteria

- ADRs 0033, 0034, 0035 land at Status: Accepted; ADR 0032 Status flipped to `Superseded by ADR 0035`
- Light revisions to ADRs 0012, 0014, 0018, 0027 land with Status remaining Accepted
- `docs/ui-architecture.md` and `docs/session-lifecycle.md` rewritten end-to-end with no remaining globe/glow/tendril references; `docs/MISSION.md` What this is reframed
- `git grep -i "globe\|mastery glow\|tendril\|trophy\|colored trail\|knowledge as a world\|Globe Navigation Model"` returns zero matches in tracked docs and ADRs except ADR 0033 (names what's being dropped, by design), ADR 0027 (forbidden-token list, by design), ADR 0018 (revised text explaining algorithm-survives-without-globe, by design), ADR 0032 file (history, by design — superseded), and `CHANGELOG.md` (history, by design)
- ROADMAP Phase 9 success criteria rewritten against triad + multi-platform; Android/web references gone
- ADR collection grows from 32 → 35 (3 new + 4 light-revised + 1 superseded); MemPalace `decision` drawers filed for ADRs 0033, 0034, 0035
- Phase 2 (Build Plan Scaffolding) opens at S-0017 with the realigned contract as input

### Phase 1.5 plan reference

The full session-by-session plan — including critical files per session, source documents, and per-session success criteria — was approved at S-0013 boot and lives at `/Users/shanekidd/.claude/plans/at-its-core-this-iterative-beaver.md`. STATE.md's `## Next session work item` block carries each session's scope inline as it becomes the active session, per the project's session protocol.

---

## Phase 2 — Build Plan Scaffolding

**Output:** a `build_plan/` directory naming the chunked authoring sessions for Phases 3-9, and the working contract for each session.

- `build_plan/MANIFEST.md` — orientation, session schedule, phase mapping
- `build_plan/00_preamble.md` — orienting prose
- `build_plan/00_session_schedule.md` — every session by ID with scope, source documents, output target, budget tier
- `build_plan/P_0_contract_lock.md` — retroactive Phase 1 record
- `build_plan/P_1_sql_schema.md` through `build_plan/P_13_ui_prototype.md` — per-phase chunks

This file (`ROADMAP.md`) names the phases at a high level. `build_plan/` names the per-session work within each phase.

---

## Phase 3 — SQL Schema Implementation

**Output:** Postgres schema deployed to Supabase via versioned migrations.

Translate `docs/architecture.md` and `docs/learner-model.md` schemas into:

- `nodes` table — id, label, domain[], summary, teaching_notes, aliases[], rigor_score_computed, rigor_score_adjustment, **confidence_level** (per Phase 1.3), confidence (numeric), provenance, status, superseded_by, graph_version_added, timestamps
- `edges` table — source_id, target_id, type, weight, confidence, provenance, evidence, graph_version_added
- `learner_events` table — event-sourced log per `docs/learner-model.md`
- `mastery_snapshots` table — cached mastery state
- `tension_log` table — per `docs/self-correction.md`
- `settings` — graph_version counter

Stack: Supabase migrations at `supabase/migrations/0001_*.sql` and forward.

### Phase 3 success criteria

- `supabase db push` applies the migrations cleanly to dev DB
- `\d+ nodes` shows expected columns including `confidence_level`
- Migration rollback works
- `tension_log` and `learner_events` schemas conform to ADR 0026 (`exchange_summary` as JSONB-with-named-fields; `learner_events.context` as structured columns; no free-text grab-bags); the OQ-PRIVACY-A erasure mechanism and OQ-PRIVACY-B institutional-regime column reservation are settled before migration authoring begins

---

## Phase 4 — Graph Validation Utility (per ADR 0016)

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

Canonical edge-type registry: `prerequisite`, `enables`, `informed_by`, `cross_domain_dependency`, etc. Adding a new predicate is a CHANGELOG-tracked material change requiring a new manifest entry in the same session.

### 4.4 Flesh out `docs/operations/seed-chunked-authoring.md`

Per-session migration workflow: read SEP article → identify concepts at granularity principle → write `00NN_seed_<subdomain>_partN.sql` migration → `supabase db push` → `tools/validate.py` → fix in-session → commit.

### Phase 4 success criteria

- `validate.py --validate-only` runs end-to-end against the live DB in <3s on a 100-node test seed
- New predicate not in PREDICATE_MANIFEST.md surfaces as a soft warn
- Deliberately-broken edge ref triggers hard-fail with exit 2
- Pre-commit hook blocks seed-authoring commits that fail audit

---

## Phase 4.5 — Input Dataset Survey (for Phase 5 seed authoring)
**Added: 2026-04-29 (S-0009)**

**Output:** a tiered survey of external datasets useful as **cross-reference inventories and prerequisite-shape priors** for Phase 5 seed authoring. Lands as a new section in [`docs/content-strategy.md`](docs/content-strategy.md) ("Cross-Domain Reference Inventories — Survey") with per-candidate assessment against the five usability axes.

This phase **does not** revise the "Generative Graph Independence" position (`business.md`) or the SEP-as-structural-reference posture (`content-strategy.md`). Concept nodes and prerequisite edges remain generatively seeded; the survey gives that generation pass better starting inventories per domain and surfaces any prerequisite-shaped graph priors worth consulting.

### Five usability axes (constrain every candidate)

1. **Graph-shape orientation.** Prerequisite-shaped (per ADR 0001) vs. influence / agreement / dialectical / citation / co-occurrence. Filter aggressively — influence-shaped data drags the modeler dialectical even when intended only as vocabulary.
2. **License.** *Simplified at S-0012 per [ADR 0032](adr/0032-personal-project-disposition.md):* "consultable for personal use" is the operative bucket. The prior tripartite distinction — ingestable (CC0/CC-BY/MIT/PD) vs. mineable-for-facts-only (citations, taxonomies) vs. consultable-only (all-rights-reserved, non-commercial like SEP) — collapses because nothing the project consumes is consumed *for commercial purposes*. The graph is generated parametrically (per [ADR 0011](adr/0011-no-hosted-copyrighted-material.md) and the surviving operational substance from `docs/content-strategy.md`); external sources serve as inventories and cross-reference checks consultable for personal use. Surveys note license terms for completeness but do not turn on the ingestable / mineable distinction.
3. **Form.** Structured graph data vs. structured taxonomy/tags vs. long-form prose. Long-form prose has low novel value — already parametrically accessible to Sonnet/Opus.
4. **Coverage breadth.** Single-domain vs. cross-domain native. Commitment 7 (cross-domain porosity per ADR 0007) makes cross-domain-native sources disproportionately valuable.
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
- **Author's own caveat** — "Browsing this visual summary cannot substitute reading a good book of history of philosophy" — is rhetorical prior art for [ADR 0011](adr/0011-no-hosted-copyrighted-material.md) and the BYO-book commitment.
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

## Phase 5 — Seed Graph Build (parallelizable)

**Output:** concept-level seed graph across philosophy subdomains. Hundreds of nodes per subdomain. Cross-domain edges first-class.

Per the chunked-authoring + eager-claim discipline, multiple subdomain sessions run concurrently without merge conflicts. This is the **first natural parallel-work moment** and the **Paperclip orchestration trial moment.**

### 5.1 Subdomain sessions

- **P_3 Epistemology** — start here; the deprecated v0.2 prototype was epistemology-focused so judgment is calibrated
- **P_4 Ethics**
- **P_5 Metaphysics**
- **P_6 Philosophy of Mind**
- **P_7 Philosophy of Language**
- **P_8 Philosophy of Science**
- **P_8.5 Service Nodes** — logic primitives, mathematical prerequisites, history nodes that terminate where they stop affecting comprehension
- **P_9 Cross-domain edges pass** — after subdomain interiors are stable, generate edges spanning subdomain boundaries

### 5.2 Source approach

- **SEP** as **structural reference only** (concept inventory, cross-references) — not a content corpus. SEP does not become hosted text.
- **Wikipedia** for accessible summaries (CC BY-SA — permits use with attribution).
- **Generate first-pass prerequisite edges via Claude;** mark `confidence_level: INTERPRETED` until validated against learner outcomes or expert review.
- **Phase 4.5 survey output** ([`docs/content-strategy.md`](docs/content-strategy.md) "Cross-Domain Reference Inventories — Survey") names the per-domain inventories and any prerequisite-shaped graph priors worth consulting at session start. Sessions consult it as a checklist; specific adoption decisions land as ADRs in-session if they involve non-trivial tradeoffs.

### 5.3 Per-session migration workflow

Per `docs/operations/seed-chunked-authoring.md`:

1. Session reads target subdomain's SEP article structure, identifies in-scope concepts at the granularity principle (one mastery state per concept)
2. Session writes new migration file `00NN_seed_<subdomain>_partN.sql` with INSERT statements, `graph_version_added` set to current settings counter, explicit `confidence_level`
3. Session runs `supabase db push`
4. Session runs `tools/validate.py --validate-only` against post-push DB
5. Hard-fails fix in-session; soft-warns recorded in session outcome_summary per category
6. Session closes, commits the migration file (CHANGELOG entry tracked)

### 5.4 Paperclip trial

When two or more subdomain sessions queue up to run in parallel (Epistemology + Ethics), trial Paperclip orchestration: tickets per subdomain, scheduled heartbeats, atomic dispatch. Decision to commit (Phase 7) hinges on this trial's results.

### Phase 5 success criteria

- Each subdomain session closes with zero hard-fails from `validate.py`
- Soft-warn counts recorded per category in session outcome_summary
- Migration files atomically attributable to the session that wrote them via the session's CHANGELOG entry
- Cross-session schema drift detected by the predicate-manifest audit

---

## Phase DEC.1 — Retrieval / Mastery-Inference Architecture Decisions

**Sits between Phase 5 and Phase 6.** After the seed graph is mature, retrieval-shape decisions become testable; before the teaching layer is built, they're load-bearing.

**Decisions to settle** (each tracked as an open tension in `docs/tensions.md` from S-0001 onward):

- **OQ-DEC1-A:** Server-side mastery computation — confirm or revisit?
- **OQ-DEC1-B:** Two-hop neighborhood retrieval shape for teaching session context
- **OQ-DEC1-C:** Embedding strategy for entity resolution — pgvector + which embedding model
- **OQ-DEC1-D:** Chunk-resolver index for SEP onward-reading vs direct SEP URL pointers

Each decision lands as an ADR with Status: Accepted and a Phase-6 implementation tag.

---

## Phase 6 — Self-Correction Pipeline

**Output:** tension log + Opus batch review pipeline operational.

Implements `docs/self-correction.md`:

- Tension log schema in Postgres (Phase 3)
- Sonnet teaching-side: emit tension records (`struggle_unresolved`, `unexpected_ease`, `spontaneous_connection`, `source_ineffective`, `mastery_contradiction`)
- Opus reviewer: scheduled batch job reads tension log, proposes graph edits via confidence-weighted pipeline, writes provisional ADR-status decisions
- Stability constraint: between review cycles the graph is read-only at the structural level — learners never encounter mid-session structural changes

---

## Phase 7 — Sonnet Teaching Layer (First Prototype)

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
- **OQ-CONTEXT-COMPRESSION** (per `docs/tensions.md`) settled with an ADR before the prototype runs sustained multi-turn engagements; the chosen strategy keeps typical concept-engagement cost inside the cost-ceiling per [ADR 0029](adr/0029-personal-financial-cost-ceiling.md) projections at a target user count

---

## Phase 8 — Evaluation Harness

**Substantially simplified: 2026-04-30 (S-0012 — per [ADR 0032](adr/0032-personal-project-disposition.md). External-rubric and DeepTutor-head-to-head candidates dropped; OQ-PHASE8-A's three-candidate framing reduces to one + the cold-test addition.)**

**Output:** the builder verifies the rendering-policy worked example holds against stock Sonnet (the surviving baseline), and a small private TestFlight cohort cold-tests the success criterion of [ADR 0032](adr/0032-personal-project-disposition.md) ("an app I would pay for if it weren't mine"). The cost-cap mechanism (per [ADR 0029](adr/0029-personal-financial-cost-ceiling.md), reframed at S-0012 as fixed annual operating subsidy budget) is wired and tested. App Store submission readiness lands here, not Phase 9, because the Apple Developer Program lead time forces it.

The prior three-candidate framing — (a) external rubric (community college instructor blind review), (b) head-to-head against DeepTutor unmodified, (c) head-to-head against stock Sonnet without the rendering policy — drops candidates (a) and (b) under [ADR 0032](adr/0032-personal-project-disposition.md): the external-rubric institutional channel is foreclosed (no community-college pilots), and the DeepTutor head-to-head's value was in producing publishable comparative evaluation (relevant only under the prior commercial / acquisition framing). Stock Sonnet without the rendering policy survives as the surviving baseline because it isolates the contribution of [ADR 0027](adr/0027-rendering-policy-prompt-layer-contract.md)'s prompt-layer contract — a signal the builder needs even under the personal-project disposition.

The added Phase 8 work is a **small private TestFlight cohort cold-test** (2–3 people who haven't seen the project, given the TestFlight build with no instructions). This is not market validation — it is the verification artifact for [ADR 0032](adr/0032-personal-project-disposition.md)'s success criterion ("an app I would pay for if it weren't mine"), defending against the builder-bias failure mode (knowing how the system works obscures whether it's usable cold). The cohort is *small* and *private* by design — a Phase 9 verification, not an ongoing program.

**Apple Developer Program enrollment starts here** (2–4 week lead time per [`docs/business.md`](docs/business.md) Pricing and Distribution). Don't defer to Phase 9 — the lead time risks blocking the UI prototype.

### Phase 8 success criteria

- Stock-Sonnet-without-rendering-policy head-to-head baseline runs against the [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) worked example; the rendering policy's contribution is isolated and recorded
- Apple Developer Program enrollment in flight or complete
- **Privacy policy and Apple App Store privacy questionnaire answers exist and align with the privacy ADR collection** ([ADR 0026](adr/0026-persistent-learner-storage-structural-not-substantive.md) + [ADR 0031](adr/0031-erasure-mechanism-and-individual-only-regime.md)) **before App Store submission.** Pins the privacy-policy authoring window against the Apple lead time so that submission is not blocked on policy work. Consumer App Store posture, not institutional — no DPA, no FERPA framing.
- **Cost-cap mechanism wired and tested before evaluation users are admitted** (per [ADR 0029](adr/0029-personal-financial-cost-ceiling.md), reframed at S-0012). Per-user spend ceiling, aggregate-system spend ceiling, real-time spend telemetry, and a defined behavior at the cap (per OQ-WALL-BEHAVIOR settled in an ADR before this phase opens — single-tier ladder under the cost-priced subscription model). Cost protection is a precondition for non-builder access, not a feature.
- **Small private TestFlight cohort cold-test** runs against the build the App Store would receive: 2–3 people who haven't seen the project, given the TestFlight build with no instructions; cold-test debrief recorded as the verification artifact for [ADR 0032](adr/0032-personal-project-disposition.md)'s success criterion.
- *Note: OQ-BYOK-REGIME no longer gates Phase 8 — closed by foreclosure under [ADR 0032](adr/0032-personal-project-disposition.md). The prior bullet is retracted.*

---

## Phase 9 — UI Prototype

**Narrowed at S-0012: 2026-04-30 (per [ADR 0032](adr/0032-personal-project-disposition.md) — iOS-only-native; Android / Google Play references removed; `cohort_id`-driven UI affordances removed; delete-account + data-export affordances added; static-polish discipline named explicitly; dynamic-feature foreclosure named explicitly.)**

**Output:** globe + syllabus surface, **native iOS only**. No Android, no web client. The DeepTutor fork (per [`docs/infrastructure.md`](docs/infrastructure.md)) is consulted only for what serves the iOS native target.

Per [`docs/ui-architecture.md`](docs/ui-architecture.md). Application code; **CHANGELOG / ADR discipline does not apply** to application code (per the scoping decision; state-of-record-only). Normal git history.

### Phase 9 success criteria
**Added: 2026-04-29 (S-0008); revised: 2026-04-30 (S-0012)**

- Globe-as-home-screen + concept-engagement surface implemented per [`docs/session-lifecycle.md`](docs/session-lifecycle.md) and [`docs/ui-architecture.md`](docs/ui-architecture.md), **iOS-only-native** (no Android, no web)
- **Exit affordance is a first-class UI primitive** per [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md) — single visible control reachable in one action from any concept engagement / diagnostic / close-reading surface that returns the user to graph navigation
- **Delete-account affordance is a first-class UI primitive** — wired to [ADR 0031](adr/0031-erasure-mechanism-and-individual-only-regime.md)'s `ON DELETE CASCADE` discipline; satisfies Apple App Store guideline 5.1.1 (in-app account deletion). User confirmation step communicates that deletion is reliable and irreversible.
- **Data-export affordance is a first-class UI primitive** — preserves cancellation-discipline honesty per [ADR 0032](adr/0032-personal-project-disposition.md) commitment 6 (the project may be paused or cancelled at any point; user data exportability makes cancellation honest, not destructive). Sibling to delete-account; both surfaces required for Phase 9 close.
- Cost-cap mechanism (per [ADR 0029](adr/0029-personal-financial-cost-ceiling.md), reframed at S-0012 as fixed annual operating subsidy budget) operates against the production user-facing surface, not just the evaluation harness from Phase 8
- No "general chat" surface exposed (per [ADR 0028](adr/0028-input-side-scope-structural-not-prompt.md)); free-form input only inside the three bounded contexts (concept engagement, diagnostic, close reading)
- **Static polish only** per [ADR 0032](adr/0032-personal-project-disposition.md) commitment 6 — visual design, typography, animation, copy quality, layout, iconography, sound design, haptics. **Dynamic-feature surfaces explicitly foreclosed** — no social, no sharing, no leaderboards, no streaks, no push notifications beyond auth/billing, no community, no in-app messaging, no "what's new" surfaces. Any proposal to add a dynamic-feature surface must supersede ADR 0032.
- *No `cohort_id`-driven UI affordances; no institutional onboarding flow; no LMS integration. The institutional schema provisions retired in S-0012 are not surfaced.*

---

## Recurring — Project health checks (per ADR 0022)

**Not phase-anchored.** Every ~30 sessions (configurable cadence), the project's own machinery is audited for fit / gaps / dead weight / bloat. The cadence trigger fires automatically at session boot when `last_claimed mod health_check_cadence == 0`. User accepts (the session's work is the audit, per `docs/operations/health-check.md`) or defers.

**First check expected around S-0030.** `tools/health_check.py` lands in one of the sessions ~S-0025.

Telemetry hooks built in S-0001:
- `tools/validate-history.jsonl` (append-only, soft-warn category trends)
- `session/archive/S-NNNN.json` per session (started_at, closed_at, status, working_on, outcome_summary)
- ADR status field (counts of Accepted / Deprecated / Superseded over time)
- CHANGELOG.md entries (categorized changes by date)
- MemPalace `exploration` and `decision` tags (semantic memory of every conversation)

---

## Strong working commitments referenced throughout

These are the 12 working commitments inherited from pre-Foundation design and absorbed into ADRs 0001-0012 in S-0003. Roadmap success criteria assume them as load-bearing.

1. Pedagogical edges, not historical (ADR 0001)
2. Operating discipline must not corrupt pedagogy ([ADR 0032](adr/0032-personal-project-disposition.md), supersedes [ADR 0002](adr/0002-commercial-sustainability-without-pedagogical-compromise.md); supporting operating discipline: [ADR 0029](adr/0029-personal-financial-cost-ceiling.md))
3. Supplementary media as metadata, not structure (ADR 0003)
4. Relational learner model (ADR 0004)
5. Per-text interpretive outline (ADR 0005)
6. Domain-agnostic architecture (ADR 0006)
7. Cross-domain porosity (ADR 0007)
8. Concept nodes, not thinkers (ADR 0008)
9. Portable mastery (ADR 0009)
10. Continuous contextual assessment (ADR 0010)
11. No hosted copyrighted material (ADR 0011)
12. Freshman defaults, autodidact ceiling (ADR 0012)

Plus architectural decisions (ADRs 0013–0022, recorded in S-0003 from the transitional `design-reasoning.md` and the S-0001 plan conversation):

- Mastery verification as organic escalation (ADR 0013)
- Sonnet teaches, Opus reviews (ADR 0014)
- Event-sourced learner model (ADR 0015)
- Graph construction needs live validation (ADR 0016)
- Postgres + recursive CTEs over OWL/RDF (ADR 0017)
- Flat domain tags + community detection (ADR 0018)
- Two-column rigor score override model (ADR 0019)
- Teaching notes separate from summary (ADR 0020)
- Node deprecation via status + superseded_by (ADR 0021)
- Periodic project health checks (ADR 0022)
