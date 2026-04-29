# InfoGenesis Architecture Report — Patterns for Paideia

**Source project:** `C:\Users\kidds\projects\infogenesis_graph` (read directly via MCP filesystem on 2026-04-28)

**State at read time:** 64 closed sessions, 473 change-log entries, 2,531-node graph, 1,138 PointerBindings across 33 provenance shards, 31 source documents extracted from a 96-document corpus.

**Built:** ~30 hours of autonomous Claude Code sessions per the user.

**Purpose of this report:** capture every load-bearing pattern from InfoGenesis that may apply to Paideia, in enough detail that a fresh Paideia session can reason about adaptation without re-exploring the InfoGenesis project. Includes patterns that may not be immediately useful but provide context for understanding the load-bearing ones. The report is descriptive, not prescriptive — what to do with this information is the user's call.

---

## 0. Why this report exists

The user (Shane) has built two Claude-collaborative projects: **InfoGenesis** (an Agilysys-internal POS documentation knowledge graph, 64 sessions in, near complete) and **Paideia** (an AI-guided liberal-education app built on a pedagogical dependency graph, currently in foundational design with a single epistemology seed graph). InfoGenesis solved the autonomous-multi-session-build problem at scale; Paideia is about to enter the same build phase. Shane wants Paideia to inherit the session-protocol infrastructure that made InfoGenesis tractable for autonomous Claude Code iteration, adapted to Paideia's domain.

The previous session in this conversation initially dismissed the SA/CL audit discipline as overkill for Paideia's phase. That was wrong. The user clarified that without the SA/CL discipline, every session needs human intervention to brief Claude on state, and the InfoGenesis 30-hours-to-2,531-nodes evidence is the right benchmark for what becomes possible when that bottleneck is eliminated. This report is the post-correction handoff to a fresh Claude Code session in Paideia.

The fresh session will not have the conversation history that produced this report. The fresh session has access to the Paideia project files (`CONTEXT.md` and downstream files) and to its own MCP access if the InfoGenesis directory is mounted. This report stands on its own as reference material — the fresh session does not need to re-read InfoGenesis to reason about adaptation, though it can if a specific detail needs verification.

---

## 1. What InfoGenesis is, mechanically

A typed JSON-LD entity graph over Agilysys POS product documentation, consumed by Microsoft Copilot Studio for installer and project-manager Q&A. The graph encodes typed entities (Application Profile, Pod, Server roles, Package, Module Type, Endpoint, Integration, etc.), typed relationships (object properties), and constrained attributes (datatype properties). Each node carries provenance: a confidence label (`EXTRACTED | INTERPRETED | SYNTHETIC`) and one or more pointers to source-document section anchors.

The published artifact is a single JSON file (`infogenesis_prototype.json`, ~2.3MB at SA-064) with all 2,531 nodes, regenerated from chunked source via a stdlib-only Python build script. The chunked source is the state-of-record; the root artifact is a build output and is never edited directly.

The project domain (POS product documentation) is unrelated to Paideia's domain (philosophy and liberal-education concepts). The session-protocol patterns, the chunked-authoring patterns, the rendering-policy pattern, and the decision-tracking patterns are domain-agnostic and transfer. The JSON-LD format itself, the OWL/RDF semantics, and the specific node taxonomy do not transfer.

---

## 2. The session-protocol layer — the core transferable architecture

### 2.1 Why this exists

InfoGenesis runs ~64 closed sessions plus an active sweep of in-flight ones, often in parallel under scheduled tasks. The session-protocol layer is the infrastructure that makes a Claude Code session resumable from a cold start with no human in the loop: the next session reads one file (`session_audit/entries/SA-NNN_<slug>.json` with the highest counter) and knows where the previous session stopped, what state the project is in, and what to work on next. Every other piece of InfoGenesis's discipline serves this resumability goal.

This is the load-bearing reason to copy the discipline. Without it, Paideia sessions would each need a human-authored briefing, and the 30-hours-to-2,531-nodes throughput would be unreachable.

### 2.2 The two registers

Two counter files at `session_audit/register_state.json` and `change_log/register_state.json`, each a tiny JSON object. The session_audit register at SA-064 close looks like:

```json
{
  "description": "Session audit counter state. Single source for next available SA entry number.",
  "next_id": "066",
  "format": "SA-NNN_<slug>.json — 3-digit zero-padded counter plus a 3-7 word snake_case retrieval-optimized slug naming the session's primary work (≤60 chars after the SA-NNN_ prefix). Cross-references between entries use bare counter IDs.",
  "last_written": "SA-064"
}
```

The `next_id` field is authoritative for next-slot assignment. The `last_written` field is a cross-check. The `description` and `format` fields exist so any new session reading the register understands the convention without consulting external docs. The `next_id` is `066` because SA-065 is in flight at read time (it has been claimed but not closed).

### 2.3 The session-audit (SA) entry — full schema

Every session writes one SA entry at `session_audit/entries/SA-NNN_<slug>.json`. The SA-064 example I read is ~12KB of JSON. The schema is documented in `OPERATIONS.md`:

```json
{
  "schema_version": "1.0",
  "session_id": "SA-NNN",
  "started_at": "ISO-8601 datetime or date",
  "closed_at": "ISO-8601 datetime or date — null while status is in_progress",
  "status": "in_progress | closed",
  "participants": {
    "user": "name",
    "agent": { "product": "Claude Code", "model": "claude-opus-4-7" }
  },
  "session_type": "build_plan_step | ad_hoc | infrastructure | investigation | meta",
  "execution_environment": "mcp | claude_code",
  "stage": "S0 | S1 | S2 | ... or phase letter",
  "steps_worked": ["A.1", "A.2"],
  "entry_state": "one-paragraph description of state at session start",
  "exit_state": "one-paragraph description of state at session close",
  "objectives": ["what this session set out to do"],
  "outcomes": ["what the session actually produced"],
  "decisions": [
    {
      "id": "D179",
      "decision": "short statement",
      "rationale": "why — including evidence cited",
      "alternatives_considered": ["option A", "option B"],
      "closes_open_question": "OQ-N or null",
      "status": "committed | provisional"
    }
  ],
  "open_questions": [
    {
      "id": "OQ-PG-1",
      "question": "the question",
      "context": "why it matters",
      "blocking": false,
      "proposed_next_step": "where to address it"
    }
  ],
  "artifacts_created": ["relative/path/to/file"],
  "artifacts_modified": ["relative/path/to/file"],
  "change_log_refs": ["CL-464", "CL-465"],
  "next_session": {
    "recommended_step": "explicit description of what to work next",
    "blocked_by": null,
    "notes": "anything next session needs beyond the step description"
  },
  "notes": "additional context"
}
```

Several non-obvious fields worth flagging:

**`entry_state` and `exit_state` are dense paragraphs**, not field collections. They typically include: master HEAD commit hash, worktree branch name, counter values at session boundaries, node counts, warning counts, and the specific phase/step being worked. The SA-064 entry's exit_state is ~700 words. This density matters: the next session reads exit_state to understand where it's starting from without needing to compute anything. Verbosity here pays back ten-fold across the next session's startup.

**`decisions` carry IDs (D-NN) that are global across the project**, not local to the session. SA-064's decisions are D179, D180, D181 — the next session's first decision will be D182. Decision IDs are referenced from later SA entries by bare ID, so when SA-070 says "per the D102 audit-rule precedent," the reference is stable across rephrasing or slug revision. InfoGenesis is at D181 after 64 sessions — average ~3 decisions per session, but distribution is skewed: contract-lock sessions accumulate many, mechanical-extraction sessions accumulate few.

**`closes_open_question`** lets a decision explicitly close a previously-recorded open question. The OQ identifiers are also global (OQ-A through OQ-PG-1 at SA-064; some carry namespacing like OQ-PG-1 to indicate the phase that surfaced them).

**`alternatives_considered`** is required even for what feel like obvious decisions. This forces the session to surface why option A beat option B, which is what makes the decision auditable later. The SA-064 D179 decision has two rejected alternatives explicitly recorded.

**`status: provisional`** vs `committed` on a decision is the seed of the layered decision-tracking system described in Section 6. A provisional decision is closed-but-revisitable; a committed decision is settled.

### 2.4 The change-log (CL) entry — full schema

Every material file change gets a CL entry at `change_log/entries/CL-NNN_<slug>.json`. The slug pattern is `<op>_<artifact>[_<scope>]` where op is `create | modify | rename | move | delete | archive`. This naming lets `grep build_plan change_log/entries/` return every change to build-plan content across all sessions.

```json
{
  "schema_version": "1.0",
  "change_id": "CL-468",
  "recorded_at": "2026-04-28",
  "session_id": "SA-064",
  "summary": "one-line description of what changed",
  "type": "create | modify | rename | move | delete",
  "files": [
    {
      "path": "relative/path/to/file",
      "op": "create",
      "prior_path": null,
      "purpose": "what this file is for or why it changed"
    }
  ],
  "rationale": "why the change was made; link back to the session's objective"
}
```

