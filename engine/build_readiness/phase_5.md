# Phase 5 — Seed graph build-readiness report

> Authored by S-0045 (master plan session) per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) + [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md). The master plan session **is** the gate session for Phase 5; this report covers the full Phase 5 batch (16 explicit tasks) rather than a single build session because routine-mode dispatches against the executable contract atomically. Every routine-mode session that picks up a Phase 5 task reads this report at boot. If Tier 1 contains unresolved items, the routine session refuses the task and exits with HANDOFF.
>
> Chunk: [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md). Executable contract: [`engine/session/auto_target.json`](../session/auto_target.json). Source documents: [`product/docs/architecture.md`](../../product/docs/architecture.md) (graph schema), [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md) (Phase 4.5 input dataset survey), [`engine/build_readiness/phase_3_sql.md`](phase_3_sql.md) and [`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md) (forward-pointers inherited). Load-bearing ADRs: [0001](../../product/adr/0001-pedagogical-edges-not-historical.md) (pedagogical edges, not historical), [0007](../../product/adr/0007-cross-domain-porosity.md) (cross-domain porosity), [0008](../../product/adr/0008-concept-nodes-not-thinkers.md) (concept nodes, not thinkers), [0011](../../product/adr/0011-no-hosted-copyrighted-material.md) (no hosted prose), [0016](../adr/0016-graph-construction-needs-live-validation.md) (graph validation contract), [0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) (confidence_level), [0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) (structural-reference posture for philosophy reference works), [0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) (no descoping), [0051](../adr/0051-routine-mode-and-engine-loop.md) (routine-mode architecture), [0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) (9-subdomain decomposition).

## Pre-session decisions (Tier 1 resolutions)

Seven Tier 1 findings settled in S-0045 before any routine-mode session opens against [`engine/session/auto_target.json`](../session/auto_target.json). Each cites the source documents that ground the resolution.

### T1-A — Subdomain decomposition: 9 subjects + service nodes + cross-bridges + closeout

**Decision.** Phase 5 decomposes into 9 subject subdomains (epistemology, metaphysics, logic, ethics, political philosophy, aesthetics, philosophy of mind, philosophy of language, philosophy of science) plus 3 operational tasks (service nodes, cross-bridges, closeout). 16 explicit tasks total after pre-splitting (epistemology, ethics, metaphysics, philosophy of mind into core/specialized halves).

**Rationale.** Pre-session adjudication surfaced material disagreement between [`engine/STATE.md:33-40`](../STATE.md) (8 subjects: epistemology, ethics, metaphysics, **logic**, mind, science, **political**, **aesthetics**) and the canonical [`build_plan/P_4_seed_graph_build.md:15-22`](../../build_plan/P_4_seed_graph_build.md) (6 subjects: epistemology, ethics, metaphysics, mind, **language**, science + services + crossdomain). Both lists had material omissions: STATE.md missed philosophy of language (homeless for sense/reference, speech acts, semantic externalism); build_plan missed logic, political philosophy, aesthetics (each is a top-level browse category in SEP and Routledge). The 9-subject + services + cross-bridges + closeout shape is the union of defensible coverage with the explicit deferrals named in [ADR 0052 §"Out of scope"](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) (philosophy of religion, history-as-subdomain).

**Artifact.** [ADR 0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) — *Phase 5 philosophy-subdomain decomposition*. Canon-realignment edits to [`ROADMAP.md`](../../ROADMAP.md) Phase 5.1, [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md), [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md), and [`engine/STATE.md`](../STATE.md) land in S-0045 alongside this report.

### T1-B — Subdomain task pre-splitting: epistemology, ethics, metaphysics, philosophy of mind into core+specialized

**Decision.** Four subdomains are pre-split into two tasks each at master-plan time (P5-01a/b, P5-02a/b, P5-04a/b, P5-07a/b). Logic, philosophy of language, philosophy of science, political philosophy, aesthetics remain single tasks. Service nodes, cross-bridges, closeout are single tasks each.

**Rationale.** Per [`engine/session/auto_target.schema.md:149`](../session/auto_target.schema.md) ("Break work into session-sized tasks. If a task is too large, split it; don't rely on multiple routine sessions to incrementally complete one task."), tasks must fit one routine session. The four pre-split subdomains have sufficient SEP coverage and concept density that a single migration would exceed reasonable session scope. The other five subjects are smaller (logic and aesthetics especially) or have well-bounded scopes (philosophy of language is dominated by analytic-tradition core; philosophy of science is methodology-anchored). The split lines are drawn by topic-coherence:

- **Epistemology core** (P5-01a) — foundational concepts: knowledge, justification, belief, certainty, the analysis of knowledge tradition. **Epistemology specialized** (P5-01b) — applied/specialized: social epistemology, virtue epistemology, formal epistemology, epistemic skepticism varieties.
- **Metaphysics core** (P5-02a) — being, identity, causation, time. **Metaphysics specialized** (P5-02b) — modality, free will, properties, universals, mereology.
- **Ethics metaethics+normative** (P5-04a) — moral realism, expressivism, virtue/deontological/consequentialist normative theories. **Ethics applied** (P5-04b) — bioethics, environmental ethics, applied moral problems.
- **Philosophy of mind core** (P5-07a) — mental causation, intentionality, perception, personal identity, AI/computational mind. **Philosophy of mind consciousness/specialized** (P5-07b) — consciousness, qualia, hard problem, phenomenology adjacencies.

The b-half depends on the a-half; routine-mode dispatches them in order via `depends_on`.

**Citations.** Schema discipline: [`engine/session/auto_target.schema.md:149`](../session/auto_target.schema.md). No live context-pressure signal for routine sessions: `CLAUDE.md` "Posture vs machinery" section; this gap is filed as enhancement [Issue #4](https://github.com/StarshipSuperjam/paideia/issues/4) and is decoupled from S-0045 — task-sizing pre-execution is the discipline that engineers around the gap.

### T1-C — `max_sessions` ceiling: 18

**Decision.** [`engine/session/auto_target.json`](../session/auto_target.json) sets `max_sessions: 18`. Count = 16 explicit tasks + 2-session buffer for HANDOFF-driven retries (a routine session that hits a Tier-1-blocker writes HANDOFF and exits without completing; a follow-up session retries with the unblocker applied).

**Rationale.** No hedge for context-overrun, since tasks are pre-sized to fit one session each per T1-B. The 2-session buffer covers (a) recovery from a single HANDOFF event, plus (b) one additional retry margin if a routine session encounters a transient infrastructure issue (e.g., Supabase unavailable mid-session). At `max_sessions` exhaustion, routine-mode halts with HANDOFF and the user adjudicates whether to extend, re-author the contract, or close Phase 5 with the remaining tasks deferred.

**Citations.** Schema field: [`engine/session/auto_target.schema.md:14`](../session/auto_target.schema.md). Operational behavior at exhaustion: [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md). Task count: 16 explicit tasks per T1-B and the [ADR 0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) decomposition.

### T1-D — `depends_on` graph: epistemology core anchors; cross-bridges block on all subjects + services; closeout blocks on cross-bridges

**Decision.** The `depends_on` shape:

- **P5-01a Epistemology core** — no deps (anchor)
- **P5-01b Epistemology specialized** — depends on P5-01a
- **P5-02a/b Metaphysics, P5-03 Logic, P5-04a/b Ethics, P5-05 Political philosophy, P5-06 Aesthetics, P5-07a/b Philosophy of mind, P5-08 Philosophy of language, P5-09 Philosophy of science, P5-10 Service nodes** — each depends on **P5-01a only** (parallel-eligible after epistemology core lands as the calibration anchor)
- **P5-11 Cross-bridges** — depends on all 9 subject subdomain tasks (a-and-b parts where split) plus P5-10 Service nodes
- **P5-12 Closeout** — depends on P5-11 only

**Rationale.** Epistemology-first per [`build_plan/P_4_seed_graph_build.md:14`](../../build_plan/P_4_seed_graph_build.md) ("the deprecated v0.2 prototype was epistemology-focused so judgment is calibrated"). The b-halves of pre-split subdomains depend on their own a-halves (concept inventory builds incrementally; specialized concepts presuppose core concepts). Cross-bridges block on all subjects so cross-domain edges target real concepts; running cross-bridges incrementally (as pairs become ready) was rejected because (a) it would require interleaving migrations into specific subdomain ranges in unpredictable orderings, and (b) it would push the cross-domain edge-shape decisions (predicate registry, domain-tag intersection rules) into individual subdomain sessions that should focus on their own concept inventories. Cross-bridges as a single dedicated task keeps cross-domain reasoning concentrated. Service nodes (P5-10) are not blocked on multiple subjects because formal-logic primitives and math prerequisites are mostly subdomain-independent; running service nodes after epistemology core is sufficient calibration.

**Citations.** Subdomain ordering: [`build_plan/P_4_seed_graph_build.md:14`](../../build_plan/P_4_seed_graph_build.md). Cross-bridges runs-last: [`ROADMAP.md`](../../ROADMAP.md) Phase 5.1, [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md) sub-sessions. Schema field: [`engine/session/auto_target.schema.md:24`](../session/auto_target.schema.md).

### T1-E — Cross_domain_dependency predicate: deferred to P5-11 cross-bridge task

**Decision.** The cross-bridge task (P5-11) decides whether to formally introduce the `cross_domain_dependency` predicate to [`product/seed-graph/migrations/PREDICATE_MANIFEST.md`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md) or continue the existing convention of using `pedagogical_prerequisite` with disjoint `domain[]` arrays. Both paths are legitimate; the cross-bridge session adjudicates with full graph context.

**Rationale.** The manifest reserves `cross_domain_dependency` but does not commit it ([T2-G of phase_4_graph_validation.md](phase_4_graph_validation.md) settled the v1 registry at two predicates: `pedagogical_prerequisite`, `historical_influence`). The decision turns on operational ergonomics — does cross-domain reasoning benefit from a dedicated edge type, or does the disjoint-domain convention suffice? That question depends on what the cross-bridges authoring surfaces: if cross-domain edges naturally cluster by a different shape than within-domain prerequisites (different rigor calibration, different bridging concept patterns), the dedicated predicate is warranted. If they're shape-identical to within-domain prerequisites except for the domain[] arrays, the existing convention suffices.

**Artifact.** Tier 3 forward-pointer (T3-B below); cross-bridge task carries the decision.

**Citations.** Reserved predicate: [`product/seed-graph/migrations/PREDICATE_MANIFEST.md:36`](../../product/seed-graph/migrations/PREDICATE_MANIFEST.md). Disjoint-domain convention: same. ADR governing predicate registry: [`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md) T2-G.

