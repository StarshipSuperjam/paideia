# Paideia Implementation Plan

> **Read the [Status](#status) section first.** This document is a phase-by-phase checklist for building Paideia from its current design state to a working teaching prototype, adopting the InfoGenesis project's session-protocol patterns. Pick up at the current phase in any session.

---

## Status

**Current phase:** Pre-Phase 0 — in progress (Pre-0.1 closed; Pre-0.2 and Pre-0.3 pending)
**Last session:** 2026-04-28 (Pre-Phase 0.1 closed — `git init`, `.gitignore`, `.env.example`, initial commit `b91426e`, pushed to `StarshipSuperjam/paideia` private. Homebrew + `gh` 2.92.0 installed and authenticated.)
**Next action:** Pre-0.2 — user confirms `ANTHROPIC_API_KEY` in shell env, creates Supabase project `paideia-dev` (free tier), enables `pgvector` extension, copies URL + anon key + service role key into a local `.env` (gitignored). Then Pre-0.3 — install Supabase MCP server in `~/.claude/settings.json`. Then a fresh `Start Engine` opens Phase 0.
**Blockers:** None for Claude — Pre-0.2 and Pre-0.3 are user-handled (account creation, dashboard work, global config edits). Optional cleanup: git committer identity is `shanekidd@Shanes-MacBook-Air.local` — set `git config --global user.email` before further commits if a different attribution is wanted.

When picking up a session, update this block at the end with the date, what was completed, and what's next. After Phase 0 closes, this block is replaced by the SA/CL workflow (the most recent SA entry's `next_session.recommended_step` becomes authoritative).

---

## How to Use This Document

This file is the **transitional build plan** — the bootstrap structure that runs until the SA/CL session-protocol layer is operational. After Phase 0 closes, the transition happens automatically:

1. **Now through Phase 0:** read this file at session start. Find the current phase. Each phase has checkboxes for steps; check them off as completed and update the Status block at session close. A new session should be able to figure out what to work on from the Status block alone.

2. **After Phase 0 closes:** `CLAUDE.md` and `OPERATIONS.md` are written, `SA-001_adopt_session_protocol.md` exists, and the `Start Engine` trigger phrase is in effect. From that point forward, sessions read the most recent SA entry's `next_session.recommended_step` field instead of this document. This file remains as a high-level reference but is no longer the source of truth.

3. **For the user (manual mode):** at any point, you can pause the automated SA/CL workflow and pick up from this checklist instead — useful if a phase needs your judgment rather than autonomous execution. Just note in the Status block which mode you're operating in.

**Each phase below has two markers:**
- 🤖 **Claude Code handles** — Claude can execute autonomously
- 👤 **You handle** — requires your action (account creation, billing, dashboard work, decisions)

---

## Why This Plan Exists (Brief)