CL entries are atomic and machine-pattern-matchable; SA entries are session-narrative. The two-register split is intentional. SA-064 produced 10 CL entries (CL-464 through CL-473), one per material file change. Sessions typically produce 5-15 CL entries; 64 sessions have produced 473 CL entries.

### 2.5 The full nine-step Start Engine session-startup procedure

This is the load-bearing autonomous-iteration mechanism. Documented in `OPERATIONS.md`:

**Step 1 — Triage by trigger phrase.** "Start Engine" (case-insensitive) on the user's first turn = build-plan-step session, runs the full procedure. Absent = default-path session, light procedure (read just enough state to be useful, engage with the request as stated, write an SA entry at close with `steps_worked: []`).

**Step 2 — Don't re-read CLAUDE.md or OPERATIONS.md.** They're already in context (auto-loaded by harness or accumulated). Re-reading wastes context budget.

**Step 3 — Verify worktree-master parity.** Sessions run in worktrees on `claude/<slug>` branches. Compare `git rev-parse HEAD` against `git -C <main-repo-path> rev-parse master`; if they differ, run `git merge --ff-only master` from the worktree. Halt on uncommitted changes that prevent fast-forward. The reference incident: SA-035 / SA-036 collision when a worktree branched at master-pre-3ca726f and missed a parallel session's fast-forward, resulting in the worktree reading stale state.

**Step 4 — Sweep stale worktrees.** Enumerate `git worktree list`, and for each non-current worktree where (a) branch HEAD is a strict ancestor of master, (b) status is clean, (c) branch follows `claude/<slug>` pattern: remove via `git worktree remove` followed by `git branch -d`. Run as separate commands, not chained with `&&`, because Windows often returns non-zero "Permission denied" on the worktree remove while still successfully unregistering it. The empty residual directory under `.claude/worktrees/` is held by an OS-level handle (Claude Code parent harness, Windows Search indexer, antivirus scanner) and cannot be removed by `rmdir`; the directory is benign cosmetic residue at that point and clears on reboot.

**Step 5 — Read `project_state.md`.** Carry-forward decisions and current scope. Paideia equivalent: `CONTEXT.md`.

**Step 6 — List `build_plan/` and read `build_plan/MANIFEST.md`.** Locate which step is next. Read just the chunk for the active step, not the whole directory.

**Step 7 — Read the most recent SA entry.** Highest-NNN file in `session_audit/entries/`. Sort by the leading three-digit counter and ignore the slug for ordering. Its `next_session.recommended_step` field names what this session works.

**Step 8 — Discover current filesystem state.** Compare the project root against the prior SA's `exit_state` claim. If anything differs, surface to the user before proceeding. This catches the case where a user made out-of-session changes between sessions.

**Step 9 — Read step-specific artifacts.** What the build-plan step depends on (chunk files, source PDFs, etc.).

**Step 10 — Confirm the step before starting.** State the step, objective, artifacts, expected decisions. Under auto-mode, announce-and-proceed without waiting; under non-auto-mode, pause for confirmation.

**Step 11 — Claim the SA slot eagerly.** This is the critical step that makes parallel sessions safe. Bump `session_audit/register_state.json next_id` to NNN+1 and `last_written` to SA-NNN. Write a stub SA entry at `SA-NNN_<topic_slug>.json` with `status: "in_progress"` plus minimal frontmatter (start time, participants, planned work, entry_state). Commit with message `SA-NNN: claim slot for <topic>` and fast-forward master. The claim-commit propagates the bumped counter through master so any parallel session starting after this point sees `next_id: NNN+1` and claims a different slot. If the most recent SA entry on master has `status: "in_progress"`, another session is already holding that slot — wait or surface to user.

The `in_progress` stub plus eager-claim is the mechanism that prevents the SA-035/SA-036-style collision Shane hit when running parallel sessions. Before SA-036 D113, sessions claimed slots lazily at close; two sessions starting concurrently both saw `next_id: 035`, both started work, and one had to renumber and rebase. After the eager-claim discipline landed, the collision became impossible by construction.

### 2.6 The session-shutdown procedure

Before session ends:

**Step 1 — Run the audit pass.** `python publish_graph.py --src graph_chunks/prototype --validate-only` (and analogously for any other validated artifact). Hard-fails on duplicate `@id`. Soft-warns on undeclared types, undeclared predicates, missing attestations, isolated nodes, function-layer-primitive coverage gaps, OWL/RDF completeness gaps, and render-readiness violations. The validate-only summary prints per-category counts so signal is readable at a glance.

**Step 2 — Spot-check what changed.** For each entity created or modified this session: is it attested by a pointer to the right source-document section, is the confidence honest, does the type match the framing the source uses, does the entity satisfy the end-state contract. The audit catches structural mistakes; the spot-check catches judgment mistakes.

**Step 3 — Watch for sample-question battery tailoring.** A heuristic, not a mechanical check. Symptoms: extraction or scope decisions justified by battery coverage rather than corpus coverage. The battery is illustrative of question shapes, not a definition of completeness. InfoGenesis names this anti-pattern explicitly because they hit it through the first 24 sessions — a rationale phrase like "extraction-exempt against the sample-question battery" or "load-bearing for sample question N" used as completeness justification is the symptom.

**Step 4 — Fix findings inline when small.** Vocabulary cleanup, missing pointer attachment, type touchups. Carry-forward only for findings that would derail the session's primary aim or require user judgment. **Authoring rules that codify deferral is an anti-pattern:** every such rule generates downstream sessions whose only purpose is to clean up the session that wrote them. Explicitly named in OPERATIONS.md.

**Step 5 — Rewrite the SA stub in place.** Replace `status: "in_progress"` with `status: "closed"` plus `closed_at`, `exit_state`, `outcomes`, `decisions`, `open_questions`, `artifacts_*`, `change_log_refs`, `next_session`, `notes`. Preserve the start-time fields the stub already wrote. If the topic shifted during the session, `git mv` to a revised slug at close.

**Step 6 — Write CL entries** for each material file change.

**Step 7 — Update `change_log/register_state.json`.** The session_audit register was already bumped at slot-claim.

**Step 8 — State the next session's step explicitly.** The `next_session.recommended_step` field and the final response to the user should agree.

**Step 9 — Commit and master-fast-forward.** Stage the working-tree state, commit with a message naming the SA ID and short summary, then fast-forward master from the worktree branch using `git -C <main-repo-path> merge --ff-only claude/<slug>`. The `git push . HEAD:master` shape fails with `denyCurrentBranch`; the merge command is the reliable form. Confirm the main repo's working tree is clean before fast-forwarding. Established at SA-026 after SA-025's close-out left master at the prior session's HEAD and the next session couldn't see SA-025's writes.

### 2.7 The archival rule (and why Paideia probably skips it)

Before a session makes its first material modification to a covered artifact, the pre-edit state is snapshotted to `_archive/<artifact>_SA-NNN.<ext>`, where SA-NNN is the session that **last wrote** the state being archived (read from the most recent prior SA entry that names the file in `artifacts_created` or `artifacts_modified`). One snapshot per covered artifact per session, taken at first modification, capturing the file's session-open state byte-for-byte. For chunked-authoring directories, archival is per-chunk.

The rule is a build-cycle defense for fast in-session rollback without invoking git tooling. Once git history is established (InfoGenesis git-init was at SA-023, after the rule already existed), the same recovery surface is available via `git checkout`. The archival rule was retained through the build cycle for procedural continuity; HANDOFF.md flags it as a candidate for retirement at handoff.

**For Paideia specifically:** the archival rule is probably overhead from session zero, since Paideia starts with git from the beginning. The recovery surface git provides is sufficient. **Skip the `_archive/` discipline.** This is one place not to copy.

### 2.8 Material-change criteria

Write a CL entry for: creating a new artifact file (any covered artifact); modifying an artifact in a way that affects a reader's understanding (adding rows to a register, updating ontology classes, revising a chunk); renaming or moving an artifact; deleting an artifact.

Don't write CL entries for: iterative saves within a session (only the final state matters); trivial formatting fixes that don't change meaning; tool-generated scratch files that aren't committed.

### 2.9 What the SA/CL discipline does NOT cover

InfoGenesis runs CL entries on `publish_graph.py` script changes. For Paideia, the application code itself is going to be substantial (Vercel + Supabase + Anthropic API stack); CL-tracking every code change would be busywork without retrieval value. **Recommendation: scope the CL discipline to the project-state-of-record (design docs, graph schemas, seed graph chunks, build_plan, etc.) and let normal git history serve as the system of record for application code.** This is a tighter scope than InfoGenesis runs.

### 2.10 SA entries: JSON or markdown?