### T1-F — Closeout task criteria

**Decision.** P5-12 Closeout's `criteria` block:

```json
[
  {"type": "adr_status", "id": "0052", "status": "Accepted"},
  {"type": "file_exists", "path": "engine/build_readiness/phase_5_closeout.md"},
  {"type": "validate_passes"}
]
```

The closeout task is `complete` when ADR 0052 is Accepted (already true at S-0045 close), the closeout summary file exists, and `validate.py` is clean against the full Phase 5 graph. ENGINE_LOG and STATE.md updates are part of the closeout's authored artifacts but are operational allowlist files (commit anyway, no scope_lock entry needed) per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md).

**Rationale.** Mechanically verifiable; doesn't require subjective judgment. The closeout summary file (`engine/build_readiness/phase_5_closeout.md`) is authored by the closeout session itself; its `file_exists` criterion is the gate that confirms the work shipped. Optional close ADR (if a Phase-5-wide finding warrants one) is not required by the criteria — the closeout session decides whether to author one based on what surfaced.

**Citations.** Criterion types: [`engine/session/auto_target.schema.md:30-82`](../session/auto_target.schema.md). Operational allowlist: [`engine/adr/0051-routine-mode-and-engine-loop.md`](../adr/0051-routine-mode-and-engine-loop.md), CLAUDE.md "Routine-mode posture".

