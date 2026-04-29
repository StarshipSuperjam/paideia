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

### 1.2 Author rendering policy

- **`AGENT_INSTRUCTIONS.md`** — standalone rendering-policy file extracted from `docs/pedagogy.md`. Forbidden tokens (mastery-state names, prerequisite-edge framing, evidence-event references, scaffolding-proximity language, weight/confidence/provenance exposure, graph_version references, tension-log mechanism). Surviving tokens (concept names, domain-area names). Citation rules. Uncertainty posture. Worked example.

### 1.3 Add `confidence_level` to node schema

Add `confidence_level` (`EXTRACTED | INTERPRETED | SYNTHETIC`) to the node schema in `docs/architecture.md`, orthogonal to existing `provenance` and numeric `confidence`. Synthetic nodes are first candidates for self-correction review.

### Phase 1 success criteria

- Sessions 9, 10, 11 closed; sessions 12-14 explicitly tagged deferred in `docs/tensions.md`
- `AGENT_INSTRUCTIONS.md` exists and a worked example passes when fed to Sonnet against a stub graph
- `confidence_level` column added to the node schema (architecture.md)
- All Phase 1 ADRs land in `adr/` with Status: Accepted

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

---

## Phase 8 — Evaluation Harness

**Output:** ordinal external-baseline evaluation. Not closed-loop self-validation.

Validation against your own authored criteria is weak signal (per ADR — closed-loop is misleading). External baseline produces ordinal signal robust to designer drift. Paideia's evaluation: teaching quality measured by:

- (a) external rubric (community college instructor blind review), or
- (b) head-to-head against a baseline (DeepTutor unmodified, or stock Sonnet without the rendering policy), or
- (c) some combination

**OQ-PHASE8-A** (open tension in `docs/tensions.md`): which baseline mix? Decided at Phase 8 entry.

**Apple Developer Program enrollment starts here** (2-4 week lead time per `docs/business.md`). Don't defer to Phase 9 — the lead time risks blocking the UI prototype.

### Phase 8 success criteria

- Evaluation harness operational against the chosen external-baseline mix (per OQ-PHASE8-A resolution at Phase 8 entry)
- Apple Developer Program enrollment in flight or complete
- **Privacy policy and Apple App Store privacy questionnaire answers exist and align with the privacy ADR collection** (ADR 0026 and any superseding/extending ADRs that emerge from OQ-PRIVACY-A and OQ-PRIVACY-B) **before App Store submission.** This pins the privacy-policy authoring window against the Apple lead time so that submission is not blocked on policy work.

---

## Phase 9 — UI Prototype

**Output:** globe + syllabus surface, native iOS/Android primary, web test surface.

Per `docs/ui-architecture.md`. Application code; **CHANGELOG / ADR discipline does not apply** to application code (per the scoping decision; state-of-record-only). Normal git history.

Subscribe to Google Play Console if not already done in Phase 8.

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
2. Commercial sustainability without pedagogical compromise (ADR 0002)
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