InfoGenesis runs structured-JSON SA entries because their build artifact is JSON-LD and their tooling already handles JSON. Paideia's design docs are markdown, the schema is SQL, and there's no parallel reason to make SA entries JSON specifically. Two options:

**Option A — Keep SA entries as JSON.** Pro: schema validation is trivial, machine-readability is direct, the pattern is exactly what InfoGenesis runs and is proven. Con: dense paragraphs (entry_state, exit_state, decision rationale) embedded in JSON strings are awkward to read directly without a JSON viewer; large strings with internal newlines get escaped.

**Option B — SA entries as markdown with YAML frontmatter.** Frontmatter carries the structured fields (session_id, started_at, status, decisions list, next_session block); the body holds the prose narrative (entry_state, exit_state, outcomes). Pro: human-readable in any text editor, prose stays prose, frontmatter remains machine-parseable. Con: two formats to handle, slightly more parsing logic, slightly less proven than InfoGenesis's pure-JSON shape.

CL entries are short, atomic, and machine-pattern-matchable; they should stay JSON regardless of which option SA entries take. The user's call.

---

## 3. The build_plan layer

### 3.1 The structure

`build_plan/` is a directory of small, slug-named markdown chunks. There's a `MANIFEST.md` that orients a reader, a `00_session_schedule.md` that's the canonical "what does each session work" reference, a `00_preamble.md` for orienting prose, and per-stage / per-substage / per-phase chunks.

InfoGenesis went through a structural refactor at SA-028. The original build plan was structured by document-class groupings (pilot stack, IGCM admin guides, using-guides, release notes, reports guides, version-gap reconciliation). After 22 sessions, Shane realized this had inverted the actual product topology — they'd extracted Kiosk depth on top of a deployment substrate without the core POS behavior the Kiosk add-on assumes, producing a 486-node prototype that could describe Kiosk-specific behavior in detail while being silent on POS concepts those behaviors reference. The fix was a phased restructure ordering extraction by product-topology dependency:

- **Phase 0:** end-state contract lock (one-time gating before any extraction)
- **Phase A:** deployment substrate (Installation Guide, Server Deployment, Port Usage)
- **Phase B:** core POS behavior (Using IG POS, IGCM POS Terminal, LA UG, Upgrade Guide)
- **Phase C:** operational and reference (Offline Capabilities, DB Replication, POS API, Reports)
- **Phase D:** payment and peripheral substrate (12UX with Agilysys Pay, Peripherals Reference, payment-device docs)
- **S2.5:** retrieval architecture decision (pipeline shape selection)
- **S2.6:** chunk-resolver build (turn pointer text into retrievable prose)
- **Phase E:** add-on products (Kiosk closeout, Fly, OnDemand, KDS, DMB + PanOptic)
- **Phase F:** integration layer (PMS, casino, loyalty, others, Event Notifications)
- **Phases G/H/I bundled:** country/customer context, hardware peripheral catalog, customization
- **S5:** pipeline implementation
- **S5.5:** baseline-vs-treatment evaluation
- **S6:** consolidation and delivery

Chunks are named `P_<letter>_<slug>.md` for phases, `S<N>_<substage>_<slug>.md` for substages, `S<N>_<slug>.md` for standalone stages without substages. Retired sections are marked RETIRED in the manifest with notes about which phase they folded into. The retirement-with-notes pattern matters: the chunks aren't deleted, they're left in place with retirement notes pointing at the new structure, which preserves traceability without breaking historical SA references.

### 3.2 The session schedule

`build_plan/00_session_schedule.md` is the canonical reference for what each session works. It lists sessions by ID (Session A.1, B.1, B.2, ..., DEC.1, etc.) with their scope, source documents to read, output target, and budget tier. The most recent SA entry's `next_session.recommended_step` field names the next session by ID, and the new session reads the schedule plus the corresponding phase chunk.

The schedule is updated as sessions split (run long and divide their scope) or merge (small sessions bundle). It's not a contract; it's a planning estimate that gets refined.

### 3.3 Budget tiers

Two tiers, expressed as percent of the 1M-token Claude Code context window:

- **Substantive extraction or modeling:** 60% target, 70% hard cap
- **Mechanical or procedural work:** 70% target, 80% cap

The rationale: long-context recall and instruction-following degrade non-linearly as context fills; the cliff for nuanced judgment work sits well before the published needle-in-haystack ceiling. The tiers anchor against this. Sessions hitting cap close cleanly at a sensible boundary; the next session continues. Splits are normal expected behavior, not procedural defects. **Session count is not a quality metric; running an additional session to preserve quality is always preferable to compressing two sessions of work into one and degrading judgment.**

### 3.4 Bundling rule

A session may bundle adjacent decisions sharing context, or pair a substantive step with a mechanical follow-on. A session never bundles two substantive extraction steps. The session schedule encodes this — GHI.1 bundles country/customer-context (Phase G) with customization (Phase I) because both are small-content; B.6 bundles LA UG with Upgrade Guide because both are smaller substrate docs.

The rule was tightened at SA-046-era retrospective when empirical observation showed Phase A and Phase B sessions consistently closed under 30% utilization, and the Phase B.5 follow-up sequence (SA-041 / SA-042 / SA-044 / SA-045) extracted the same Items chapter and adjacent sub-records across four sessions when two would have sufficed. The original no-bundling rule was a defensible posture under the older Cowork-with-MCP environment with its truncation and timeout failure modes; under Claude Code with a 1M-token context window and native file tools, the rule was over-conservative. The lesson: rules that were calibrated for older environments need re-checking once the environment changes.

### 3.5 The end-state-quality first-pass principle

Established at SA-028 in response to a user correction: extraction is end-state quality first-pass, not baseline + later optimization passes. Every entity created or modified in any session emerges complete against the locked end-state contract — full attribute set, declared @type, render-ready label, at least one provenance pointer, honest confidence label, predicates declared with domain/range, render-readiness against the rendering policy. Entities that fail are extraction defects, fixed in the same session, not deferred work.

This is a load-bearing principle for autonomous iteration. Without it, you accumulate a downstream rework cycle that compounds across 30+ sessions into substantial re-touch work. Shane named this as out-of-budget for the build cycle.

### 3.6 Auto-mode and interrupt criteria

The default operating mode for "Start Engine" sessions, committed at SA-028. The startup procedure executes through the announce-step without pausing. Interrupt criteria are deliberately narrow:

- **Modeling decision** whose chosen direction would propagate as irreversible structure across multiple downstream sessions and where the right direction is genuinely unclear. Escalates as an SA-entry `open_questions` item with `blocking: true` plus a session-end pause.
- **Unsolvable problem** the agent has tried multiple approaches to. Escalates the same way.
- **Destructive-action decision** per Claude Code guardrails (`rm`, `git reset --hard`, force-push). Confirm before exercising.

Routine judgment calls during extraction (type framing, confidence labels, vocabulary additions, audit-rule refinements) are made by the session and recorded in the SA entry rather than escalated. The user's explicit framing (paraphrased): "I cannot be course-correcting and doing housekeeping sessions over and over. The only interruption should be because Claude cannot see a solution to a problem you face, or you have to make a choice that has large downstream impacts that are irreversible and the way forward is unclear."

This narrow interrupt criteria is what makes scheduled-task autonomous iteration tractable. A session that escalates routine judgment calls forces the user back into the loop and breaks the autonomous-throughput model.

### 3.7 What this looks like for Paideia

InfoGenesis's phases are about *which corpus content gets extracted*. Paideia's phases are about *which architecture layer gets built*. The phase decomposition for Paideia is the user's call, but a plausible first-pass structure:

- **P_0:** contract lock — settle remaining open items in the prompt pack (sessions 8-14 from CONTEXT.md plus the items raised in the prior conversation around node-level confidence, rendering policy, provisional-decisions discipline)
- **P_1:** SQL schema implementation — the Postgres tables for graph, learner events, mastery state
- **P_2:** seed graph rebuild at concept level for epistemology, replacing the current epistemology seed with the new schema
- **P_3:** ethics subdomain
- **P_4:** metaphysics subdomain
- **P_5:** philosophy of mind / language / science subdomains
- **P_6:** cross-domain edge generation (logic, mathematics, history service nodes terminating where they stop affecting comprehension of philosophy)
- **DEC.1:** retrieval / mastery-inference architecture decision
- **P_7:** self-correction pipeline implementation (Sonnet/Opus split, tension log schema)
- **P_8:** first teaching prototype (Sonnet teaching layer reading the rendering policy as system instructions)
- **P_9:** evaluation harness

The pattern that transfers regardless of decomposition: chunked-build-plan discipline, canonical session-schedule file, retirement-with-notes for refactored sections, budget tiers, bundling rule, end-state-quality first-pass principle, narrow auto-mode interrupt criteria.

---

## 4. The graph authoring layer

### 4.1 Chunked authoring with @type routing