### T1-G — Initial `paused: false`

**Decision.** [`engine/session/auto_target.json`](../session/auto_target.json) is authored with `paused: false`. The user flips the existing `paideia-engine-loop` Claude Code Routine from Manual to Hourly when ready; routine-mode begins firing immediately on the next cadence boundary.

**Rationale.** Authoring `paused: true` and requiring a separate "go" commit would add a pointless ceremony layer. The user's authority to start/stop routine-mode lives at the Routine UI level (Manual vs Hourly toggle); `paused` in the target file is an emergency stop for the AI to use mid-execution if needed, not a deliberate handoff mechanism. Initial state matches the user's intent at master-plan close.

**Citations.** Schema field semantics: [`engine/session/auto_target.schema.md:13`](../session/auto_target.schema.md). User control surface: Claude Code Routine UI (out-of-tree).

## Tier 2 decisions

Concrete answers routine-mode sessions implement without re-deciding. Each carries source citation.

### T2-A — Migration filename ranges per subdomain

The committed prefix scheme per [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) (extended in S-0045):

| Range | Subdomain | Task ID(s) |
|---|---|---|
| `0011-0019` | Epistemology | P5-01a (`0011-0015`), P5-01b (`0016-0019`) |
| `0020-0029` | Ethics | P5-04a (`0020-0025`), P5-04b (`0026-0029`) |
| `0030-0039` | Metaphysics | P5-02a (`0030-0035`), P5-02b (`0036-0039`) |
| `0040-0049` | Philosophy of mind | P5-07a (`0040-0045`), P5-07b (`0046-0049`) |
| `0050-0059` | Service nodes | P5-10 |
| `0060-0069` | Cross-bridges | P5-11 |
| `0070-0079` | Philosophy of language | P5-08 |
| `0080-0089` | Philosophy of science | P5-09 |
| `0090-0099` | Logic | P5-03 |
| `0100-0109` | Political philosophy | P5-05 |
| `0110-0119` | Aesthetics | P5-06 |
| `0120-0129` | Phase 6 self-correction (relocated from `0070-0079`) | (out of Phase 5 scope) |

Per-task migrations follow `NNNN_seed_<subdomain>_partN.sql`. Pre-split tasks may write multiple migration files per session within their assigned sub-range (e.g., P5-01a may write `0011_seed_epistemology_part1.sql` + `0012_seed_epistemology_part2.sql` if the session naturally splits the work). Single tasks may also write multiple migrations within their range; the task is `complete` when all session-authored migrations land and `validate_passes`.

**Citations.** Routing manifest: [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) (updated in S-0045). graph_version increment contract: same file, "graph_version increment contract" section.

### T2-B — `confidence_level` composition target per subdomain

**Decision.** Each subject subdomain task targets:

- `INTERPRETED ≥ 70%` floor
- `SYNTHETIC ≤ 20%` ceiling
- `EXTRACTED` the small remainder (likely <10%, possibly 0% for some subdomains)

Service nodes (P5-10) target the same shape; cross-bridges (P5-11) target `INTERPRETED` for all edges (cross-domain reasoning is interpretive by nature; SYNTHETIC for cross-domain edges signals a particularly speculative bridge that should land in the Opus review queue).

**Rationale.** Per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) (`confidence_level: EXTRACTED | INTERPRETED | SYNTHETIC`) and [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) (structural references provide priors for *generative* authoring, not extracted prose), philosophy nodes are predominantly INTERPRETED. EXTRACTED is reserved for nodes whose definition is directly lifted from a structural reference's entry inventory (rare, since the project doesn't reproduce prose). SYNTHETIC nodes flag the Opus review queue per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md) and [`product/docs/self-correction.md`](../../product/docs/self-correction.md) — keep them small.

The composition is an expectation, not a hard rule. A routine session that produces a SYNTHETIC ratio above 20% does not fail; the validator's `synthetic_review_queue` soft-warn fires at standard threshold and the session records the elevated count in `outcome_summary` for cross-session telemetry per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md).

**Citations.** ADR 0030 confidence_level contract: [`product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md`](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md). ADR 0046 generative-authoring posture: [`product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md`](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md). Self-correction consumer: [`product/docs/self-correction.md`](../../product/docs/self-correction.md).

### T2-C — Soft-warn category recalibrations for philosophy seeds

**Decision.** Routine sessions interpret two soft-warn category thresholds with philosophy-specific framings:

- **`suspicious_cross_domain_ratio`** — fires at >40% per the v1 metric ([phase_4_graph_validation.md T2-D](phase_4_graph_validation.md)). For philosophy subdomains the expected cross-domain ratio is structurally higher than the original calibration target (epistemology bridges to philosophy of science, logic, philosophy of language, philosophy of mind; metaphysics bridges to philosophy of mind, ethics, philosophy of science, philosophy of religion-when-readmitted). Routine sessions treat firing of this category at <60% within philosophy subdomains as expected and record per-subdomain context in `outcome_summary`. Above 60% remains a real signal warranting investigation.
- **`orphan_leaf`** — fires per node with zero inbound + zero outbound prerequisite-type edges. Routine sessions producing partial subdomain seeds (the b-halves of pre-split subdomains, or the first migration in a multi-migration single-task subdomain) will produce orphan leaves that resolve when the rest of the subdomain authoring lands. Acceptable orphan-leaf density during partial Phase 5 closure is up to 30% of the session's authored nodes; cross-bridges (P5-11) is the natural resolution surface.

The validator code is unchanged; the recalibration is interpretive and lives in routine-session `outcome_summary` annotations. If post-Phase-5 telemetry shows the threshold itself should change in code, that lands in a follow-up session as a P_2-style refinement (not an ADR 0016 supersession).