InfoGenesis (the user's parallel POS-documentation knowledge graph project) was built in ~30 hours of autonomous Claude Code sessions across 64 closed sessions, producing a 2,531-node graph. The throughput came from a session-protocol layer (SA entries + CL entries + eager slot claim + auto-mode + narrow interrupt criteria) that lets a fresh session resume cold from a single audit file.

Paideia is at the analogous inflection point: 8 of 14 design-pack sessions closed, schema and pedagogy decisions settled, the 45-node thinker-level prototype archived, and the seed graph rebuild reclassified as an implementation task. **Without InfoGenesis-style session protocol, every Paideia build session would need a human briefing.** This plan adopts the patterns that transfer (session protocol, chunked authoring with routing manifest, rendering policy as a standalone artifact, three-level node confidence, layered decision tracking) and skips the patterns that don't (`_archive/` snapshots, JSON-LD storage, OWL/RDF semantics, sample-question battery as organizing principle).

The full source report is at [infogenesis_report_for_paideia.md](infogenesis_report_for_paideia.md).

---

## Pre-Phase 0 — Platform Setup

**Output:** git remote pushed to GitHub, Supabase project created, MCP wired into Claude Code, all environment variables set.

**business.md already settles the right starting position:** personal accounts on every service, transfer to a commercial entity if/when one forms.

### Pre-0.1 — Initialize Git and Push to GitHub

🤖 **Claude Code handles:** `git init`, `.gitignore`, `.env.example`, initial commit
👤 **You handle:** create the private GitHub repo on your personal account; provide the remote URL or run `gh auth login` so Claude can use the `gh` CLI

Steps:
- [ ] `git init` in `/Users/shanekidd/Documents/Claude_Files/Paideia/`
- [ ] Create `.gitignore` (covers `.claude/`, `.env*`, `node_modules/`, build outputs, OS cruft)
- [ ] Create `.env.example` (template; real `.env` gitignored)
- [ ] Stage and commit current state ("initial commit: design phase, 8 of 14 prompt-pack sessions closed")
- [ ] **You:** create private repo `shanekidd/paideia` (or chosen name) on GitHub
- [ ] `git remote add origin` + `git push -u origin main`

Why personal account, why private: business.md ("Building under personal accounts is the correct starting position. GitHub repo transfer to an org preserves forks, issues, and history with automatic URL redirect."). Private because the seed graph and pedagogical content are part of the commercial moat.

### Pre-0.2 — Stand Up the Third-Party Stack

| Platform | Purpose | Cost | How Claude connects | When |
|---|---|---|---|---|
| **Anthropic API** | Claude models for teaching, Sonnet/Opus self-correction split | Pay-per-use; Claude Max covers build sessions | API key in env var `ANTHROPIC_API_KEY`; separate from the Max subscription Claude Code itself uses | Now |
| **GitHub** | Version control, issue tracking, eventual CI | Free for private repos | Native — `gh` CLI plus the standard git remote | Pre-0.1 |
| **Supabase** | Postgres + pgvector + auth + storage | Free tier sufficient through Phase 5; $25/mo Pro tier when scaling | **Supabase MCP server** (`@supabase/mcp-server-supabase`) — direct DB read/write from Claude Code via MCP. https://github.com/supabase-community/supabase-mcp | Pre-0.2 |
| **Vercel** | Frontend hosting + preview deployments | Free Hobby tier through prototype phase | GitHub integration — auto-deploys on push to main; preview deployments per-PR | Phase 9 |
| **DeepTutor fork** | Apache 2.0 base for the close-reading agent infrastructure | Free (open source) | `git clone` + fork on GitHub; vendored subdirectory or git submodule | Phase 7 |
| **Apple Developer Program** | iOS App Store distribution | $99/year | Not connectable to Claude — manual deployment via Xcode/Transporter. **Enroll early** (2-4 week lead time per business.md) | Start enrollment Phase 8 |
| **Google Play Console** | Android Play Store distribution | $25 one-time | Not connectable — manual. Faster onboarding than Apple | Phase 9 |
| **Amazon Associates** | Affiliate revenue on book recommendations | Free (revenue share) | Not connectable — links generated using your associate tag in env var | Deferred — until commerce layer |

**Required for Pre-Phase 0:** Anthropic API, GitHub, Supabase. **Deferred:** everything else.

👤 **You handle:**
- [ ] Confirm `ANTHROPIC_API_KEY` is set in env (separate from Max subscription used by Claude Code itself)
- [ ] Create Supabase project `paideia-dev` (free tier)
- [ ] Enable `pgvector` extension in Supabase dashboard
- [ ] Copy project URL + anon key + service role key into local `.env` (gitignored)

### Pre-0.3 — Wire Up MCP Connections

👤 **You handle:** install the Supabase MCP server in Claude Code's settings (modifies global config; needs your authorization)
🤖 **Claude Code handles:** verify connectivity once installed

Steps:
- [ ] **You:** add Supabase MCP server to `~/.claude/settings.json` or project-level `.claude/settings.local.json`
- [ ] Verify: `claude mcp list` shows Supabase connected
- [ ] Test with a trivial query (e.g., `SELECT current_database()`)

### Pre-Phase 0 Verification

From a fresh Claude Code session in the project directory, the following all work:
- [ ] `git status` (clean repo, remote configured)
- [ ] `gh repo view` (private repo on personal account)
- [ ] An MCP-mediated Supabase query returns results
- [ ] `echo $ANTHROPIC_API_KEY` returns a key

---

## Phase 0 — Adopt Session Discipline (Foundation)

**Output:** a project that supports cold-start Claude Code sessions. **The single most important phase. Without it, autonomous iteration is unreachable.**

### 0.1 — Directory and Counter Scaffolding

🤖 **Claude Code handles:** all file creation

- [ ] Create `session_audit/register_state.json` — counter (`next_id: "002"` after SA-001 is written, `last_written: "SA-001"`, plus `description` and `format` fields per InfoGenesis pattern)
- [ ] Create empty `session_audit/entries/` directory
- [ ] Create `change_log/register_state.json` — counter
- [ ] Create empty `change_log/entries/` directory
- [ ] Create `provisional-decisions.md` — empty header (the layered-decision-tracking layer Paideia is missing)

### 0.2 — Procedural Docs

🤖 **Claude Code handles:** writing OPERATIONS.md and CLAUDE.md

- [ ] Create `OPERATIONS.md` (~400 lines) with sections:
  - (a) trigger phrases (`Start Engine` for build sessions, default-path otherwise)
  - (b) nine-step startup procedure (worktree-master parity check, sweep stale worktrees, read CONTEXT.md, list build_plan/ and read MANIFEST.md, read most recent SA entry, discover filesystem state, read step-specific artifacts, claim SA slot eagerly with `in_progress` stub, commit + master FF)
  - (c) session-shutdown procedure (`audit_graph.py --validate-only` audit pass, spot-check, fix-inline-when-small rule, rewrite SA stub in place, write CL entries, commit + master FF)
  - (d) SA schema (markdown with YAML frontmatter)
  - (e) CL schema (pure JSON)
  - (f) auto-mode interrupt criteria (irreversible-with-unclear-path / unsolvable / destructive-action only)
  - (g) budget tiers (60/70 substantive, 70/80 mechanical)
  - (h) end-state-quality first-pass principle
  - (i) bundling rule
  - (j) material-change criteria for CL entries
  - (k) scope of CL discipline (state-of-record only — not React/API/web app code)
- [ ] Create `CLAUDE.md` (~50 lines) — orientation entry point. Points at OPERATIONS.md for procedural depth, CONTEXT.md for carry-forward state, names the SA/CL discipline, names `Start Engine` as the trigger phrase
- [ ] **Delete `PROJECT_SETUP.md`** — superseded by CLAUDE.md; build moves entirely to Claude Code

### 0.3 — Bootstrap SA-001 (Retroactive)

🤖 **Claude Code handles:** writing SA-001

- [ ] Create `session_audit/entries/SA-001_adopt_session_protocol.md` (markdown with YAML frontmatter)
  - Dense `entry_state` paragraph naming the 8 closed prompt-pack sessions, the 12 carry-forward commitments, current tensions, archived prototype, the 4 settled design sessions, Pre-Phase 0 platform setup state
  - Dense `exit_state` paragraph naming what changed (directories created, files written, PROJECT_SETUP.md deleted)
  - `decisions` array — D1 through D10+ per the [Decisions Settled During Planning](#decisions-settled-during-planning) section below
  - `next_session.recommended_step` naming Phase 1
- [ ] Update `session_audit/register_state.json` (`next_id: "002"`, `last_written: "SA-001"`)
- [ ] Update `change_log/register_state.json` if any CL entries were written

### 0.4 — Codify the Layered Decision-Tracking System

The five layers, three of which are non-trivial in Paideia:

1. **Carry-forward** → CONTEXT.md ✓ (already exists)
2. **Open questions** → tensions.md ✓ (already exists)
3. **Provisional decisions** → `provisional-decisions.md` (created in 0.1)
4. **Session-level decisions** → SA entry `decisions` field (D-NN globally numbered)
5. **Watch-flag** → fold into tensions.md with explicit tagging; don't separate-file until volume justifies

🤖 **Claude Code handles:** writing the empty `provisional-decisions.md` header (already in 0.1) and adding a section to OPERATIONS.md describing the five layers and their interaction

### Phase 0 Verification

- [ ] A fresh Claude Code session types `Start Engine` and successfully completes the nine-step startup procedure: reads CONTEXT.md, locates the next session in build_plan (or this file pre-Phase 2), reads SA-001, claims SA-002, writes a stub
- [ ] The session can then close cleanly with audit pass + CL entries + master fast-forward

**Test: spawn a single Claude Code session and observe whether it boots without human briefing.** If yes, Phase 0 is closed and the SA/CL workflow takes over from this document.

---

## Phase 1 — Contract Lock

**Output:** every remaining design ambiguity that would propagate into the seed graph is settled, written down, and audit-checked.

### 1.1 — Close Pending Prompt-Pack Sessions (9-14)

The 14-session prompt pack lives at [prep-paideia-prompt-pack.md](prep-paideia-prompt-pack.md). Sessions 9-14 are still open. Per blocking priority:

- [ ] **Session 9 (Engagement Depth Aggregation)** — blocks prototype work. Run as the first SA-tracked session.
- [ ] **Session 10 (Decay Parameter Verification)** — depends on 9.
- [ ] **Session 11 (Historical Maximum Tracking)** — small schema decision, independent.
- [ ] **Session 12 (Fork Maintenance Timeline)** — defer; resolve after Phase 7 prototype lands.
- [ ] **Session 13 (Gamification & Milestone Tone)** — defer; mostly resolved as a sensibility, not a feature decision.
- [ ] **Session 14 (Media Edge Quality)** — defer until Phase 5 surfaces concrete cases.

🤖 Claude Code handles each session as an SA-tracked work item with the user's input where judgment is required.

### 1.2 — Adopt the InfoGenesis-Surfaced Additions

Settled-by-the-report items, recorded as carry-forward decisions:

- [ ] **Three-level node confidence** (`EXTRACTED | INTERPRETED | SYNTHETIC`) — added to the node schema in [architecture.md](architecture.md). Currently the schema tracks `provenance` (`human | ai_proposed | ai_confirmed`) and a numeric `confidence`. The InfoGenesis discipline argues for an explicit categorical level orthogonal to provenance; synthetic nodes are first candidates for self-correction review.
- [ ] **Schema-drift audit categories** — `audit_graph.py` checks declared-predicate coverage and attribute-shape consistency from session zero, not after-the-fact. (InfoGenesis discovered 128 PointerBindings with divergent schema variants at SA-053; preventable with audit checks earlier.)
- [ ] **End-state-quality first-pass** as a hard rule for the seed graph: every node emerges complete against the locked contract — full attribute set, declared label, at least one provenance pointer, honest confidence label. Defects fix in-session, never deferred.

### 1.3 — Write `AGENT_INSTRUCTIONS.md` (Rendering Policy)

Standalone artifact extracted from [pedagogy.md](pedagogy.md). pedagogy.md is *why* the expression contract exists; AGENT_INSTRUCTIONS.md is the operational rules the Sonnet teaching layer reads as system instructions.

- [ ] **Forbidden tokens.** Mastery state names ("exposed/proficiency/mastery" never user-facing as terms), prerequisite-edge framing, evidence-event references, scaffolding-proximity language, weight/confidence/provenance exposure, graph_version references, tension-log mechanism, Sonnet/Opus references, "service node," "scaffolding," construction-commentary IDs (`SA-NNN`, `D-NN`, `CL-NNN`, `OQ-N`).
- [ ] **Surviving tokens.** Concept names (modus ponens, the Forms, Eudaimonia, Transcendental Idealism) survive verbatim. Domain-area names (epistemology, ethics) survive when relevant.
- [ ] **Scaffolding-vs-concept distinction.** Concepts by name; meta-categories paraphrased into product role.
- [ ] **Citation rules.** When the system references SEP or other sources for onward reading, what's the citation form?
- [ ] **Uncertainty posture.** "Let's check this together" instead of "your inferred-tier evidence is weak."
- [ ] **Worked example.** A learner asks "why are we doing this next" — show the graph-voice (forbidden) version and the pedagogical-voice (passing) version reasoning over the same retrieved facts.

### 1.4 — Phase 1 SA Close = Contract Locked

After Phase 1, every subsequent session's audit pass enforces the contract; no separate rework passes.

### Phase 1 Verification

- [ ] `audit_graph.py --validate-only` (built in Phase 4 but stub earlier if needed) hard-fails on a deliberately-introduced cycle and soft-warns on an undeclared predicate
- [ ] AGENT_INSTRUCTIONS.md worked example passes when fed to Sonnet against a stub graph
- [ ] CONTEXT.md updated: new "13. Three-level node confidence" carry-forward; references AGENT_INSTRUCTIONS.md, OPERATIONS.md, CLAUDE.md, provisional-decisions.md in file index; PROJECT_SETUP.md row removed
- [ ] tensions.md: sessions 9-11 closed and resolution noted; sessions 12-14 tagged as deferred

---

## Phase 2 — Build-Plan Scaffolding

**Output:** a `build_plan/` directory that names what every future session works.

🤖 Claude Code handles all of Phase 2.

- [ ] `build_plan/MANIFEST.md` — orientation
- [ ] `build_plan/00_preamble.md` — orienting prose
- [ ] `build_plan/00_session_schedule.md` — canonical "what does each session work" reference, listing sessions by ID with scope, source documents, output target, budget tier
- [ ] `build_plan/P_0_contract_lock.md` — retroactively documenting Phase 1
- [ ] `build_plan/P_1_sql_schema.md` — Phase 3 chunk
- [ ] `build_plan/P_2_seed_authoring_infra.md` — Phase 4 chunk
- [ ] `build_plan/P_3_epistemology.md` ... `P_8_service_nodes.md` — Phase 5 chunks
- [ ] `build_plan/P_9_cross_domain.md`
- [ ] `build_plan/DEC_1_retrieval_architecture.md`
- [ ] `build_plan/P_10_self_correction.md`
- [ ] `build_plan/P_11_teaching_prototype.md`
- [ ] `build_plan/P_12_evaluation.md`
- [ ] `build_plan/P_13_ui_prototype.md`

The schedule is a planning estimate, not a contract; sessions split or bundle as evidence accumulates (per the InfoGenesis SA-046 retrospective).

**Once Phase 2 closes, this `IMPLEMENTATION_PLAN.md` file becomes a high-level reference. The `build_plan/` directory is the operational source.**

---

## Phase 3 — SQL Schema Implementation

**Output:** Postgres schema deployed to Supabase; migrations versioned.

🤖 Claude Code handles via Supabase MCP.

Translate [architecture.md](architecture.md) and [learner-model.md](learner-model.md) schemas into:

- [ ] `nodes` table — id, label, domain[], summary, teaching_notes, aliases[], rigor_score_computed, rigor_score_adjustment, **confidence_level** (`EXTRACTED|INTERPRETED|SYNTHETIC`, new from Phase 1.2), confidence (numeric), provenance, status, superseded_by, graph_version_added, timestamps
- [ ] `edges` table — source_id, target_id, type, weight, confidence, provenance, evidence, graph_version_added
- [ ] `learner_events` table — event-sourced log per [learner-model.md](learner-model.md)
- [ ] `mastery_snapshots` table — cached mastery state
- [ ] `tension_log` table — per [self-correction.md](self-correction.md)
- [ ] `settings` — graph_version counter

Stack: Supabase migrations (`supabase/migrations/`), tracked under CL discipline.

### Phase 3 Verification

- [ ] `supabase db push` applies the schema migrations cleanly to the dev DB
- [ ] `\d+ nodes` in psql shows the expected columns including `confidence_level`
- [ ] Migration rollback works

---

## Phase 4 — Seed Graph Authoring Infrastructure (Database-First)

**Output:** per-subdomain Supabase migration files + ROUTING.md manifest + `audit_graph.py` validator that queries the live DB.

**Important:** the 2026-04-09 seed graph session already settled "seeding happens directly in the database at build time, not via JSON" (per CONTEXT.md). The InfoGenesis chunked-JSON-LD authoring layer **does not transfer literally** — but the chunked-authoring **discipline** does. Paideia's choice: **chunks are SQL migration files**, organized per-subdomain in the Supabase migrations directory.

### 4.1 — Migration-as-Chunk Layout

```
supabase/
└── migrations/
    ├── 0001_schema_nodes_edges.sql              # Phase 3 — schema
    ├── 0002_schema_learner_events.sql           # Phase 3 — schema
    ├── 0003_schema_tension_log.sql              # Phase 3 — schema
    ├── 0010_seed_meta.sql                       # ontology metadata, graph_version=1
    ├── 0011_seed_epistemology_part1.sql         # P_3 session 1 output
    ├── 0012_seed_epistemology_part2.sql         # P_3 session 2 output (if split)
    ├── 0020_seed_ethics_part1.sql               # P_4 session 1
    ├── 0030_seed_metaphysics_part1.sql          # P_5
    ├── ...
    ├── 0050_seed_service_nodes.sql              # logic primitives, math, history
    └── 0060_seed_cross_domain_edges.sql         # Phase 5 final pass
```

Numeric prefix scheme: `00NN` schema, `001N` epistemology, `002N` ethics, `003N` metaphysics, etc. **Each session's output is one new migration file**, naturally giving per-session attribution and per-session diff review.

### 4.2 — ROUTING.md

- [ ] Create `supabase/migrations/ROUTING.md` — manifest mapping subdomain → migration file range, compound-domain rules (dual-domain concepts written into the higher-precedence subdomain's migration with `domain[]` carrying both tags), per-session narrative paragraphs (one per migration file, ~200-400 words documenting what that session added and why). This is the long-form audit trail that doubles InfoGenesis's per-shard narrative pattern.

### 4.3 — `audit_graph.py`

- [ ] Create `audit_graph.py` (~250 lines stdlib Python + `psycopg`) — connects to Supabase, queries the live database, runs validation. Replaces InfoGenesis's `publish_graph.py` entirely; no JSON stitch step exists.

**Hard-fail checks (exit 2):**
- duplicate node `id`
- dangling edge references (source_id or target_id not in nodes)
- cycles in prerequisite-edge subgraph (SCC detection via Kosaraju)

**Soft-warn checks (printed to stderr by category):**
- orphaned leaves (zero outbound + zero inbound prerequisite edges)
- missing `summary` or `teaching_notes`
- suspicious cross-domain edge ratio (e.g., epistemology subdomain with > 40% cross-domain inbound — likely indicates a missing service node)
- **undeclared predicate names** (edge.type not in the canonical predicate manifest — catches schema drift across sessions per InfoGenesis D159 lesson)
- **attribute-shape inconsistency** (nodes of same domain with materially different attribute coverage)
- missing rigor score components (rigor_score_computed null when topology data is sufficient)
- render-readiness violations (labels containing scaffolding tokens — "service_node", "synthetic", "stub")
- confidence_level=SYNTHETIC nodes flagged for review queue

**Modes:**
- `--validate-only` (default) — read-only DB queries, print per-category counts, exit 0/1/2
- `--export-snapshot path/to/snapshot.json` — write a current-state snapshot (for offline review or self-correction batch jobs)
- No write-back path — DB writes happen via migration files run through `supabase db push`. Audit is read-only.

### 4.4 — Predicate Manifest

- [ ] Create `supabase/migrations/PREDICATE_MANIFEST.md` — canonical list of allowed edge types (`prerequisite`, `enables`, `informed_by`, `cross_domain_dependency`, etc.). The audit script reads this and warns on any edge type not in the list. Adding a new predicate requires updating the manifest as part of the same session — a CL-tracked material change, surfaced in the SA decisions array.

### 4.5 — Per-Session Migration Workflow

1. Session reads target subdomain's SEP article structure, identifies in-scope concepts at the granularity principle
2. Session writes a new migration file `00NN_seed_<subdomain>_partN.sql` containing INSERT statements for new nodes and edges, with `graph_version_added` set to the current settings counter
3. Session runs `supabase db push` against the dev DB
4. Session runs `python audit_graph.py --validate-only` against the post-push DB
5. Hard-fails fix in-session; soft-warns recorded in SA exit_state per-category counts
6. Session closes, commits the migration file (CL entry tracked)

### 4.6 — Update OPERATIONS.md Audit Step

- [ ] Update OPERATIONS.md audit-pass step to invoke `python audit_graph.py --validate-only` at session close. The validation is end-to-end: chunks (migrations) → DB → audit, not chunks → audit.

### Phase 4 Verification

- [ ] `audit_graph.py --validate-only` runs end-to-end against the live DB in <3s on a 100-node test seed
- [ ] New predicate not in PREDICATE_MANIFEST.md surfaces as a soft warn
- [ ] Deliberately-broken edge ref triggers hard-fail with exit 2

---

## Phase 5 — Seed Graph Build (Parallelizable)

**Output:** concept-level seed graph across philosophy subdomains. Hundreds of nodes per subdomain. Cross-domain edges first-class.

Per the chunked-authoring + eager-slot-claim discipline, multiple subdomain sessions can run concurrently without merge conflicts.

- [ ] **P_3 Epistemology** — start here; the deprecated `philosophy-graph-seed-v0.2.json` was epistemology-focused, so judgment is calibrated.
- [ ] **P_4 Ethics**
- [ ] **P_5 Metaphysics**
- [ ] **P_6 Philosophy of Mind**
- [ ] **P_7 Philosophy of Language**
- [ ] **P_8 Philosophy of Science**
- [ ] **P_8.5 Service Nodes** — logic primitives, mathematical prerequisites, history nodes that terminate where they stop affecting comprehension. This is where InfoGenesis's "prerequisite chains terminate when further depth stops affecting comprehension" rule operationalizes.
- [ ] **P_9 Cross-domain edges pass** — after subdomain interiors are stable, generate edges spanning subdomain boundaries (metaphysics → philosophy of mind, ethics → political philosophy, philosophy of science → epistemology, etc.).

**Source approach:** SEP as structural reference (concept inventory, cross-references), not as content corpus. Wikipedia for accessible summaries (CC BY-SA). Generate first-pass prerequisite edges via Claude; mark `confidence_level: INTERPRETED` until validated.

**Per-session workflow:** session reads the relevant SEP article structure, identifies concepts in scope at the granularity principle (one mastery state per concept; if mastery doesn't transfer, split the node), writes a new migration file with INSERT statements for nodes + edges and explicit `confidence_level`, applies via `supabase db push`, validates against `audit_graph.py --validate-only` (which queries the live DB), fixes defects in-session by editing the migration before commit, closes SA entry naming concepts touched and recording soft-warn counts in exit_state.

### Phase 5 Verification

- [ ] At the end of each subdomain session, `audit_graph.py --validate-only` against the post-`db push` DB runs zero hard-fails
- [ ] Soft-warn count is recorded per-category in the SA exit_state
- [ ] Migration files are atomically attributable to the SA entry that wrote them via the SA's `change_log_refs` array
- [ ] Cross-session schema drift is detected by the predicate-manifest audit

---

## Phase DEC.1 — Retrieval / Mastery-Inference Architecture Decision

**Output:** settled architecture decision recorded in CONTEXT.md and a build-plan chunk.

Per InfoGenesis's S2.5 pattern: architecture decisions get their own session at the point in the build where post-substrate evidence makes the choice meaningful. After Phase 5 the seed graph is mature enough to test retrieval shapes.

Decisions to settle:
- [ ] Mastery computation: server-side (per current architecture) — confirm or revisit
- [ ] Two-hop neighborhood retrieval shape for teaching session context (per [self-correction.md](self-correction.md))
- [ ] Embedding strategy for entity resolution — pgvector + which embedding model
- [ ] Whether to maintain a chunk-resolver index (InfoGenesis pattern) for SEP onward-reading lookup, or rely on direct SEP URL pointers

---

## Phase 6 — Self-Correction Pipeline

**Output:** tension log + Opus batch review pipeline operational.

Implements [self-correction.md](self-correction.md):

- [ ] Tension log schema in Postgres (Phase 3)
- [ ] Sonnet teaching-side: emit tension records (`struggle_unresolved`, `unexpected_ease`, `spontaneous_connection`, `source_ineffective`, `mastery_contradiction`)
- [ ] Opus reviewer: scheduled batch job reads tension log, proposes graph edits via confidence-weighted pipeline, writes provisional decisions
- [ ] Stability constraint: between review cycles the graph is read-only at the structural level

---

## Phase 7 — Sonnet Teaching Layer (First Prototype)

**Output:** a callable teaching endpoint that produces learner-facing prose against the rendering policy.

- [ ] Sonnet system prompt = `AGENT_INSTRUCTIONS.md` (Phase 1.3) verbatim
- [ ] Input: current concept node + prerequisite nodes (one-hop) + two-hop neighborhood for entity resolution
- [ ] Output: teaching turn in product voice, no scaffolding tokens
- [ ] DeepTutor fork as infrastructure base (per [infrastructure.md](infrastructure.md)); pedagogical layer is the new Sonnet integration
- [ ] First test: the worked example from `AGENT_INSTRUCTIONS.md` — does the live system produce the pass-case voice or fall back to graph-voice?

### Phase 7 Verification

- [ ] Sonnet teaching prototype, given the AGENT_INSTRUCTIONS.md worked-example input, produces the pass-case voice
- [ ] Spot-check: feed it 10 random concept queries, manually grade for forbidden-token leakage. **Zero leakage is the bar.**

---

## Phase 8 — Evaluation Harness

**Output:** ordinal external-baseline evaluation, not closed-loop self-validation.

The InfoGenesis SA-025 lesson: validation against your own authored criteria is weak signal; validation against an external baseline produces ordinal signal robust to designer drift. Paideia's analogue: evaluation should be teaching quality measured by:
- (a) external rubric (community college instructor blind review)
- (b) head-to-head against a baseline (DeepTutor unmodified, or a stock Sonnet without the rendering policy)

**Not** against an in-house question battery the graph was authored to traverse.

👤 **Start enrolling in Apple Developer Program here** (2-4 week lead time per business.md).

---

## Phase 9 — UI Prototype

**Output:** globe + syllabus surface, native iOS/Android primary, web test surface.

Per [ui-architecture.md](ui-architecture.md). Application code; **CL discipline does not apply** (per the scoping decision in Phase 0.2). Normal git history.

👤 **Subscribe to Apple Developer Program and Google Play Console** if not already done in Phase 8.

---

## Decisions Settled During Planning

These get recorded as D1+ in SA-001's `decisions` array.

1. **SA entry format: markdown with YAML frontmatter.** CL entries: pure JSON. Optimized for AI generation reliability on dense prose fields.
2. **Three-level node confidence: adopt** (`EXTRACTED | INTERPRETED | SYNTHETIC` as a new `confidence_level` column on nodes, orthogonal to existing numeric `confidence` and categorical `provenance`).
3. **Chunks are SQL migration files** (one per session), not a JSON intermediate. Matches the prior 2026-04-09 settled decision that seeding happens directly in the database. `audit_graph.py` validates against the live DB via `psycopg`. The InfoGenesis chunked-authoring **discipline** transfers; the JSON format does not.
4. **CL discipline scope: state-of-record only.** Design docs, schemas, seed graph migration files, build_plan, OPERATIONS.md. Application code (React/API/web app, DeepTutor fork integration) git-only.
5. **`_archive/` retained for design-doc retirements** (current usage). **Not used for build-cycle pre-edit snapshots** (git covers it).
6. **Closed prompt-pack sessions (1-8) not retroactively re-authored as SA entries.** Referenced in SA-001's entry_state by date.
7. **`PROJECT_SETUP.md` deleted.** Build moves entirely to Claude Code; the "paste-into-Claude-project" file has no job. Orientation lives in `CLAUDE.md` only.
8. **GitHub private repo on personal account** (`shanekidd/paideia` or similar). business.md already settled this as the right starting position; transfer paths exist for every service except Apple Developer when a commercial entity forms.
9. **Required Pre-Phase 0 platform stack: Anthropic API, GitHub, Supabase.** Vercel/DeepTutor/Apple/Google/Amazon Associates deferred until their phase.
10. **Supabase MCP is the connective tissue between Claude Code and the database.** Direct DB read/write from build sessions; no intermediate ORM layer for seed authoring.

---

## Gap Analysis: InfoGenesis Patterns vs. Paideia Current State

| InfoGenesis Pattern | Paideia Status | Action |
|---|---|---|
| SA entries + CL entries + counter registers | None | **Build in Phase 0** |
| Nine-step Start Engine startup procedure | None | **Build in Phase 0 (OPERATIONS.md)** |
| Eager slot claim with `status: in_progress` stub | None | **Build in Phase 0** |
| Auto-mode + narrow interrupt criteria | None | **Codify in Phase 0 (OPERATIONS.md)** |
| Budget tiers (60/70 extraction, 70/80 mechanical) | None | **Adopt in Phase 0** |
| End-state-quality first-pass principle | Implicit | **Codify in Phase 0** |
| `project_state.md` carry-forward layer | **CONTEXT.md** ✓ | Keep |
| Open-questions layer | **tensions.md** ✓ | Keep |
| **Provisional-decisions layer** | **Missing** | **Create in Phase 0** |
| Watch-flag layer | Implicit in tensions.md | Defer (probably overkill at Paideia scale) |
| Global decision IDs (D-NN) | None | **Add in Phase 0** |
| `OPERATIONS.md` procedural depth | None | **Create in Phase 0** |
| `CLAUDE.md` orientation entry point | **PROJECT_SETUP.md** (partial) | **Replace in Phase 0; delete PROJECT_SETUP.md** |
| Build plan as chunked manifest + session schedule | None | **Create in Phase 2** |
| Chunked authoring with routing manifest | None | **Create in Phase 4 — chunks ARE SQL migration files (not JSON), per-subdomain, with ROUTING.md narrative manifest** |
| Stdlib Python validation script with `--validate-only` | None | **Create in Phase 4 (`audit_graph.py`) — queries live Supabase DB** |
| **Standalone rendering policy (`AGENT_INSTRUCTIONS.md`)** | Implicit in pedagogy.md | **Extract in Phase 1** |
| Three-level node confidence (`EXTRACTED \| INTERPRETED \| SYNTHETIC`) | Edges only; node-level silent | **Add to schema in Phase 1** |
| Multi-target shared-pointer pattern (provenance) | Not yet — relevant when SEP comes in | Address in Phase 4 |
| Construction-commentary filter in node prose | Not applicable yet | Address in Phase 1 (in rendering policy) |
| Retirement-with-notes pattern | Already practiced (`_archive/`) ✓ | Keep |
| Phase 0 contract lock | None | **Make it Phase 1 of this plan** |
| Schema-drift audit categories | None | **Build into `audit_graph.py` from session zero** |
| `_archive/` pre-edit snapshots | N/A | **Skip** (git covers it) |
| JSON-LD storage | N/A — Paideia is SQL | Skip |
| OWL/RDF semantics | N/A — settled rejection | Skip |
| 96-PDF source corpus extraction | N/A — SEP is structural reference | Adapt (see Phase 5) |
| Sample-question battery as organizing principle | Risk to avoid | **Anti-pattern; do not adopt** |
| CL on application code | N/A | **Scope CL to state-of-record only** |

---

## Critical Files to Create / Modify / Delete

**Pre-Phase 0 (new):**
- `.gitignore`
- `.env.example` (template; real `.env` gitignored)
- `.claude/settings.local.json` — MCP server registrations (Supabase at minimum)

**Phase 0 (new + delete):**
- [CLAUDE.md](CLAUDE.md) — orientation entry for AI sessions (new)
- [OPERATIONS.md](OPERATIONS.md) — procedural depth, ~400 lines (new)
- [provisional-decisions.md](provisional-decisions.md) — empty header (new)
- `session_audit/register_state.json` (new)
- `session_audit/entries/SA-001_adopt_session_protocol.md` (new)
- `change_log/register_state.json` (new)
- **Delete [PROJECT_SETUP.md](PROJECT_SETUP.md)** — superseded by CLAUDE.md

**Phase 1 (new + modify):**
- [AGENT_INSTRUCTIONS.md](AGENT_INSTRUCTIONS.md) — rendering policy (new)
- [architecture.md](architecture.md) — add `confidence_level` field to node schema
- [CONTEXT.md](CONTEXT.md) — add "13. Three-level node confidence" carry-forward; reference AGENT_INSTRUCTIONS.md, OPERATIONS.md, CLAUDE.md, provisional-decisions.md in file index; remove PROJECT_SETUP.md row
- [tensions.md](tensions.md) — close session 9-11 tensions; tag 12-14 as deferred

**Phase 2 (new):**
- `build_plan/MANIFEST.md`, `00_preamble.md`, `00_session_schedule.md`, per-phase chunks

**Phase 3 (new):**
- `supabase/migrations/0001_schema_nodes_edges.sql` and successors
- `supabase/config.toml`

**Phase 4 (new):**
- `supabase/migrations/ROUTING.md` — per-session narrative manifest
- `supabase/migrations/PREDICATE_MANIFEST.md` — canonical edge types
- `audit_graph.py` — stdlib + psycopg validator (queries live DB)
- `supabase/migrations/0010_seed_meta.sql` — graph metadata

**Reused (existing, no changes needed):**
- [pedagogy.md](pedagogy.md) — keep as design rationale; AGENT_INSTRUCTIONS.md cites it
- [learner-model.md](learner-model.md), [self-correction.md](self-correction.md), [reading-system.md](reading-system.md), [infrastructure.md](infrastructure.md), [ui-architecture.md](ui-architecture.md), [content-strategy.md](content-strategy.md), [business.md](business.md), [expansion.md](expansion.md), [design-reasoning.md](design-reasoning.md), [session-lifecycle.md](session-lifecycle.md)
- `_archive/` — keep retirement-with-notes pattern

---

## Session Pickup Protocol (Until Phase 0 Closes)

For each new Claude Code session before Phase 0 has closed:

1. **Read this file's [Status](#status) section first.** Understand the current phase and next action.
2. **Read [CONTEXT.md](CONTEXT.md).** Carry-forward decisions.
3. **Read the current phase's section in this file.** Understand what's been checked off and what's next.
4. **Execute the next steps.** Mark checkboxes complete as you go.
5. **At session close, update the Status section** with date, what was completed, what's next, and any blockers.

**After Phase 0 closes** (CLAUDE.md and OPERATIONS.md are written, SA-001 exists), this protocol is replaced by the `Start Engine` trigger and SA/CL discipline. From that point, sessions read the most recent SA entry instead of this file.

---

*This file is the transitional build plan. Source: [infogenesis_report_for_paideia.md](infogenesis_report_for_paideia.md). Last updated: 2026-04-28.*