`graph_chunks/prototype/` and `graph_chunks/seed/` hold the authored state-of-record. Each directory contains:

- `00_context.json` — master JSON-LD context. Single source of truth at stitch time; per-chunk @context references are not honored.
- `99_meta.json` — single `owl:Ontology` node and graph-level metadata.
- Per-@type chunk files (`10_classes.json`, `11_object_properties.json`, `12_datatype_properties.json`, `13_named_individuals.json`, `20_instances_pods.json`, `21_instances_documents.json`, ..., `62_instances_custom_scripting.json`).
- `90_provenance_NNN.json` shards for high-volume types (`ig:PointerBinding` is sharded; the file count is currently 33).
- `ROUTING.md` — the manifest defining @type-to-filename routing.

The chunk count at SA-064 is roughly 60 files for the prototype directory. The full prototype regenerated to ~2.3MB / 2,531 nodes via `publish_graph.py`. The chunked form is the authored surface; the root-level `infogenesis_prototype.json` is a build output and is not edited directly.

Numeric prefix conventions: `00_` for context, `10-19_` for schema (classes, properties), `20-89_` for instance buckets, `90-98_` for provenance shards, `99_` for ontology metadata. The `2N_` numeric range is reserved for first-class instance types; new type files claim the next available `2N_` number, and numeric gaps are acceptable. Post-SA-022, slots 26-29 are occupied; slot 30 onward is the next claim range.

### 4.2 The ROUTING.md manifest

ROUTING.md is the most operationally important file in the chunked-authoring system. It contains:

**A routing table** mapping `@type` → filename. Order in the table matches the order the partition script applies; first matching row wins. The table currently has ~80 rows.

**A compound-@type rule:** when @type is a list (e.g., `["ig:ExternalSystem", "owl:NamedIndividual"]`), routing uses the most-specific member.

**A shard rollover rule** for high-volume types. InfoGenesis went through two iterations: SA-015 committed a greedy size-based rollover (20 KB soft cap / 24 KB hard cap); SA-036 D111 retired that and replaced it with session-bound rollover (each session that adds new PointerBindings opens a fresh shard with the next available counter; sessions that add zero PointerBindings open no shard; once a session closes, its shard is frozen). The session-bound rule maps shards 1:1 to sessions, which makes diff review naturally per-session.

**Per-shard narrative paragraphs** logging what each shard contains, when it was created, and the per-session decisions that shaped it. The manifest is also the per-session log for the provenance subsystem. This is incidentally Paideia-relevant: ROUTING.md doubles as a long-form audit trail. Each paragraph runs ~200-400 words and chronicles the session that created the shard plus everything in it.

**New-type-creation rules:** if a session creates a node whose @type has no row, the session creates the corresponding chunk file, adds a row to the manifest, and records both as material changes in the change log.

### 4.3 The publish_graph.py script

~18KB of stdlib-only Python (Python ≥3.8). The full source structure:

- `load_context(src_dir)` — loads `00_context.json`.
- `collect_chunks(src_dir)` — reads every `*.json` under src in lexical filename order, excluding the master context. Each chunk file holds `{ "@graph": [...] }`.
- ID-uniqueness check — hard fail on duplicate `@id`, exit code 2.
- Soft-warn passes — undeclared @types, undeclared `ig:*` predicates (added at SA-053 per the Phase C/D PointerBinding-shape divergence finding), instances missing `ig:hasPointer` attestation, isolated nodes (added at SA-027 per D84), predicates declared without domain/range, entities missing `rdfs:label` or `skos:prefLabel`, render-readiness violations (labels containing namespace prefixes or construction-commentary tokens) — the latter three added at SA-029 per Phase 0 end-state contract lock.
- Output — one merged JSON-LD object, indent=2, terminating with a single newline.

The script is invoked as:

```bash
python publish_graph.py --src graph_chunks/prototype --out infogenesis_prototype.json
python publish_graph.py --src graph_chunks/seed --out infogenesis_ontology_seed.json
python publish_graph.py --src graph_chunks/prototype --validate-only
```

The validate-only mode prints per-category warning counts to stderr without writing output. Sessions run validate-only at session close as the audit pass.

The script has no third-party dependencies, no virtualenv, no setup.py. It's deliberately small and stable — the kind of utility that survives across 64 sessions without churn. The audit-pass extensions are added incrementally (SA-027, SA-029, SA-053) as the project's quality bar evolves; the core stitch logic doesn't change.

### 4.4 The provenance pattern

Each node carries a per-node provenance summary plus references to structured provenance nodes:

```json
{
  "@id": "ig:Customer",
  "@type": "owl:Class",
  "subClassOf": "ig:ConfigurationClass",
  "label": "Customer",
  "comment": "Customer tenant as recorded in LA...",
  "confidence": "EXTRACTED",
  "attestation": "Installation Guide, 'LA Setup — Create Customer and Instance' (p. 10).",
  "ig:hasPointer": [
    "igd:ptr-installation-guide-def-001",
    "igd:ptr-igcm-pos-terminal-def-638"
  ]
}
```

Three confidence levels: `EXTRACTED` (directly attested in source), `INTERPRETED` (inferred from how multiple sources treat the concept), `SYNTHETIC` (fabricated as an attachment point because some other concept needed a prerequisite to hang off — InfoGenesis avoids this aggressively, but the level exists in the schema).

`attestation` is a human-readable string citing the source-document section. `ig:hasPointer` references one or more PointerBinding nodes in the provenance shards. Each PointerBinding looks like:

```json
{
  "@id": "igd:ptr-installation-guide-def-001",
  "@type": "ig:PointerBinding",
  "ig:pointerPurpose": "ig:Definitional",
  "ig:targetDocument": "igd:doc-installation-guide",
  "ig:sectionAnchor": "LA Setup (formerly CDLS) — Create Customer and Instance (p. 10)"
}
```

Pointer purposes: `Definitional` (the section that defines what the entity is), `Configurational` (the section showing how the entity is configured), `Operational` (the section describing how the entity is used at runtime), `Licensing`, etc. The set of purposes is open and grows as new source-content shapes are encountered.

This is a two-tier provenance system: per-node confidence + attestation as quick reference, plus a separate provenance subgraph (the PointerBinding shards) for structured retrieval. The PointerBindings can be queried: "which nodes attest to section X of document Y?" The tiered structure means agents can render light citations from the per-node attestation string without traversing the provenance subgraph, but a chunk-resolver can use the structured pointers for source-document retrieval.

InfoGenesis handles a multi-target re-use pattern (D-shared-class-pointer, established at SA-046) where one PointerBinding can serve multiple node attestations when the source document organizes content by per-section anchor rather than per-node prose. SA-049's APIEndpoint extraction collapsed ~30 individual pointers into one shared pointer because the API Reference Guide describes all endpoints in one Overview section.

### 4.5 What this looks like for Paideia

The chunked authoring pattern is transferable. Specifics that change for Paideia:

**Chunk by subdomain, not by @type.** Paideia's nodes are concepts (philosophy concepts, eventually history/literature/etc. concepts). Chunking by domain — `epistemology.json`, `ethics.json`, `metaphysics.json`, `philosophy_of_mind.json`, `cross_domain_edges.json` — matches how the seed graph is structured logically and matches how concurrent extraction would parallelize. Within a domain, secondary partitioning by node type (concepts vs. edges) is also reasonable, but the primary axis is subdomain.

**A routing manifest mapping subdomain → filename.** Some concepts are cross-domain service nodes (logic primitives, mathematical prerequisites). Either route those to `service_nodes.json` or replicate within each domain that uses them with `owl:sameAs`-style linking. InfoGenesis's compound-@type rule has an analogue here.

**A `build_seed.py` script.** Stdlib Python, hard-fails on duplicate IDs and dangling edge references and cycle detection (already a settled Paideia commitment). Soft-warns on orphaned leaves, missing comments, suspicious cross-domain edge ratios, missing prerequisite chains. Validate-only mode for use as the session-close audit pass.

**Confidence-on-nodes is an open question for Paideia that InfoGenesis has answered.** When Opus generates a concept node for "Aristotle's distinction between potentiality and actuality," is that EXTRACTED from SEP, INTERPRETED from how multiple sources treat the concept, or SYNTHETIC because some downstream concept needed a prerequisite? The Paideia schema currently tracks weight/confidence/provenance/evidence on edges, but is silent on node-level confidence. The InfoGenesis pattern argues for explicit node-level confidence tags. Synthetic nodes become first candidates for the self-correction pipeline review when learner data surfaces evidence that the prerequisite chain is wrong.

**Chunked-authoring gives parallel-session extraction a clean shape.** Different sessions can extract different subdomains in parallel without merge conflicts on a shared seed file. With the eager-slot-claim discipline and per-session shard rollover for any high-volume node type Paideia ends up with (probably edges, given that hundreds of nodes will mean thousands of edges), parallel extraction becomes operationally tractable.