**Citations.** Original metric: [`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md) T2-D, [`engine/tools/validate.py:1276-1278`](../tools/validate.py). Cross-domain porosity: [ADR 0007](../../product/adr/0007-cross-domain-porosity.md). Forward-pointer for code-level threshold change: T3-D below.

### T2-D — Per-task `scope_lock.allowed_paths` shape

**Decision.** Per-task `scope_lock.allowed_paths` are tight, anchored to the task's migration range. Every subject subdomain task and the service-nodes/cross-bridges tasks (P5-01a through P5-11) **also include `PREDICATE_MANIFEST.md` and `ROUTING.md`** in their scope_lock — any task may discover a new edge type that warrants registry entry, and ROUTING.md gets a per-session-narrative entry per session per the per-session-narrative discipline at [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md). The closeout task (P5-12) instead has scope_lock over the build-readiness summary file plus the ADR directories. Examples:

- **P5-01a Epistemology core:** `["product/seed-graph/migrations/0011_*.sql", ..., "product/seed-graph/migrations/0015_*.sql", "product/seed-graph/migrations/PREDICATE_MANIFEST.md", "product/seed-graph/migrations/ROUTING.md"]`
- **P5-11 Cross-bridges:** same shape, range `0060_*.sql` through `0069_*.sql` plus `PREDICATE_MANIFEST.md` and `ROUTING.md`. The formal `cross_domain_dependency` predicate decision lives in this task per T1-E; the broader ability to register predicates exists for every task because cross-domain edges may be authored mid-subdomain (rare but legitimate when a concept is structurally cross-domain at first authoring).
- **P5-12 Closeout:** `["engine/build_readiness/phase_5_closeout.md", "engine/adr/*.md", "product/adr/*.md", "engine/adr/README.md", "product/adr/README.md"]` (ADR scope_lock is broad because closeout may author a Phase-5-wide ADR; the README index entry update accompanies it).

The operational allowlist (current.json, current_plan.md, auto_target.json (status fields only), archive/S-*.json, register_state.json, ENGINE_LOG.md, HANDOFF.md, STATE.md) is unioned automatically per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) and is not listed in scope_lock.

**Rationale.** Tight globs maximize the anti-rogue guarantee per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) and [`engine/session/auto_target.schema.md:148`](../session/auto_target.schema.md). The 5-slot per-task glob list (vs. a single `0011_*` wildcard) is intentional: each task owns a specific sub-range, preventing accidental writes to a sibling task's range.

**Citations.** Glob semantics: [`engine/tools/check_routine_scope.py:116-157`](../tools/check_routine_scope.py) (segment-aware matching). Operational allowlist: [`engine/adr/0051-routine-mode-and-engine-loop.md`](../adr/0051-routine-mode-and-engine-loop.md), CLAUDE.md "Routine-mode posture". scope_lock discipline: [`engine/adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md`](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md).

### T2-E — Per-task criteria shape

**Decision.** Each subject subdomain task uses a two-criterion combo of objective, runnable checks:

```json
[
  {"type": "migration_applied", "id": "0011_seed_epistemology_part1"},
  {"type": "validate_passes"}
]
```

The `migration_applied` criterion targets the **first migration** in the task's prefix sub-range (e.g., `0011_seed_epistemology_part1` for P5-01a). The routine session may write multiple migrations within its sub-range; the task is `complete` when at least the first migration is applied AND `validate.py` returns zero hard-fails. Concept-count expectations and confidence_level composition (per T2-B) are interpretive guidance for the routine session, not gate criteria — soft-warns and `outcome_summary` annotations carry the per-session telemetry forward across the routine sequence.

Per-task first-migration ids:

| Task | First migration id | Range allows |
|---|---|---|
| P5-01a Epistemology core | `0011_seed_epistemology_part1` | `0011-0015` |
| P5-01b Epistemology specialized | `0016_seed_epistemology_part1` | `0016-0019` |
| P5-02a Metaphysics core | `0030_seed_metaphysics_part1` | `0030-0035` |
| P5-02b Metaphysics specialized | `0036_seed_metaphysics_part1` | `0036-0039` |
| P5-03 Logic | `0090_seed_logic_part1` | `0090-0099` |
| P5-04a Ethics metaethics+normative | `0020_seed_ethics_part1` | `0020-0025` |
| P5-04b Ethics applied | `0026_seed_ethics_part1` | `0026-0029` |
| P5-05 Political philosophy | `0100_seed_political_philosophy_part1` | `0100-0109` |
| P5-06 Aesthetics | `0110_seed_aesthetics_part1` | `0110-0119` |
| P5-07a Philosophy of mind core | `0040_seed_mind_part1` | `0040-0045` |
| P5-07b Philosophy of mind consciousness/specialized | `0046_seed_mind_part1` | `0046-0049` |
| P5-08 Philosophy of language | `0070_seed_language_part1` | `0070-0079` |
| P5-09 Philosophy of science | `0080_seed_science_part1` | `0080-0089` |
| P5-10 Service nodes | `0050_seed_services_part1` | `0050-0059` |

P5-11 cross-bridges uses: `migration_applied` for `0060_seed_crossbridges_part1` + `validate_passes`. P5-12 closeout uses the criteria in T1-F.

**Rationale.** Migration-applied + validate-passes is objective, runnable, requires zero new predicate registration. The "minimum concept count" framing was rejected as a gate criterion because it would require introducing three new predicates (`seed_concepts_count_at_least_n`, `service_node_inventory_complete`, `cross_bridge_coverage_complete`) with database fixtures and tests — scope-creep beyond S-0045's master-plan responsibilities. The session-time discipline (concept count, INTERPRETED ratio, orphan-leaf density) is communicated through phase_5.md's T2-B and T2-C plus per-routine-session `outcome_summary` annotations, not through machine-checkable criteria. If post-Phase-5 telemetry shows machine-checkable concept-count gates would have caught real failures the soft-warn telemetry missed, the predicate registration lands in a follow-up session per ADR 0051's master-plan revision discipline.

**Citations.** Schema criterion types: [`engine/session/auto_target.schema.md:30-82`](../session/auto_target.schema.md). Migration filename convention: T2-A above and [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md). validate.py contract: [`engine/tools/validate.py`](../tools/validate.py).

### T2-F — `depends_on` graph encoding in `auto_target.json`

The graph from T1-D encoded as JSON `depends_on` arrays:

| Task | `depends_on` |
|---|---|
| P5-01a Epistemology core | `[]` |
| P5-01b Epistemology specialized | `["P5-01a"]` |
| P5-02a Metaphysics core | `["P5-01a"]` |
| P5-02b Metaphysics specialized | `["P5-01a", "P5-02a"]` |
| P5-03 Logic | `["P5-01a"]` |
| P5-04a Ethics metaethics+normative | `["P5-01a"]` |
| P5-04b Ethics applied | `["P5-01a", "P5-04a"]` |
| P5-05 Political philosophy | `["P5-01a"]` |
| P5-06 Aesthetics | `["P5-01a"]` |
| P5-07a Philosophy of mind core | `["P5-01a"]` |
| P5-07b Philosophy of mind consciousness/specialized | `["P5-01a", "P5-07a"]` |
| P5-08 Philosophy of language | `["P5-01a"]` |
| P5-09 Philosophy of science | `["P5-01a"]` |
| P5-10 Service nodes | `["P5-01a"]` |
| P5-11 Cross-bridges | `["P5-01a", "P5-01b", "P5-02a", "P5-02b", "P5-03", "P5-04a", "P5-04b", "P5-05", "P5-06", "P5-07a", "P5-07b", "P5-08", "P5-09", "P5-10"]` |
| P5-12 Closeout | `["P5-11"]` |

No cycles; eligibility walks correctly per [`engine/tools/check_target.py`](../tools/check_target.py)'s scheduler.

### T2-G — Adversarial reconnaissance: anti-patterns specific to philosophy seed authoring

Five corruption vectors enumerated with the soft-warn category that catches each:

1. **Cross-domain edge collisions.** Two subdomain sessions authoring the same cross-domain edge independently (e.g., epistemology and philosophy of science both add a `pedagogical_prerequisite` from "scientific_method" to "induction"). Caught by: `dangling_edge` is N/A here (edges land successfully); the duplicate manifests as `UNIQUE (source_id, target_id, edge_type)` constraint violation at insert time per [`product/seed-graph/migrations/0003_edges.sql:55`](../../product/seed-graph/migrations/0003_edges.sql), which fails the migration. Mitigation: P5-11 cross-bridges runs after all subjects, so individual subdomain sessions do NOT author cross-domain edges (they author within-domain prerequisite edges only). Cross-domain edges are P5-11's exclusive responsibility.

2. **Bridge-concept naming drift.** A service-node concept named `mathematical_induction` in one session and `induction_mathematical` in another. Caught by: the granularity principle clarity in T2-A migration ranges, plus PREDICATE_MANIFEST.md's expectation that service-node concept names are stable. Mitigation: the service-node task (P5-10) is single-task (not pre-split); naming consistency is the session's responsibility within its scope.

3. **Confidence_level composition skew.** A subdomain produces predominantly SYNTHETIC nodes (>50%), signaling either over-aggressive generation or under-grounded authoring. Caught by: `synthetic_review_queue` soft-warn count per session; T2-B sets the expectation. Mitigation: the master plan's INTERPRETED ≥ 70% floor; routine session that exceeds the SYNTHETIC ceiling annotates in `outcome_summary` and the next session's gate-readiness check surfaces the trend.

4. **Domain-tag cardinality explosions.** A concept tagged with 5+ subdomains (e.g., a Kant concept tagged `epistemology`, `metaphysics`, `mind`, `language`, `science`). Caught by: no current validator check; the master plan establishes a max-tag policy. Mitigation: per-subdomain authoring sessions tag conservatively (typically 1-2 domains); tags 3+ are admissible but flagged in the session's `outcome_summary` for cross-session review. If a concept legitimately spans 4+ subdomains, the per-subdomain compound-domain handling rule in [ROUTING.md](../../product/seed-graph/migrations/ROUTING.md) directs which subdomain session owns the migration; cross-bridges later resolves cross-domain edges from the canonical home.

5. **Orphan-leaf accumulation in partial seeds.** Per T2-C; routine sessions producing partial subdomain seeds will produce orphan leaves that resolve when the rest of the subdomain authoring lands. The b-halves of pre-split subdomains are particularly susceptible. Mitigation: the orphan_leaf threshold (up to 30% of session's authored nodes) gives partial closures room; cross-bridges (P5-11) is the resolution surface for any orphans surviving subdomain interior closure.

**Citations.** UNIQUE constraint: [`product/seed-graph/migrations/0003_edges.sql:55`](../../product/seed-graph/migrations/0003_edges.sql). Soft-warn categories: [`engine/tools/validate.py:1265-1278`](../tools/validate.py), [`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md) T2-D. Domain-tag cardinality: derived from [`product/docs/architecture.md`](../../product/docs/architecture.md) `domain[]` array; no hard cap currently.