### 4.6 Storage format note

Paideia is going SQL with edge tables (settled architecture commitment, per CONTEXT.md as I remember it). InfoGenesis's chunked-JSON-LD format is for authoring; the runtime consumer (Copilot Studio) reads the merged JSON file. For Paideia, the chunked-JSON-LD pattern can still apply to the *authoring* surface even though the *runtime* consumer is Postgres. The build script then loads chunks and writes to the database (or to SQL migration files) instead of stitching to a single JSON output.

Alternatively, the chunked authoring can produce SQL directly — chunk files in some intermediate format (YAML, JSON, or even SQL fragments), build script generates `INSERT` statements for the seed migration. The format choice is independent of the chunked-authoring discipline.

---

## 5. The rendering policy layer (AGENT_INSTRUCTIONS.md)

### 5.1 What it is

A 200-line markdown document that defines how the deployed agent renders answers from the graph. It is the operational instruction set that gets copied into the consumer's system instructions (in InfoGenesis's case, Copilot Studio's system prompt). Separate from the design rationale — that lives in the carry-forward decisions in `project_state.md`. AGENT_INSTRUCTIONS.md is the "how do you talk" layer; project_state.md is the "why does this matter" layer.

The principle: **the graph is the agent's evidence substrate, not its vocabulary.** User-facing answers render in product terms an InfoGenesis installer or project manager would recognize and never surface the graph's own scaffolding.

### 5.2 The forbidden-token list

InfoGenesis explicitly enumerates what cannot appear in user-facing output:

- `subclass`, `superclass`, `object property`, `datatype property`, `predicate`
- `edge` or `node` in the graph sense, `traverse`, `walk the edge`, `class hierarchy`, `ontology`, `IRI`, `URI`, `namespace`
- `@id`, `@type`
- `"modeled as [X] attribute"` framing
- `enum values`, `X-to-Y relation`, `"load-bearing"`
- Construction-commentary IDs (`SQ-N`, `OQ-N`, `SA-NNN`, `D-NN`)
- Backticked predicate names like `readsConfigFrom`, `cookMode`, `reloadTarget`

Property identifiers are camelCase internal names; they never render verbatim. Each property's comment field carries a product-prose paraphrase, and the agent uses the paraphrase. `ig:readsConfigFrom` is not "the readsConfigFrom edge"; it is "the App Server a terminal reads its configuration from."

### 5.3 The class-identifier two-tier distinction

Class identifiers split into two categories:

**Survives into output verbatim:** class names that are also product nouns the user recognizes. `Cook`, `Reload`, `Terminal`, `App Server`, `Application Profile`, `Package`, `Pod`. These are things the user observes or invokes; they're product vocabulary.

**Never surfaces:** class identifiers that exist only as scaffolding. `ConfigurationOperation`, `ExternalSystem`, `ExternalIntegration`. These are paraphrased into product role ("operations that propagate configuration changes," "the system that distributes packages," "a third-party service IG integrates with").

For Paideia, the analogue is concept names like "ad hominem" or "modus ponens" or "the Forms" survive verbatim (they're what the learner is here to acquire) versus meta-categories like "logical fallacy," "epistemological position," "service node," "scaffolding-proximity," "mastery threshold" which are scaffolding-only.

### 5.4 The construction-commentary filter

Comments may carry project-internal annotations — sample-question references, open-question IDs, session IDs, "load-bearing for" markers, provisional-shape markers. The agent strips all of it from user-facing output. "Load-bearing for sample question 3" never reaches the user. "Provisional shape (OQ-F)" never reaches the user.

The `confidence` and `attestation` fields are authorship provenance. Attestation names IG document sections — useful as citation source when paraphrased. Confidence values (`EXTRACTED`, `INTERPRETED`, `SYNTHETIC`) are internal — never surface. When content is INTERPRETED rather than directly attested, the agent flags the interpretation in product terms ("the Installation Guide does not explicitly say X, but the pattern across per-product install sequences implies...") — never by citing the tag name.

### 5.5 Source pointers and citations

InfoGenesis cites using document titles and section anchors: "Installation Guide, 'LA Setup — Mapping Application Profile to Instance' (p. 11)". Pointer IDs, pointer-purpose class names, scope-attribute names — none surface. Product scope and version scope on pointers are useful for disambiguation and surface as plain English ("this is specifically the IG Kiosk 12.3.14 behavior; the Fly variant may differ").

### 5.6 Uncertainty posture

When the graph's shape on a question is undetermined, the agent says so in product terms — "the installation documentation does not determine this; check the customer's LA record." The agent does not name the open question or cite the schema. **Honesty about openness passes; fabrication of a hard rule the docs do not specify fails.**

When the scenario requires customer-specific data the agent does not have, it describes the retrieval method and names the system of record. It does not invent customer-side values. ("LA for profile state, CDLS for package distribution, the App Server for cook timestamps.")

### 5.7 The worked example

AGENT_INSTRUCTIONS.md ends with a concrete worked example showing a user query, a fail case (ontology voice), and a pass case (product voice) for the same retrieved facts. The fail case:

> Cook and Reload are subclasses of ConfigurationOperation. Traverse the readsConfigFrom edge and compare lastCookTimestamp to lastReloadTimestamp.

The pass case:

> Start by checking which App Server the misbehaving terminal is reading configuration from. A terminal consumes the configuration its App Server's Prepare Terminal Data has prepared — if the terminal is pointing at a different App Server than the working ones, that is the first thing to fix. Assuming it is on the right App Server, compare freshness: the App Server records when Cook last ran, and the terminal records when Reload last completed. If the terminal's Reload is older than the App Server's Cook, it has not picked up the latest prepared configuration — force a Reload (SMU Reload Menus, the Send Command Reload Terminal Config scheduled task, or the Reload Config checkbox on the Prepare Terminal Data dialog).

Both reason over the same retrieved facts. The difference is voice. The worked example is what makes the policy operational rather than aspirational.

### 5.8 Why this is the highest-value transferable artifact for Paideia

Paideia has an expression contract in `pedagogy.md` (per my memory of CONTEXT.md). The contract is settled in principle but probably hasn't been pulled out as a standalone artifact with operational teeth. Pedagogy.md captures *why* the expression contract exists; the rendering policy is the operational rules the Sonnet teaching layer reads as system instructions.

The Paideia version would contain:

- **Forbidden tokens.** Mastery state names (exposed/demonstrated/inferred as user-facing terms), prerequisite-edge framing, evidence-event references, decay, scaffolding-proximity language, weight/confidence/provenance exposure, graph_version references, anything from the event-source schema, the tension-log mechanism, the self-correction-pipeline mechanism. Internal terms like "Sonnet teaching layer" or "Opus graph construction" or "service node."

- **Surviving tokens.** Concept names (modus ponens, the Forms, syllogistic, etc.) survive verbatim. Domain-area names (epistemology, ethics, metaphysics) survive when relevant.

- **Scaffolding-vs-concept distinction.** Concept nodes by name; meta-categories never surface.

- **Citation rules.** When the system references SEP or other sources for the learner's onward reading, what's the citation form? When does the system invent new explanations vs. point to existing scholarship?

- **Uncertainty posture.** When the system's confidence on a learner's mastery state is low, how does it express that? "Let's check this together" vs. "your inferred-tier evidence is weak" — only the first survives.

- **A worked example.** A learner asks "why are we doing this next" and the response shows what the graph-voice answer looks like (forbidden) versus the pedagogical-voice answer (passing).

This becomes a system-instructions document for the Sonnet teaching layer, separate from pedagogy.md (which is design rationale).

---

## 6. The decision-tracking layered system

InfoGenesis's decisions are tracked across multiple layers, with different semantics:

### 6.1 Layer 1 — Carry-forward decisions (project_state.md)

The committed-and-not-subject-to-re-litigation layer. Currently ~30 entries in InfoGenesis covering: graph is a file artifact (not hosted database), representation is typed entity layer (not full OWL inference), JSON-LD with .json extension is canonical, Copilot Studio is sole current consumer with fork-capability constraint, ontology stability rests on IG vocabulary stability, the graph encodes authority/relationships/state/causality (not procedural checklists), rendering voice is first-class output requirement separate from content correctness, sessions operate autonomously under Start Engine with narrow interrupt criteria, end-state quality first-pass principle, build-plan structure is phased (post-SA-028 refactor), session schedule is canonical, etc.

Each carry-forward names: the decision in declarative form, when it was committed, what evidence drove it, and (sometimes) what later evidence would warrant retraction. Retracted decisions are preserved as historical record rather than deleted.

The Paideia analogue is **CONTEXT.md plus the downstream files** (architecture.md, pedagogy.md, etc.). The structure is parallel; the topics differ.

### 6.2 Layer 2 — Open questions (tensions.md analogue)

Unresolved tensions that are actively in scope. InfoGenesis tracks these inside SA entries (`open_questions` field) with global OQ-N identifiers, plus a centralized `ontology_notes/07_watch_flag_items.md` for standing watch-flag items that aren't immediately actionable.

The Paideia analogue is **tensions.md** — already established in CONTEXT.md as I remember it.

### 6.3 Layer 3 — Provisional decisions (closed-but-revisitable)

This is the layer Paideia doesn't currently have. InfoGenesis tracks these in two places:

**Inside SA entries**, on individual decisions where `status: "provisional"` rather than `committed`. Example from SA-006: "S0.4 prototype drafting chose Pod-as-domain for both `hasBasePackage` and `hasAddOn` at instance level... approach read cleanly at the prototype scale... PackageBinding reification remains the fallback if S1 test runs expose retrieval ambiguity. SQ-3 is *provisionally* resolved in favor of the loose-relation approach; confirmation awaits S1 evidence."

**Inside `ontology_notes/05_judgment_calls_during_drafting.md`**, a file that captures modeling decisions that weren't pre-named as open questions but had to be made during drafting. Each entry records: the alternatives, the choice taken, the reasoning, and the trigger condition that would cause re-opening. Examples from the actual file:

- "Instance versus Application Profile cardinality" — pilot documentation does not force the choice; modeled `hasApplicationProfile` and `mappedToInstance` without asserting cardinality constraints; if S0.4 prototype population exposes a case where the cardinality matters, the shape can be tightened.
- "Package and AddOn as parent/subclass rather than peers" — both are distributable versioned artifacts and the difference is relational; if a later session finds AddOn carries attributes Package does not (or vice versa) that break the subclass semantics, the shape can be revisited.
- "Per-Pod Base Package binding not yet reified" — the strict modeling is a ternary; took the loose-relation approach; if S0.4 shows this forces awkward representation, the PackageBinding reification is the fallback.

This middle tier matters because it has nowhere to go in Paideia's current documentation system. CONTEXT.md is for settled, tensions.md is for unresolved — the "decided provisionally because the seed graph forced a choice but the evidence is thin" category currently has no home. That's where things end up that get re-litigated in later sessions because nobody remembered why we chose A over B.

The Paideia analogue would be a new file: `provisional-decisions.md` or `judgment-calls.md`. Empty at first; populated as the seed graph rebuild generates judgment calls. Each entry: alternatives considered, choice taken, reasoning, re-opening trigger.

### 6.4 Layer 4 — Watch-flag items (`07_watch_flag_items.md`)

A separate file in `ontology_notes/` that captures questions that aren't decisions and aren't actively being resolved — they're things to watch for in future evidence. Example: "OQ-N (Shane's Config Guide reservation, SA-004) — Not a seed decision but a standing empirical question: will install-and-troubleshoot test questions consistently traverse into configured-entity content?"

Watch-flag items are pure prompts for future attention. They don't carry a decision; they carry a question to keep in mind. If evidence arrives, they get promoted to open-question status (Layer 2) or trigger a decision (Layer 1 or Layer 3).

The Paideia analogue might fold into tensions.md with explicit "watch-flag" tagging, or split into its own `watch-flags.md`. Probably overkill for early Paideia; the InfoGenesis four-layer split emerged at scale.

### 6.5 Layer 5 — Session-level decisions (SA-entry `decisions` field)

The atomic decision level. Every decision a session makes gets a D-NN entry with rationale, alternatives, status (committed/provisional), and an optional `closes_open_question` reference. These are the building blocks; the higher layers reference them.

InfoGenesis is at D181 after 64 sessions. The decision graph is independent of the session graph: a single session may produce 1-15 decisions, and decisions reference each other across sessions ("per the SA-029 D102 audit-rule precedent" in an SA-053 decision rationale).

### 6.6 Cross-layer references

InfoGenesis uses bare counter IDs for all cross-references (`closes_open_question: "OQ-V"`, `change_log_refs: ["CL-061"]`, `closes: "SQ-3"` as referenced in SA narrative). The slug suffix on filenames is a retrieval aid only; cross-references never use the slug. This means slug revisions don't invalidate references, and retroactive renames are safe. Established at SA-017 when the slug convention was retroactively applied to all 16 prior SA entries and all 65 prior CL entries in one bulk rename.

---

## 7. Filesystem layout reference

Relative to project root, full layout at SA-064:

```
infogenesis_graph/
├── README.md                         (orientation for fresh reader)
├── CLAUDE.md                         (orientation for AI sessions)
├── OPERATIONS.md                     (procedural depth — session lifecycle, write paths, archival, schemas)
├── project_state.md                  (carry-forward decisions, scope, pilot profile)
├── AGENT_INSTRUCTIONS.md             (consumer-side rendering policy)
├── HANDOFF.md                        (deferred items, receiving-engineer starting basis)
├── LICENSE                           (placeholder)
├── pyproject.toml                    (housekeeping)
├── .gitattributes                    (LF normalization)
├── .gitignore                        (.claude, _archive, etc.)
├── publish_graph.py                  (chunks-to-JSON-LD stitch script)
├── resolve_pointer.py                (chunk-resolver primitive — added at SA-053)
├── infogenesis_prototype.json        (build output, 2.3MB)
├── infogenesis_ontology_seed.json    (build output, 90KB)
├── ig_knowledge.png                  (architectural diagram)
│
├── source_files/                     (96 source PDFs, read-only inputs)
│
├── graph_chunks/
│   ├── prototype/                    (state-of-record for prototype)
│   │   ├── 00_context.json
│   │   ├── 99_meta.json
│   │   ├── 10-13_*.json              (schema chunks)
│   │   ├── 20-62_instances_*.json    (instance buckets)
│   │   ├── 90_provenance_001-033.json (sharded PointerBindings)
│   │   └── ROUTING.md                (manifest)
│   └── seed/                         (parallel structure for seed)
│
├── chunk_index/                      (chunk-resolver index, SA-053+)
│   └── by_document/<doc-slug>.json
│
├── build_plan/
│   ├── MANIFEST.md
│   ├── 00_preamble.md
│   ├── 00_session_schedule.md        (canonical session breakdown)
│   ├── P_0_*.md ... P_I_*.md         (phase chunks)
│   ├── S0_*.md ... S6_*.md           (stage chunks, some retired)
│   └── 99_session_flow.md
│
├── ontology_notes/
│   ├── MANIFEST.md
│   ├── 00_intro.md
│   ├── 01-10_*.md                    (modeling decisions, judgment calls, validations)
│   └── SA011_* / SA012_*             (SA-cluster modeling notes)
│
├── document_register/
│   ├── MANIFEST.md
│   └── *.md                          (per-classification chunks of the corpus survey)
│
├── glossary/
│   ├── MANIFEST.md
│   └── *.md                          (per-term chunks of IG vocabulary)
│
├── test_plan/
│   ├── MANIFEST.md
│   └── *.md                          (per-question chunks of validation battery)
│
├── session_audit/
│   ├── register_state.json           (counter)
│   └── entries/
│       └── SA-NNN_<slug>.json        (one per session)
│
├── change_log/
│   ├── register_state.json           (counter)
│   └── entries/
│       └── CL-NNN_<op>_<artifact>[_<scope>].json (one per material change)
│
├── _archive/                         (pre-edit snapshots, retired at handoff)
│   └── <artifact>_SA-NNN.<ext>
│
└── .claude/                          (Claude Code harness state, gitignored)
    └── settings.local.json
```

Five chunked-authoring directories beyond the graph itself: `build_plan/`, `ontology_notes/`, `document_register/`, `glossary/`, `test_plan/`. Each follows the manifest-plus-chunks pattern. The chunked-prose pattern was established at SA-018 to retire the pre-existing monolithic prose files (`build_plan.md`, `infogenesis_ontology_seed_notes.md`, etc.) which had been silently truncating under the SA-010 Cowork pattern. Under Claude Code, the chunked form persists for retrieval economy and per-session-tagged archival rather than for truncation defense.

For Paideia, the chunked-prose pattern probably applies to any prose artifact that grows past a few thousand words. CONTEXT.md is probably fine as a single file; tensions.md is probably fine as a single file. The seed graph is the immediate candidate for chunking. The build_plan is the next.

---

## 8. The two-environment model and what's now retired

InfoGenesis currently runs two execution environments:

**Claude.ai with MCP** — Claude.ai web/desktop client with `mcp-server-filesystem` for atomic writes. Failure mode: MCP server wedging under load (4-minute timeouts). Recovery: restart Claude.ai client.

**Claude Code** — Anthropic's CLI client with native file tools, real bash, sub-agent delegation, native PDF reading, persistent harness memory directory, 1M-token context window. Atomic file-tool writes. Workhorse for build sessions.