### T2-H — Source-acquisition discipline per subdomain

Per [ADR 0046](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md) and the [Phase 4.5 survey](../../product/docs/content-strategy.md):

- **All 9 subject subdomains:** SEP (primary), IEP (secondary), Wikipedia (CC BY-SA, accessible summaries) — **consultable for graph-shape value, no prose reproduction**. Graph-shape extraction is uncopyrightable per Feist; entry text is copyrightable and never hosted.
- **Routledge / Oxford (philosophy collection):** require legitimate channels (institutional library access, publisher subscription, per-volume purchase). Per-source acquisition decisions land as ADRs in the consuming routine session if the access path involves non-trivial budget impact.
- **Logic (P5-03) supplementary:** ConceptNet `/r/HasPrerequisite` (CC BY-SA) — usable as sanity-check for service-node logical-prerequisite chains. Mathlib (Apache 2.0) — usable for soundness checks on mathematical scaffolding the service nodes consume.
- **Excluded:** Önduygu philo-browser propositions+edges layer (graph-shape-incompatible — dialectical, not prerequisite). Tag layer is usable as concept-vocabulary checklist for analytic-tradition coverage.

Routine sessions consult the [Phase 4.5 survey](../../product/docs/content-strategy.md) at boot to identify per-subdomain inventories and respect access-warrant tradeoffs. Sessions do NOT acquire paywalled sources without user authorization (the user's per-source budget approval is the surface; routine sessions running unattended cannot make subscription commitments).

**Citations.** ADR 0046: [`product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md`](../../product/adr/0046-structural-reference-posture-extends-to-philosophy-reference-works.md). Survey: [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md) "Cross-Domain Reference Inventories — Survey". ADR 0011: [`product/adr/0011-no-hosted-copyrighted-material.md`](../../product/adr/0011-no-hosted-copyrighted-material.md).

## Tier 3 forward pointers

Decisions explicitly deferred. Each names the deferral and where it's marked.

### T3-A — Branch-based rollback verification (inherited)

**Deferral.** Phase 6+ pending local Supabase CLI setup or explicit user budget approval for development branches. Inherited from [phase_3_sql.md](phase_3_sql.md) T3-G and reaffirmed at [phase_4_graph_validation.md](phase_4_graph_validation.md) T3-A. Phase 5 routine sessions are read+write against the live `paideia-dev` DB; rollback verification is orthogonal to the validator's correctness. If any Phase 5 routine session opts into branch-based verification under user-approved budget, the T3 forward-pointer settles at that point.

**Marked at.** This Tier 3 entry; STATE.md's next-session work-item carries forward at session shutdown if any Phase 5 routine session changes the disposition.

### T3-B — `cross_domain_dependency` predicate formal introduction

**Deferral.** P5-11 cross-bridges task. Per T1-E, the cross-bridge session adjudicates whether to formally introduce the predicate or continue the disjoint-domain convention.

**Marked at.** This Tier 3 entry; PREDICATE_MANIFEST.md's reserved entry; T1-E explicitly defers.

### T3-C — Per-subdomain rigor_score calibration

**Deferral.** Per-routine-session basis. Each subject subdomain task computes `rigor_score_computed` per the formula in [`product/docs/architecture.md:69-77`](../../product/docs/architecture.md); calibration of overrides via `rigor_score_adjustment` is per-node-instance work, not a phase-level decision. The validator's `missing_rigor_score` soft-warn fires on default-value detection.

**Marked at.** This Tier 3 entry; per-routine-session `outcome_summary` if calibration concerns surface.

### T3-D — Soft-warn threshold code changes

**Deferral.** Post-Phase-5 telemetry-driven. T2-C names the philosophy-specific reinterpretation (cross-domain ratio threshold relaxed to 60%, orphan-leaf density acceptable up to 30%). If post-Phase-5 telemetry shows the thresholds in `engine/tools/validate.py` should change in code, that lands in a follow-up session as a P_2-style refinement (not an ADR 0016 supersession — the categories are contract-stable; the thresholds are tuning parameters).

**Marked at.** This Tier 3 entry; closeout (P5-12) `outcome_summary` carries the trend evidence forward.

### T3-E — Adversarial-triage prompt template

**Deferral.** First-real-use of the [structural-reference parser tool](../tools/parse_structural_reference.py) per [ADR 0047](../adr/0047-structural-reference-parser-tool-and-adversarial-triage-workflow.md). The parser is runnable ad-hoc; routine sessions may consult it but the prompt template is deferred to first-real-use per ADR 0047.

**Marked at.** This Tier 3 entry; ADR 0047 itself names the deferral.

### T3-F — Mid-session context-pressure signal

**Deferral.** [Issue #4](https://github.com/StarshipSuperjam/paideia/issues/4) (`enhancement`). Routine sessions have no live context-pressure detection; CLAUDE.md's 60/70/80 budget percentages are AI posture, not machinery. S-0045 engineers around the gap by sizing tasks pre-execution per T1-B; long-term the gap is real and worth a mechanism. Decoupled from Phase 5 entirely.

**Marked at.** Issue #4; Tier 3 entry.

### T3-G — Philosophy of religion subdomain readmission criterion

**Deferral.** Post-Phase-5. Per [ADR 0052 §"Out of scope"](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md), philosophy of religion folds into metaphysics for this MVP; class-boundary admit-criterion governs future readmission (top-level coverage in SEP/Routledge browse categories AND graph-shape distinctness from existing 9 subdomains AND non-trivial concept inventory at the granularity principle). A future session that surfaces a concrete readmission case lands a small ADR; the criterion is settled.

**Marked at.** This Tier 3 entry; [ADR 0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) class-boundary clause.

## Success criteria for routine-mode Phase 5 execution

Phase 5 closes when:

- All 16 tasks in [`engine/session/auto_target.json`](../session/auto_target.json) reach `status: complete` (or HANDOFF entries adjudicate the remainder if `max_sessions: 18` exhausts).
- `engine/tools/validate.py --validate-only` runs clean against the full Phase 5 graph (zero hard-fails; soft-warns recorded per category in archives).
- The closeout task (P5-12) lands [`engine/build_readiness/phase_5_closeout.md`](phase_5_closeout.md) summarizing per-subdomain coverage, soft-warn telemetry trends across the routine session sequence, and the predicate registry's final state (whether `cross_domain_dependency` was formally introduced or not per T1-E/T3-B).
- Per-subdomain success per [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md): each subdomain task closes with zero hard-fails; soft-warn counts recorded per category in routine-session `outcome_summary`; migration files atomically attributable to the routine session via the session's ENGINE_LOG entry.
- ADR 0052 status remains Accepted at Phase 5 close. If a Phase-5-wide finding warrants superseding ADR 0052 (e.g., a subdomain proves to be unworkable at the granularity principle), the closeout session authors the supersession ADR; closeout's `validate_passes` criterion is met regardless.

**Per-routine-session checkpoint (any task):**

- The routine session reads this report at boot per [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md). If any Tier 1 finding shows unresolved (the resolution artifact is missing, the cited ADR is in `Proposed` or non-existent, the cited canon-file does not contain the cited content), the routine session refuses the task and writes HANDOFF.
- The routine session's plan-then-scope-check ([`engine/tools/check_routine_scope.py --plan engine/session/current_plan.md`](../tools/check_routine_scope.py)) confirms the session's authored plan stays within the active task's `scope_lock.allowed_paths` ∪ operational allowlist.
- Pre-commit hook hard-fails any commit that touches paths outside scope_lock per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md).

## Authored resolution artifacts (in S-0045)

Master plan session deliverables:

- [`engine/build_readiness/phase_5.md`](phase_5.md) (this file)
- [`engine/session/auto_target.json`](../session/auto_target.json) — executable contract
- [`product/adr/0052-phase-5-philosophy-subdomain-decomposition.md`](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) — new ADR
- [`product/adr/README.md`](../../product/adr/README.md) — ADR index entry for 0052
- [`product/seed-graph/migrations/ROUTING.md`](../../product/seed-graph/migrations/ROUTING.md) — prefix scheme extended (5 new subdomain ranges, Phase 6 relocated)
- [`ROADMAP.md`](../../ROADMAP.md) Phase 5.1 — list updated to 9 subjects + services + cross-bridges + closeout
- [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md) — sub-sessions list and success criteria updated
- [`engine/STATE.md`](../STATE.md) — last-session pointer + next-session work item updated at session shutdown
- [`engine/ENGINE_LOG.md`](../ENGINE_LOG.md) `[Unreleased]` — Added/Changed entries for the new artifacts and canon-realignment edits
- GitHub Issue #4 (mid-session context-pressure signal, `enhancement`)
- MemPalace `decision`-tagged drawer for ADR 0052 (captured at session shutdown per [ADR 0036](../adr/0036-expression-contract-for-inward-documents.md) two-layer rule)

No new predicates registered in [`engine/tools/check_target.py`](../tools/check_target.py)'s `PREDICATE_REGISTRY`. Per T2-E, the criteria use the existing `migration_applied` + `validate_passes` types only. If post-Phase-5 telemetry surfaces concept-count gates as load-bearing, predicate registration lands in a follow-up master plan session per ADR 0051's revision discipline.

## See also

- [`build_plan/P_4_seed_graph_build.md`](../../build_plan/P_4_seed_graph_build.md) — the Phase 5 chunk; updated in S-0045 to reflect this gate's decisions.
- [`engine/session/auto_target.json`](../session/auto_target.json) — the executable contract; encodes T1/T2 resolutions.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the gate protocol this report executes.
- [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — no-descoping clause; ratified by ADR 0052.
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — routine-mode architecture; under which this gate is also the master plan.
- [ADR 0052](../../product/adr/0052-phase-5-philosophy-subdomain-decomposition.md) — 9-subdomain decomposition; this gate's central T1-A artifact.
- [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) — Layer 1 reference for routine-mode session procedure.
- [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) — gate procedure operational doc.
- [`engine/operations/seed-chunked-authoring.md`](../operations/seed-chunked-authoring.md) — per-routine-session migration workflow.
- [`engine/build_readiness/phase_4_graph_validation.md`](phase_4_graph_validation.md) — prior gate report; T3-A (branch-based rollback) inherited.
- [`engine/build_readiness/phase_3_sql.md`](phase_3_sql.md) — earlier gate report; T3-G (validate_graph stub) closed at S-0035; T3-A inherited via phase_4.
- [`product/docs/content-strategy.md`](../../product/docs/content-strategy.md) — Phase 4.5 input dataset survey; per-subdomain reference inventories.
- [`product/docs/architecture.md`](../../product/docs/architecture.md) — node/edge schema; granularity principle.