A third environment (Cowork) was active through SA-042 and retired at SA-043. The retirement landed because Cowork's failure mode (the SA-010 silent-truncation pattern at ~25 KB) was specific to that environment, and Claude Code's empirical observation across 17 sessions surfaced no truncation. The bash post-write verification step that was retained as defense in depth from SA-023 through SA-042 was retired with Cowork. The Cowork-era artifacts (chunked authoring partly motivated by truncation defense, append-mode-heredoc patterns, 25 KB shard caps) persist for procedural continuity but no longer serve their original purpose.

Paideia probably runs Claude Code as the build environment (matches InfoGenesis's workhorse). Claude.ai-with-MCP is useful for design-and-discussion sessions where the user is actively in the loop; Claude Code is useful for autonomous build execution. The execution_environment field on SA entries declares which.

---

## 9. Specific patterns worth copying

A consolidated list of patterns from sections 2-6, ordered roughly by load-bearing-ness for autonomous iteration:

1. **The SA/CL discipline as a whole.** The single most important thing to copy. Without it, autonomous iteration is unreachable. SA entries with the dense entry_state/exit_state paragraphs, eager slot claim with stub entry, full nine-step startup procedure, full nine-step shutdown procedure with audit pass.

2. **The two registers (`session_audit/register_state.json` and `change_log/register_state.json`).** Tiny files, load-bearing for slot-claim safety.

3. **Global decision IDs (D-NN).** Stable cross-references across rephrasing and slug revisions.

4. **`OPERATIONS.md` as the procedural-depth document.** Read on demand for specific procedural questions, not at every session start. CLAUDE.md is the orientation entry point that points at it.

5. **`project_state.md` (Paideia: `CONTEXT.md`) as the carry-forward decisions document.** Read at the start of every "Start Engine" session.

6. **Build-plan as a chunked manifest plus per-step chunks.** With a canonical session-schedule file.

7. **Budget tiers (60/70 extraction, 70/80 mechanical).** Anchor for when to split sessions.

8. **End-state-quality first-pass principle.** Extraction completes against contract; no deferred rework.

9. **Auto-mode with narrow interrupt criteria.** Routine judgment is session-internal; only irreversible-with-unclear-path / unsolvable / destructive-action escalate.

10. **Chunked authoring with a routing manifest.** Per-domain (Paideia) or per-@type (InfoGenesis) chunks plus a manifest.

11. **A stdlib-Python build script (~18KB) with hard-fail-on-id-uniqueness and soft-warn-on-everything-else.** Validate-only mode for the audit pass.

12. **A standalone rendering policy document (`AGENT_INSTRUCTIONS.md`).** Forbidden tokens, paraphrase patterns, scaffolding-vs-concept distinction, worked example.

13. **Confidence-on-nodes with three levels** (`EXTRACTED`, `INTERPRETED`, `SYNTHETIC`) plus per-node attestation strings.

14. **The five-layer decision-tracking system** (carry-forward / open-questions / provisional / watch-flag / session-level). Paideia probably needs at least three of these layers (carry-forward via CONTEXT.md, open-questions via tensions.md, provisional via a new file).

15. **The multi-target shared-pointer pattern** for provenance when source organization is per-section rather than per-node. Probably relevant when Paideia maps SEP articles to multiple concept nodes.

16. **The construction-commentary filter** in node comments (session IDs, decision references, watch-flag markers — accumulate in node prose for traceability, get stripped by the rendering layer).

17. **The retirement-with-notes pattern** for refactored sections. Old chunks aren't deleted; they're marked RETIRED with notes pointing at the new structure. Preserves traceability without breaking historical references.

---

## 10. Specific patterns NOT to copy (or to adapt heavily)

1. **The `_archive/` discipline.** Retain git from session zero; git history covers the recovery surface. Paideia doesn't need pre-edit snapshots.

2. **JSON-LD as the storage format.** Paideia is going SQL with edge tables. The chunked-authoring discipline transfers; the JSON-LD-specific bits don't.

3. **OWL/RDF semantics.** InfoGenesis explicitly chose typed-entity-layer rather than full-OWL-inference; Paideia's analogue is the SQL edge-table schema. The OWL declarations in InfoGenesis (`owl:Class`, `owl:ObjectProperty`, `rdfs:domain`, `rdfs:range`) don't transfer.

4. **The Cowork-era artifacts.** Append-mode-heredoc, bash post-write verification, 25 KB shard caps — these were Cowork-specific and have been retired or are scheduled for retirement. Paideia doesn't have a Cowork analogue and shouldn't inherit the artifacts.

5. **The 96-PDF source corpus extraction methodology.** Paideia uses SEP as structural reference, not as a corpus to extract. The "read PDF, lift entities, attest with section anchor" pattern doesn't apply directly. A Paideia analogue might be "read SEP article, identify which concepts are in scope, propose edges to existing nodes, flag for review" — different mechanics.

6. **CL entries on application code.** Scope CL discipline to project-state-of-record (design docs, schemas, seed graph chunks, build_plan); let git serve as the system of record for application code.

7. **Pure-JSON SA entries.** Paideia might be better served by markdown-with-frontmatter SA entries since the design docs are markdown and the prose-heavy fields (entry_state, exit_state, decision rationale) read better as markdown. Optional adaptation.

8. **Sample-question battery as the organizing principle for early extraction.** InfoGenesis spent 24 sessions before Shane corrected the closed-loop self-validation pattern (questions designer-authored against the graph, graph designer-populated to traverse the questions, criteria designer-seeded with nouns the graph already encodes — pass rates that aren't proof). Paideia should not bind extraction to a sample-question battery; bind it to corpus or domain coverage.

---

## 11. Things that don't directly apply but provide context

1. **The retrieval-pipeline architecture decision (S2.5).** InfoGenesis chose a hybrid pipeline (named-section retrieval over a pre-processed chunk index, with optional similarity-fallback) at SA-052/053. The chunk-resolver (`resolve_pointer.py`, ~13KB) is keyed by `(documentRef, sectionAnchor)` and returns chunks from a per-document JSON index whose pageRange overlaps the parsed page-set. Paideia's retrieval problem is different (SEP-or-similar onward-reading lookup, not ground-truth-attestation lookup), but the architecture-decision-as-a-discrete-session pattern is worth noting. InfoGenesis put the decision in its own session (DEC.1) at the point in the build where post-Phase-D substrate made testing meaningful.

2. **The chunk-resolver coverage roadmap.** InfoGenesis is at 6 of 31 documents indexed. The coverage roadmap is incremental — extraction sessions touching a source PDF index it as part of the work; standalone bootstrap sessions backfill un-indexed documents in priority order (most-PointerBindings-first). Paideia analogue might be SEP-article-coverage if Paideia ends up needing structured SEP retrieval.

3. **The PointerBinding schema canonicalization issue (D159, SA-053).** InfoGenesis discovered at SA-053 that 128 of its 950 PointerBindings carry divergent schema variants from sessions that drifted (`ig:documentRef` vs `ig:targetDocument`, `ig:scope` vs the canonical fields, `ig:supportingQuote` as a new evidence field). The decision is queued pending user direction: either rewrite to canonical or formalize the new predicates. The lesson: schema drift across sessions is real even with audit passes; the audit catches structural mistakes but not predicate-renaming drift unless the audit specifically checks declared-predicate coverage. For Paideia, schema drift is a risk worth designing the audit pass against from session zero.

4. **The model-fabrication pattern at SA-064.** When a sub-agent dispatch was given a too-large fiscal PDF (1.8MB Philippines), the sub-agent returned fabricated extraction (Setting IDs in 2401-3305 range with FB_RESEND_CERT-style function-button names that didn't match the actual Agilysys product convention). The fabrication pattern matched a model failing-silent-on-PDF-too-large by hallucinating plausible-looking content. Spot-check via a known-good source caught it; tightened second sub-agent dispatch with explicit no-fabrication discipline plus reference patterns from the verified Costa Rica + India extractions produced credible output. The lesson: when sub-agent extraction returns content, the credibility bar is "did the extraction surface real product vocabulary patterns the seed corpus already carries" — not "does the content look plausible."

5. **The session-shard mapping pattern.** Each session that adds PointerBindings opens a fresh shard. This means each shard is one session's output; diff review is naturally per-session, ROUTING.md narrative paragraphs are the per-session log. Paideia analogue is unclear (depends on whether any Paideia node type ends up high-volume enough to shard), but the pattern of per-session-tagged file outputs is worth noting.

6. **The HANDOFF.md document.** InfoGenesis maintains a handoff document throughout the build that names what's deferred to handoff: build_plan flatten to ROADMAP, change_log flatten to CHANGELOG, decision about session_audit/ disposition, decision about whether SA/CL discipline continues post-handoff, filename canonicalization rename, src/docs/data reorg, archival retirement, LICENSE replacement, README pass against final state, memory directory cleanup. Paideia doesn't currently have a handoff target (no plan to hand off), but the discipline of capturing "things deferred to a future major-state-transition session" is useful regardless.

7. **The Phase 0 contract lock.** InfoGenesis runs a one-time Phase 0 session that locks the function-layer primitive contracts, OWL/RDF semantics, per-entity completeness contract, provenance schema, and rendering-layer requirements. The audit pass extends with the new categories at the same time. The 486-node prototype is brought up to contract inline. After Phase 0, every session enforces the contract; no separate rework passes. The pattern of "lock the contract once, audit against it forever" is high-leverage for autonomous iteration.

8. **The Cowork three-environment retirement timeline.** Cowork was the original write-path environment with the SA-010 silent-truncation failure mode at ~25 KB. The chunked-authoring discipline, the bash post-write verification, the append-mode-heredoc pattern, and the size-based shard rollover were all defenses against truncation. SA-023 introduced Claude Code; SA-042 retired Cowork; SA-043 retired the Cowork-specific defenses. The chunked-authoring discipline survived because it serves retrieval economy and per-session-tagged archival cleanly, even with truncation no longer a threat. The lesson: rules calibrated for one environment need re-checking when the environment changes; retain rules that found new justifications, retire rules whose original justifications are gone.

9. **The build_plan SA-028 refactor.** The pre-SA-028 build plan was structured by document-class groupings; the post-SA-028 build plan is structured by product-topology dependency. The refactor came after 24 sessions of evidence that the original ordering was inverting product dependencies. The refactored chunks (P_0 through P_I) replaced the S3/S4 substages, which were marked RETIRED in the manifest with notes about which phase they folded into. The lesson: build_plan structure is itself a settled-decision-that-can-be-retracted-on-evidence; the refactor is its own session and the audit log preserves the retraction.

10. **The synthesis-battery retirement at SA-025.** InfoGenesis ran a 13-question synthesis battery as a build-phase gate through SA-024. SA-025 retired it as a build-phase gate (replaced by extraction-time audit passes; reactivated at S5.5 as head-to-head against chunked-indexing baseline). The retirement landed because the battery was closed-loop self-validation: questions designer-authored against the graph, graph designer-populated to traverse the questions, criteria designer-seeded with nouns the graph already encodes — pass rates that weren't the proof the project actually needed. The replacement is comparison against an external baseline at S5.5, which produces ordinal signal robust to designer drift. The lesson: validation against your own authored criteria is weak signal; validation against an external baseline is strong signal.

---

## 12. Open questions and things I couldn't fully verify

1. **Paideia's current state.** My memory of Paideia comes from the user-memories block in this conversation. The fresh session reading this report has access to actual current Paideia files (CONTEXT.md and downstream) and should treat the actual files as authoritative if they conflict with anything I've described. Specific places where my memory may be stale: the prompt pack progress (sessions 8-14), the seed graph file location, the exact set of downstream files referenced by CONTEXT.md, whether the rendering policy already exists as a standalone artifact, whether confidence-on-nodes has been settled.

2. **Whether Paideia's filesystem MCP can access the InfoGenesis directory.** This session had access to InfoGenesis via the MCP filesystem at `C:\Users\kidds\projects\infogenesis_graph` but did not have access to the Paideia directory at `/Users/shanekidd/Documents/Claude_Files/Paideia/`. The two paths suggest different OS contexts (Windows for InfoGenesis, macOS for Paideia) which may or may not be the same machine via different filesystems. The fresh session in Paideia may or may not have access to InfoGenesis for verification; if needed, this report's claims can be verified by opening the InfoGenesis files directly.

3. **Whether the SA-NNN counter naming convention transfers cleanly.** InfoGenesis is at SA-064; Paideia would start at SA-001. Whether SA-001 should be a retroactive entry capturing the project state at SA/CL adoption (everything in CONTEXT.md and downstream files as of the adoption session) versus a forward-only entry that defers historical context to entry_state references is a setup-time choice. InfoGenesis's actual SA-001 isn't visible to me from this session; checking how InfoGenesis handled its own SA-001-equivalent might inform the choice.

4. **Whether to bootstrap the discipline manually or via a Claude Code session.** InfoGenesis's discipline emerged organically across early sessions; the SA-NNN counter started somewhere and the conventions evolved. Paideia could either bootstrap manually (user creates the session_audit/, change_log/, build_plan/ directories with their initial contents and commits them as a setup), or write a setup spec detailed enough for a Claude Code session to execute the scaffolding from the spec. The user's call.

5. **The exact line between application code and project-state-of-record.** I've recommended scoping CL discipline to the latter, but the boundary is fuzzy. Schema migrations are application code or project-state-of-record? SQL files defining the seed graph are project-state-of-record; Python files implementing the build script are project-state-of-record; React components for the teaching UI are application code. The boundary that probably works: anything in `paideia/graph/`, `paideia/build/`, `paideia/docs/`, `paideia/seed/` is project-state-of-record (CL-tracked); anything in `paideia/app/`, `paideia/api/`, `paideia/web/` is application code (git-only). The exact directory layout is the user's call.

6. **Whether the chunked-authoring pattern should apply to Paideia's domain decomposition from session zero, or only when the seed graph crosses some node-count threshold.** InfoGenesis introduced chunking at SA-015 when the prototype was at ~50 nodes. Earlier than the seed-graph-grows-large threshold I gestured at in the prior conversation. The pattern is cheap to set up and pays back as soon as more than one session is touching graph content concurrently; probably worth doing from session zero rather than waiting.

7. **Whether to copy InfoGenesis's specific markdown structure conventions (no numbered headings, bold for definitional statements only, prose preferred over lists) into Paideia's documentation.** This is style discipline rather than architecture. The user has consistent preferences expressed in the system prompt; whether the InfoGenesis stylistic choices match those preferences is the user's read.

8. **Worktree branch naming.** InfoGenesis uses `claude/<slug>` where the slug is a random Heroku-style identifier (like `claude/vigilant-herschel-d3240e`). This is the Claude Code default. The slug is meaningful only as a unique session-thread identifier; the SA-NNN counter is what carries semantic meaning. Paideia inherits this from Claude Code without need for adaptation.

---

## 13. Numerical reality check

For calibration, here's what InfoGenesis actually looks like at SA-064:

- **Sessions:** 64 closed, 1+ in flight (next_id 066 means 065 is in flight)
- **Decisions:** 181 (D-NN counter)
- **Open questions:** ~20 still open (most closed by various phase sessions)
- **Change log entries:** 473
- **Graph nodes (prototype):** 2,531
- **Graph nodes (seed):** 407 (schema-only)
- **PointerBindings:** 1,138
- **Provenance shards:** 33
- **Source documents (extracted):** 31 of ~96 total in `source_files/`
- **Chunk files in graph_chunks/prototype:** ~60
- **Build plan chunks:** ~30 markdown files
- **Ontology notes chunks:** ~30 markdown files
- **Test plan chunks:** ~10 markdown files
- **Document register chunks:** ~20 markdown files
- **Glossary chunks:** ~10 markdown files
- **Total project size on disk:** ~3MB excluding source_files PDFs; ~3MB graph artifacts; source_files is the bulk of disk usage (96 PDFs)

Build time per the user: ~30 hours of Claude Code session time produced this. Probably distributed across calendar weeks rather than a continuous session block.

Paideia at start: 0 sessions, 0 decisions, 1 seed graph file (epistemology), some number of design docs (CONTEXT.md and downstream), prompt pack with sessions 1-7 closed and 8-14 pending.

Paideia at scale: probably similar order of magnitude when the philosophy domain is fully extracted (hundreds to low thousands of concept nodes plus more edges than nodes). Multi-domain expansion (history, literature, etc.) compounds the count.

---

## 14. Quick-reference summary

The single most important thing to copy from InfoGenesis: **the SA/CL discipline plus eager-slot-claim plus auto-mode plus narrow-interrupt-criteria**. This is what enables 30-hour autonomous build to 2,500-node graph. Without it, every session needs human briefing.

The single most important thing to add for Paideia that InfoGenesis demonstrates the value of: **a standalone AGENT_INSTRUCTIONS.md (rendering policy) document with forbidden tokens, paraphrase patterns, and a worked example.** This becomes the operational rules for the Sonnet teaching layer.

The single most important thing NOT to copy: **the `_archive/` pre-edit-snapshot discipline.** Git from session zero covers the recovery surface; the archival discipline is overhead.

The most consequential adaptation: **chunk the seed graph by subdomain, not by @type.** Paideia's domains are the natural axis; @type would scatter related content across unrelated files.

The most likely place for Paideia to drift if the discipline isn't tight: **schema drift across sessions** (per InfoGenesis's D159 finding at SA-053). The audit pass needs to check declared-predicate coverage, not just node-level structural integrity. A `build_seed.py --validate-only` that hard-fails on cycles, duplicates, dangling refs, and soft-warns on undeclared predicates / attribute drift / orphaned leaves should be in place before extraction starts at scale.

---

*End of report. ~10,500 words.*
