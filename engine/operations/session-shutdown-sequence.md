# Session shutdown sequence

> How a build session closes cleanly. Boot procedure lives in [`session-build-lifecycle.md`](session-build-lifecycle.md).
>
> **Canonical invocation:** Skill `session-shutdown-sequence` (per [ADR 0044](../adr/0044-skill-conversion-recipe-vs-reference.md)). The skill's body is the procedural form of this document; this document is the Layer 1 source-of-truth prose. Updates flow doc → skill, never the reverse.

## When this runs

At the end of every build session — once substantive work is at a commitable checkpoint, before the conversation ends. Run in order. Do not skip steps; the shutdown produces the durable artifacts that downstream sessions read.

## Sequence

> **Ordering note (per Issue #126, S-0163; substrate name updated at S-0192).** The diary write (step 1), the activity rollup (step 2), and the pushback/lesson capture (within step 1) all run BEFORE the audit pass (step 3). Sequencing the diary write + rollup before the audit means `validate.py --final-check` sees a complete `engine_memory_activity` field and the diary-write check passes truthfully.

### 1. Write session diary entry

Per [`engine-memory-operations.md`](engine-memory-operations.md). The engine_memory diary carries the AI's first-person reflection on the session — distinct from `outcome_summary` (outcome-focused) and ENGINE_LOG (third-person artifact narrative). What surprised me, what I noticed but didn't act on, what feels load-bearing for the next session, where my judgment was uncertain.

Build sessions only. Default-mode (exploration) sessions skip — no slot, no formal close.

Call `engine_memory_diary_write` (per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md), supersedes mempalace_diary_write at S-0192) with `agent_name: "claude"` (project convention). Content shape: 150-400 words, first person. Recommended structure (not required):

- **What I worked on this session** — one paragraph; high-level enough to be findable by `engine_memory_diary_read` at the next session's boot.
- **What surprised me** — premises that didn't hold, side-discoveries, anything that updated my model of how this project works.
- **What I noticed but deferred** — observations that are out-of-scope for this session but next-session-relevant. (If actionable enough, also surface in HANDOFF.md or as a follow-up task in `outcome_summary`; the diary is the lower-formality channel for things that don't quite warrant a tracked task.)
- **Where my judgment was uncertain** — places I made a call I'd want a fresh-eyes review on, or where I'd phrase the question differently if I were starting fresh.

After the diary write, run the **`pushback` / `lesson` capture check** (added at S-0041 per the second project health check audit's adoption-gap finding — the tags were defined at S-0032 with zero applications across the eight intervening sessions because the convention was too implicit to reach the AI's authoring loop without an explicit prompt). Ask explicitly:

- **Did this session produce a `pushback` moment?** A `pushback` moment is a verbatim exchange where you (the AI) surfaced an unnamed risk specifically (not generic concern), the user heard it, and the conversation changed direction in response. Self-pushback also qualifies — your own self-critique that the user accepted. If yes, capture it now via `engine_memory_add_drawer` per the [`pushback` tag definition in engine-memory-conventions.md](engine-memory-conventions.md). The capture preserves verbatim user framing + verbatim AI pushback + verbatim user acceptance + one-line summary of the change. Without verbatim, the recall value collapses.
- **Did this session produce a `lesson` candidate?** A `lesson` candidate is a procedural failure with a non-obvious cause and a working fix — "we tried X, it failed because non-obvious Y, the fix that worked was Z." A bug whose cause was obvious-once-named also qualifies if the *identification* was the value. If yes, capture it now via `engine_memory_add_drawer` per the [`lesson` tag definition](engine-memory-conventions.md). The capture preserves the failed approach (specific enough to be findable on similar approaches), the non-obvious reason it failed, the working fix, and optional pointers to related ADRs or ops docs.

Both capture decisions are explicit yes/no asks at every shutdown — not a heuristic for the AI to apply by judgment alone (the S-0041 audit measured: judgment-alone produced zero captures across S-0033 → S-0040). When the answer is no, no drawer is written and the session proceeds. When the answer is yes, the drawer is written here so the capture is durable before the archive moves at step 13.

**Diary write is mechanically enforced as of S-0078** (per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md)). The previous posture (a `diary_skipped: 1` self-recorded soft-warn) was load-bearing in name only — Issue #27 confirmed that 12 of 16 Phase 5 routine sessions silently skipped the diary write AND skipped the self-record, leaving the persistent-warn surface inert. Now `validate.py --final-check` (step 3) reads `engine_memory_activity.diary_write_calls` from `current.json` and hard-fails (`engine_memory_diary_write_skipped`) if zero. The previous `diary_skipped` field was renamed to `engine_memory_diary_write_skipped` across existing archives via `engine/tools/migrate_diary_skipped_archive_field.py`.

**Acknowledgement-token escape hatch.** Legitimate edge cases exist (MCP server unreachable; routine session that early-exits with nothing meaningful to reflect on; fresh repo). The AI bypasses the hard-fail by writing a one-line acknowledgement into `outcome_summary` of `current.json` BEFORE the step-3 validate call: `engine_memory_unavailable_acknowledged: <one-line reason>`. The validator scans for the token; if present, the hard-fail downgrades to a soft-warn (`engine_memory_diary_write_acknowledged_skip`) — which still participates in the 3-of-5 escalation per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). For routine sessions the validator emits `engine_memory_diary_write_skipped_routine` instead of hard-failing and appends an entry to `engine/session/diary_pending_index.json`; the recovery procedure is documented at [`routine-mode-operations.md`](routine-mode-operations.md) "Deferred diary recovery".

### 2. engine_memory activity rollup (per ADR 0091, S-0192)

Run `python3 engine/tools/scan_engine_memory_activity.py`. The tool reads `engine/session/current_engine_memory.jsonl` (per-session telemetry written by `engine/tools/hooks/post-engine-memory-tool-use.sh` on every `mcp__engine_memory__*` MCP call), counts calls per tool, and writes the structured `engine_memory_activity` field into `engine/session/current.json`. Must run AFTER step 1 (so the diary-write and pushback/lesson-capture calls are counted) and BEFORE step 3 (so `validate.py --final-check` sees the complete field).

Idempotent — re-running overwrites the rollup. Absence of the JSONL file (no engine_memory calls fired this session) writes a zero-count rollup; the audit's adoption check interprets zero counts per the ADR's severity rules.

### 3. Audit pass

Run `python3 engine/tools/validate.py --final-check` from the repo root. The `--final-check` flag includes the engine_memory adoption checks per [ADR 0091](../adr/0091-engine-memory-substrate-sqlite-fts5.md) (S-0192) — the two soft-warns (`engine_memory_boot_query_skipped`, `engine_memory_diary_read_skipped`) and the hard-fail (`engine_memory_diary_write_skipped`, with the acknowledgement-token escape hatch). During the cutover window (S-0192 → S-0193) the legacy `mempalace_*` adoption checks per superseded ADR 0056 also fire from `validate_mempalace_adoption()` as defense-in-depth; they retire at S-0193. Because step 1 wrote the diary and step 2 rolled the activity field, this pass sees the diary write truthfully and does not false-fire.

Resolve any hard-fails — these are blocking by default in the pre-commit hook anyway, so reaching shutdown means the working tree should already be clean of hard-fails. If somehow a hard-fail surfaces (e.g., a file referenced in CROSS_REFERENCES.md that you intended to create but didn't), fix it before continuing.

Soft-warns are not blocking but must be recorded — they feed health-check telemetry. Note the per-category counts; you'll write them into `outcome_summary_soft_warns` at step 11.

### 4. Spot-check

For every artifact created or modified in this session, ask:

- **Confidence labels honest?** If a doc claims "settled," it's settled; if it's a working hypothesis, it says so. Don't overclaim certainty.
- **Type framing correct?** A reference doc reads as reference (declarative). A procedure reads as procedure (imperative). A decision record reads as a decision (Status field, Context, Consequences).
- **Cross-references resolve?** Every link or `path/file.md` mention points at something real. Particularly important for `docs/CROSS_REFERENCES.md` — the validator catches missing files but not wrong paths to existing ones.
- **Voice consistent with the file's purpose?** Operations docs are AI-facing; design docs are human-and-AI-facing; ADRs are decision-of-record.

The audit catches structural mistakes. The spot-check catches judgment mistakes.

### 5. Cold-context review pass (sessions that modified tracked Python under engine/ or SQL under product/seed-graph/migrations/)

Layer 3 of the universal expression contract per [ADR 0039](../adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Two pattern rows currently carry a Layer 3 cold-review trigger: Python/engine per [ADR 0038](../adr/0038-expression-contract-for-ai-authored-code.md) + [`code-discipline.md`](code-discipline.md), and SQL/migrations per [`migration-discipline.md`](migration-discipline.md). Sessions that did not modify either of those scopes skip this step. Sessions that modified both run both branches.

#### Python/engine branch

Identify the modified Python files in this session: `git diff --name-only <session-base>..HEAD | grep -E '^engine/.*\.py$'`. The session-base is the commit that immediately precedes the eager-claim — typically `git merge-base origin/main HEAD~`, or simply `HEAD~N` where N is the number of commits this session has produced.

Launch a sub-agent (Explore type) with no session context. The agent's brief is the cold-review prompt template in [`code-discipline.md`](code-discipline.md) — the agent reads each modified file's contract block, then reads the implementation, then reports per-file whether the code matches its contract or where the contract and code drift apart. Cite specific contract claims and code lines for each mismatch.

#### SQL/migrations branch

Identify the modified SQL files in this session: `git diff --name-only <session-base>..HEAD | grep -E '^product/seed-graph/migrations/.*\.sql$'`.

Launch a sub-agent (Explore type) with no session context. The agent's brief is the cold-review prompt template in [`migration-discipline.md`](migration-discipline.md) — the agent reads each modified migration's contract comment block, then reads the migration body, then reports per-file whether the body matches the contract and whether the migration honors the discipline (CASCADE on FKs to users(id), RLS-enable on public.* tables, CHECK constraint shape on enum-modeled columns, transaction wrap, JSONB constraint shape, idempotency).

#### Recording findings

Record findings from each branch in `engine/session/current.json`'s `outcome_summary`:

- **All matches.** Append `"cold-review pass (<branch>): <N> file(s), all match contract."` to `outcome_summary`.
- **Mismatches found.** Append the per-file findings verbatim, then a one-sentence response per finding distinguishing addressed-in-session from deferred-to-follow-up. Material drift that warrants follow-up — code or SQL that contradicts a contract block in a way the session did not catch — surfaces as a new HANDOFF.md entry or a follow-up-task line in `outcome_summary` so the next session sees it.

The pass is fresh-eyes by construction: the sub-agent has no memory of the authoring session's premises and so cannot share its blind spots. The mechanism targets the compound-drift failure mode — a wrong premise built upon by internally-consistent artifacts that pass automated checks authored against the same premise. Cold-review surfaces premise drift; lint/type/test/SQL-gate checks do not.

### 6. Update `STATE.md`

Edit the `## Current` table:

- **Last build session** → `S-<this session's id> (<date>) — <one-line summary>`.
- **Last commit on main** → leave the placeholder pointing at `git log --oneline -1 main`; the next session reads it live.
- **Trim policy (size guard)**: delete every row labeled "Prior build session" or "Prior-prior build session" from the table — keep only the new "Last build session" row. These rows duplicate ENGINE_LOG.md; accumulating them without a drop bound caused STATE.md to exceed the MCP tool read limit at S-0069. If STATE.md still exceeds ~20,000 tokens after the row drop, also collapse the "Current phase" cell to the current-state summary form: `Phase N — <description> (in progress/closed; S-XXXX → present). N/M tasks complete. K ADRs — J Accepted + L Superseded — A engine + B product. Full session history in ENGINE_LOG.md.`

Edit the `## Next session work item` block:

- Replace with the next session's scope. Be concrete: what files get authored, what files get retired, what success looks like. The next session reads this cold; it should be sufficient.
- If this session uncovered new work that should sit before what was previously next, surface it here and update `ROADMAP.md` if the change crosses a phase boundary.

### 7. Update `ENGINE_LOG.md`

`ENGINE_LOG.md` is the dated-narrative layer for material engine changes — the renamed `CHANGELOG.md` per [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md). The `CHANGELOG.md` filename is reserved for future learner-visible product release content (first entry at Phase 9); session shutdowns write here.

Under `[Unreleased]`, add entries by category (Added / Changed / Removed / Deprecated / Fixed / Security). Material-change criteria — log it if it meets *any* of these:

- New top-level file or directory.
- New or removed ADR.
- New or removed entry in `docs/`.
- Breaking change to a schema, predicate, or commitment.
- New session-protocol behavior (hooks, commands, register fields).
- New or changed ENGINE_LOG-tracked design commitment.

Skip these — not material:

- In-session commit messages on application code (Phase 9+; tracked in git only).
- Typo fixes, formatting cleanups, link repairs.
- Minor wording revisions inside an existing doc.

For SQL migrations: log the session-level filenames as authored (e.g., `0001_users.sql`, `0002_nodes.sql`). Supabase migration version tracking is separate and automatic — `supabase db push` records its own deployment-version metadata in the dev DB. The two are orthogonal; ENGINE_LOG records what the session wrote, Supabase records what got applied where.

At the next release tag (e.g., `0.1.0` at Phase 0 close), the `[Unreleased]` block gets promoted to a dated section.

### 8. Side-discovery audit

Run `python3 engine/tools/audit_side_discoveries.py` from the repo root. The script scans this session's commit messages (range `<eager-claim-SHA>..HEAD`, computed from the eager-claim subject pattern) for follow-up markers — `flagged`, `follow-up`, `follow up`, `TODO`, `FIXME`, `deferred`, `noted for`, `future session`, `next session`, `pending`, `out of scope` — and matches each hit against the `side_discoveries` field in `engine/session/current.json`. Markers preceded within ~12 chars by `no` / `not` / `nothing` / `no longer` are filtered as obvious negations.

The pattern this addresses: side-discoveries the AI flags during a session land in commit messages or end-of-session prose ("flagged for follow-up") and vanish without a mechanical surface that triggers future action. Naming an explicit disposition for each match forces the AI to either route the discovery to the right surface (`engine/scheduled_audits.json`, `product/docs/tensions.md`, HANDOFF.md, an inline fix-commit) or explicitly accept it as a no-op with stated reasoning. Authored at S-0033 per [HANDOFF.md](../../HANDOFF.md) Item 2.

If any marker lacks a disposition, the script exits 2 and prints `commit / marker / surrounding-context` to stderr. Resolve by editing `current.json`'s `side_discoveries` list — append one entry per undispositioned marker:

```json
{
  "commit": "<7-char SHA prefix>",
  "marker": "<phrase that matched, lowercased>",
  "disposition_type": "scheduled_audit | tension_oq | handoff_section | addressed_inline | acceptable_no_action",
  "disposition_ref": "<id, OQ name, section heading, fix-commit SHA, or empty>",
  "reasoning": "<optional; required for acceptable_no_action>"
}
```

Re-run the script. Iterate until exit 0. The total count of dispositions (per type) feeds into the diary entry at step 1 and `outcome_summary` at step 11.

If a marker truly is a false positive (e.g., literal text inside a code-discipline doc like "this used to say TODO"), use `acceptable_no_action` with a short reasoning. The `acceptable_no_action` path is the documented escape hatch — using it is normal, not a sign of laziness.

The audit is hard-fail by design: undispositioned markers block the close, mirroring the mechanical-surface discipline the audit itself instantiates. The script does not introduce a new soft-warn category.

#### 8a. HANDOFF-disposition audit

Run `python3 engine/tools/audit_handoff_dispositions.py` from the repo root. The script diffs `HANDOFF.md` across this session's range (`<eager-claim-SHA>^..HEAD`) and finds every newly-added section header (`+## ...` in the unified diff). For each, it requires a `**Disposition:**` line in the section body matching one of four accepted forms:

- `fixed-in-session @ <SHA>` — the bug or finding the section names was fixed in this session; the SHA points at the resolving commit.
- `deferred-with-user-confirmation` — the user explicitly confirmed deferral via a prior chat turn (the diary or `working_on` field ideally name when).
- `out-of-scope` — the entry documents a pattern, anti-pattern, or recovery procedure that's structurally not a fix-now item.
- `not-actionable` — informational only; no fix exists or none warranted given current state.

The pattern this addresses: the AI finds a bug whose fix is in context, writes a HANDOFF.md prose entry naming the bug + the proposed fix for a future session, and never applies the fix in the current session — the deferral pattern. Authored at S-0036 per CLAUDE.md "Default to fix-in-context."

If any new section is missing or has an unrecognized disposition, the script exits 2 and the per-section detail goes to stderr. Resolve by **applying the fix in this session and updating the disposition to `fixed-in-session @ <commit-SHA>`**, OR — if deferral is genuinely warranted (substantial scope, contract change, budget cap reached) — flag the user, get confirmation, and use `deferred-with-user-confirmation`.

The audit also runs from the pre-commit hook in `closing` mode (the close commit cannot land if any new HANDOFF section is undispositioned), so this manual invocation is a way to catch the issue before staging. Hard-fail by design.

The audit ignores edits to existing sections — only newly-added section headers are scanned. The retrofit cost on pre-S-0036 entries would be prohibitive; the discipline applies forward only.

#### 8b. Archive structured-fields audit

Run `python3 engine/tools/audit_archive_structured_fields.py` from the repo root. The script reads `engine/session/current.json` and validates that the `outcome_summary_soft_warns` key is present and non-null. Empty dict (`{}`) is permitted — it's the legitimate shape for a session whose `validate.py` emitted no warnings.

Authored at S-0055 per [Issue #13](https://github.com/StarshipSuperjam/paideia/issues/13). The S-0052 health-check audit found that S-0043 through S-0047 (five consecutive archives) lacked the field entirely — not empty, the JSON key was absent. [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s persistent-warn surface counts categories *inside* the field; it cannot detect a missing field, only count occurrences within it. So a session that forgets to write the field is invisible to the surface for the next 5 sessions. This audit fires at session-shutdown after the structured field is written and before the archive lands.

If the field is missing or null, the script exits 2 and the close is blocked. Resolve by populating `outcome_summary_soft_warns` from the current session's validate.py output (the field shape is `{category_name: count}`); if the session genuinely had zero warnings, write `{}` rather than `null` or omitting the key.

The audit also runs from the pre-commit hook in `closing` mode against the staged archive content (`git show :engine/session/archive/S-NNNN.json | python3 ... --from-stdin`), so this manual invocation is a way to catch the issue before staging. Hard-fail by design.

Optional secondary check: if the field is present but empty (`{}`) AND the session had ≥3 commits, the audit emits a stderr advisory pointing at the likely "wrote empty by default" pattern. The advisory is informational; the field is technically valid so the audit still exits 0.

### 9. Scope-delivery audit (per ADR 0049)

Before the outcome_summary is written, the AI is prompted explicitly with the literal text:

> *Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?*

The AI's structured answer is written to `engine/session/current.json` as the `scope_delivery` field:

```json
"scope_delivery": {
  "delivered": true,
  "user_confirmed_changes": false,
  "explanation": "Yes — all four interventions plus telemetry landed cleanly."
}
```

`delivered: false` triggers the `scope_delivery_non_yes` soft-warn at the close-commit's validate.py run, regardless of `user_confirmed_changes`. The warn is signal for cross-session aggregation (the persistent-warn surface escalates 3-of-5 firings into the boot-time multi-session erosion signal in `session-start.sh`), not punishment. Even justified scope changes leave a trace so the trend is visible.

The `user_confirmed_changes` flag is captured for future audit but does not affect the soft-warn. When `delivered: false` and `user_confirmed_changes: true`, the entry passes the audit but the warn still fires. When `delivered: false` and `user_confirmed_changes: false`, the same warn fires; the user's review of the archive will surface the unjustified deviation.

The prompt is asked at every shutdown — not a heuristic for the AI to apply by judgment alone. Same discipline as the `pushback`/`lesson` capture check at step 1 (S-0041 audit measured judgment-alone produced zero captures across eight sessions; explicit prompt is the load-bearing surface).

### 10. Defer-handle audit (per ADR 0049 Decision 6, S-0100 amendment / Issue #54)

After the scope-delivery audit at step 9, before `outcome_summary` fill at step 11, the AI is prompted explicitly with the literal text:

> *Did your `outcome_summary` use any hedge-shaped phrasing — references to "future session", "next session will", "revisit when", "deferred indefinitely", or similar? If yes, declare `next_session_handle` as either an Issue number (`#NN`), a specific session ID (`S-NNNN`), or explicit `null` (when the phrasing is intentional forward-pointer prose, not a deferral).*

The answer is written to `engine/session/current.json` as the `next_session_handle` field. Three valid values:

- `"#<num>"` — GitHub Issue number tracking the deferred fix.
- `"S-<NNNN>"` — specific scheduled session that picks up the work (4-digit pad). Either an existing archive OR the next-claim slot in `register_state.json`.
- `null` — explicit "no defer" when hedge phrasing in `outcome_summary` is intentional forward-pointer prose (e.g., "the next routine session will resume from the same target" — true statement, not a deferral).

The `validate_outcome_summary_unhandled_defer` audit at `--final-check` enforces the contract per the disposition table in [`tools-validate-interpretation.md`](tools-validate-interpretation.md). The primary positive category `outcome_summary_unhandled_defer` fires when hedge prose appears with the field absent from the JSON entirely (the "you forgot to declare" case). Three verification categories diagnose handle errors: `next_session_handle_unknown_issue` (Issue verified missing via `gh issue view`), `next_session_handle_unknown_session` (session ID matches no archive and is not the next-claim slot), `next_session_handle_malformed` (string doesn't match `#<num>` or `S-<NNNN>`).

Closes Pushback Cluster A from the S-0097 audit. The user adjudicated structured-field formulation over keyword-scan-only at S-0098 — anchors on a positive contract ("must declare the handle") rather than a negative one ("must not use these words"). False positives become "you forgot to declare" rather than "your prose tripped a regex." Two canonical instances captured as `[pushback]`-prefixed drawers in `paideia/problems` (S-0071 "correctable in any future session via a JSON edit"; S-0048 "preserved for manual review").

The prompt is asked at every shutdown — same discipline as step 9; explicit prompting is the load-bearing surface for both deferral mechanisms.

### 11. Fill `session/current.json` `outcome_summary` and `outcome_summary_soft_warns`

`outcome_summary` is ~50 words of prose. What got done, anything noteworthy for the next session, what tradeoffs surfaced. Example shape:

```
"outcome_summary": "Procedural layer landed: CLAUDE.md + 11 operations docs + MISSION.md + CROSS_REFERENCES.md. Hooks wired for MemPalace capture. CONTEXT.md retired. validate.py: 0 hard-fails, 2 soft-warns (expected_future_file_missing for adr/, will resolve in S-0003). Next: S-0003 ADR collection."
```

Honest summaries beat flattering ones — health-check trend analysis and the next session's boot procedure both depend on them.

`outcome_summary_soft_warns` is the structured trend canon per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). **Per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md) (S-0035 onward), the field is computed by aggregating across every `validate.py` invocation recorded in this session's `engine/tools/validate-history.jsonl` entries — per-category max-count.** This closes a gap in the prior "final validator run only" rule: a soft-warn that fires at boot (e.g., `chromadb_palace_health` under suspicion-level corruption) but resolves before shutdown would otherwise be dropped from the archive, defeating the cross-session 3-of-5 surface. Aggregating across all session invocations means boot-only firings still accumulate.

The boot-only firing case isn't theoretical: the SessionStart hook runs `validate.py --health-probe-only` per ADR 0045, which writes its own validate-history.jsonl entry independent of the final pre-commit run. Without the aggregation change, that entry's findings would never reach the archive.

Shape:

```json
"outcome_summary_soft_warns": {
  "expected_future_file_missing": 0,
  "adr_missing_status": 0,
  "adr_index_inconsistent": 0,
  "cross_reference_broken": 0,
  "engine_log_format": 0,
  "state_format": 0,
  "superseded_adr_currency": 0,
  "adr_back_reference_orphan": 2,
  "adr_consequences_deliverable_audit": 0,
  "chromadb_palace_health": 0,
  "repo_config_health": 0,
  "skill_layer1_parity_drift": 0,
  "mempalace_hnsw_status_suspect": 0,
  "engine_memory_zero_citations_after_search": 0,
  "engine_memory_diary_write_acknowledged_skip": 0,
  "engine_memory_diary_write_skipped_routine": 0,
  "undeclared_predicate": 0,
  "attribute_shape_inconsistency": 0,
  "missing_rigor_score": 0,
  "render_readiness_violation": 0,
  "synthetic_review_queue": 0,
  "orphan_leaf": 0,
  "suspicious_cross_domain_ratio": 0,
  "engine_memory_boot_query_skipped": 0,
  "engine_memory_diary_read_skipped": 0,
  "engine_memory_diary_write_skipped": 0,
  "engine_memory_diary_write_skipped_routine": 0,
  "engine_memory_diary_write_skipped_substrate_intermittent": 0,
  "engine_memory_diary_write_acknowledged_skip": 0,
  "mempalace_substrate_at_close": 0,
  "mempalace_retired_surface_used": 0,
  "outcome_summary_unhandled_defer": 0,
  "next_session_handle_unknown_issue": 0,
  "next_session_handle_unknown_session": 0,
  "next_session_handle_malformed": 0
}
```

All known soft-warn categories appear in the block, even with zero counts; absent keys signal "this category did not exist at this session's close" rather than "this category fired zero times." The boot-time persistent-warn surface (per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md)) reads this field across the last 5 archives and surfaces categories appearing in 3-or-more. `skill_layer1_parity_drift` is the Skill ↔ Layer-1 procedure-parity category per [ADR 0089](../adr/0089-skill-layer1-parity-validator-check.md). The `engine_memory_*` categories are emitted by `validate.py --final-check` per ADR 0091 (S-0192) reading `engine_memory_activity` written by `scan_engine_memory_activity.py` at step 2. The legacy `mempalace_*_skipped`, `mempalace_substrate_at_close`, `mempalace_retired_surface_used`, and `mempalace_hnsw_status_suspect` categories fire alongside during the cutover window (S-0192 → S-0193) and retire at S-0193 alongside the MemPalace package itself. `engine_memory_diary_write_skipped_routine` plays the same routine-protection role for the new substrate as `mempalace_diary_write_skipped_routine` did for the old: when fired, the validator appends an entry to `engine/session/diary_pending_index.json` so the next boot's SessionStart hook surfaces the deferred-diary count and the user can run the recovery procedure documented at [`routine-mode-operations.md`](routine-mode-operations.md) "Deferred diary recovery". `chromadb_palace_health` and `repo_config_health` are the shared-state probe categories per ADR 0045 — they fire on either suspicion or hard-broken state at any validator invocation during the session. The seven graph-audit categories (`undeclared_predicate` through `suspicious_cross_domain_ratio`) added at S-0037 per [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) and the [Phase 4 build-readiness gate](../build_readiness/phase_4_graph_validation.md) — they fire when `SUPABASE_DB_URL` is set and the audit runs against the live DB; sessions without DB connectivity record zeros (the audit skips entirely, recording `graph_audit_skipped` in `checks_run` rather than firing any category).

**Aggregation procedure (per ADR 0045):**

1. Determine session-base SHA: `git merge-base origin/main HEAD` (the commit immediately before the eager-claim).
2. Read `engine/tools/validate-history.jsonl`. Filter entries whose `session_id` matches this session's S-NNNN (or whose timestamp falls between session-base time and now if `session_id` is "outside-session").
3. For each soft-warn category appearing in any filtered entry's `soft_warns` dict, take the max count across all entries.
4. Per ADR 0091 (S-0192), the three `engine_memory_*_skipped` categories — and the legacy `mempalace_*_skipped` categories that fire alongside during the cutover window — come from `validate.py --final-check`. They are part of the validate-history.jsonl entries from step 1, not separate session-state. The aggregation procedure picks them up automatically along with all other validator categories.
5. Ensure every known category from the catalog appears with at least 0; absent keys carry the documented "category didn't exist" semantic.

### 12. Scan drawer citations (per ADR 0056 S-0093 amendment, Issue #39)

After `outcome_summary` is filled at step 11 AND the diary write completed at step 1, run [`engine/tools/scan_mempalace_citations.py`](../tools/scan_mempalace_citations.py) from the repo root. The tool scans `outcome_summary`, today's diary entry (via `mempalace.mcp_server.tool_diary_read`), and commit messages from `git log <eager-claim-sha>..HEAD --format=%B` for three citation patterns (drawer IDs, S-NNNN archive references, tag-named references). Writes the nested `mempalace_citations` block under the existing `mempalace_activity` field in `engine/session/current.json`. Idempotent.

**S-0192 cutover window.** The citations scan currently writes to the `mempalace_activity.mempalace_citations` sub-block; the `mempalace_zero_citations_after_search` soft-warn continues firing. The sibling scan tool `scan_engine_memory_citations.py` lands at S-0193 (T1-E) and writes `engine_memory_activity.engine_memory_citations`. Until then, the `engine_memory_zero_citations_after_search` soft-warn fires whenever `engine_memory_activity.search_calls > 0` because no scan populates the citations block — that's the expected cutover-transient behavior. After S-0193 both layers consolidate on the engine_memory path.

### 13. Archive the claim

```bash
mv session/current.json session/archive/S-<NNNN>.json
```

Add a `closed_at` timestamp and update `status` to `closed` (or `closed_partial` if you hit a budget cap mid-work):

```json
{
  "id": "S-<NNNN>",
  "started_at": "...",
  "closed_at": "<ISO-8601 UTC>",
  "status": "closed",
  ...
  "outcome_summary": "..."
}
```

Update `session/register_state.json`:

```json
{
  "next_id": "<unchanged from claim>",
  "last_claimed": "S-<NNNN>",
  "current_status": "closed"
}
```

### 14. Final commit + main FF + push

Commit message uses Conventional Commits with the session ID:

```
<type>(<scope>): <summary>

S-<NNNN> close: <one-line outcome>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Then push the close commit via the build-mode lifecycle wrapper (per [ADR 0076](../adr/0076-build-mode-lifecycle-push-wrapping.md)):

```bash
python3 engine/tools/build_lifecycle_push.py close
```

The wrapper mechanically shape-verifies HEAD (close subject pattern, archive/S-NNNN.json created, current.json deleted, register_state.json flips `in_progress` → `closed`) before pushing. On success it performs the parent-side FF best-effort. Exit codes 0 / 2 / 3 / 4 / 5 per the wrapper's CLI contract. The wrapper bypasses the harness's "Default Branch Push" classifier via subprocess-spawned git from a permitted python tool — same pattern as `routine_lifecycle_push.py` (ADR 0054) for routine sessions.

No per-push confirmation — the `/start-engine` invocation at session boot already authorizes the shutdown push (per `session-build-lifecycle.md` Push policy). After the push completes, the durable close has landed on `origin/main`; the session is fully closed.

### 15. Close-side worktree preservation (per ADR 0076 Amendment v2, S-0143)

**The closing session's worktree is NOT swept at close.** It survives close push + parent FF + archive so the user can return to that worktree for follow-up discussion, in-tree review of the session's deliverables, or out-of-scope edits. Both [`engine/tools/routine_worktree_sweep.py`](../tools/routine_worktree_sweep.py) and [`engine/tools/sweep_worktrees.sh`](../tools/sweep_worktrees.sh) carry a `caller's-own-worktree` pre-flight that refuses sweep when invoked against the caller's current working directory — defense-in-depth in case any consumer accidentally targets it at close.

Accumulated prior-session worktrees are collected at the **next session's boot** by the bulk-sweep wiring in [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh), which invokes `sweep_worktrees.sh --apply --quiet` between the concurrent-session collision check and the shared-state health probe. The bulk utility's conservative pre-flight (`claude/*` branch + clean working tree + branch merged into `main`) ensures only safely-removable worktrees are reaped; dirty or unmerged worktrees are preserved with a one-line stderr note naming the path and reason. The full multi-line preserve-report (path + branch + merged/ahead/behind + dirty files + last commit + actionable guidance) is available on demand by running `bash engine/tools/sweep_worktrees.sh` (dry-run, no `--quiet`).

**Liveness-marker preservation (per ADR 0076 amendment, S-0157 / [Issue #120](https://github.com/StarshipSuperjam/paideia/issues/120)).** `session-start.sh` writes a `session-live` marker into each worktree's private git dir (`.git/worktrees/<name>/session-live`) at every boot — *before* the eager-claim ritual, so even a plan/exploration-mode session that never claims a slot carries the marker. Both `sweep_worktrees.sh` and `routine_worktree_sweep.py` preserve any worktree whose marker mtime is within a 24h freshness window. This closes the gap the caller-self check does not cover: a sibling session's boot-time sweep would otherwise reap a *bystander* live worktree that is `claude/*` + clean + merged (a pre-eager-claim session has made no commits yet, so it matches every reap criterion). A genuinely abandoned worktree's marker goes stale after 24h and the worktree becomes reapable again.

If a future session genuinely needs to sweep its own worktree at close (e.g., a one-shot maintenance session whose worktree should not survive), the opt-in path is `python3 engine/tools/routine_worktree_sweep.py --allow-caller-self` — reserved for test fixtures and manual recovery; production close ceremonies must not set the flag.

Pre-S-0143 history: ADR 0076's original Amendment (S-0142) wired build-mode close to invoke `routine_worktree_sweep.py` on its own worktree (the S-0142 worktree was the first natural exercise). That invocation destroyed the closing session's working folder before the user could follow up on the session's deliverables; the user could not return to the worktree to ask clarifying questions, since the directory was gone. ADR 0076 Amendment v2 at S-0143 reverses the close-side invocation and shifts cleanup to next-session boot.

## Updating design docs during a session

Design docs in `docs/` (not the operations procedures, the project-content docs: `architecture.md`, `pedagogy.md`, `tensions.md`, etc.) follow a maintenance protocol that applies throughout the session, not just at shutdown:

- **Strong idea clarified or strengthened** → add to the relevant downstream file. If it rises to a core commitment, surface it in `docs/MISSION.md` (Strong working commitments) and `ROADMAP.md` (Strong working commitments referenced throughout).
- **New tension** → add to `docs/tensions.md` with enough context for a future session to understand the stakes. Date the entry.
- **Tension resolved** → move from `docs/tensions.md` to the relevant downstream file with a "Resolved: YYYY-MM-DD" line. Don't delete the entry from `tensions.md` — re-mark it `Resolved` so the historical record is preserved in place.
- **New commitment + reasoning** → both the *what* and the *why* land in an ADR per [`adr-authoring.md`](adr-authoring.md). The conversational story lands in engine_memory under `room='decisions'` with `tag='decision'` (per [`engine-memory-conventions.md`](engine-memory-conventions.md)). The transitional `design-reasoning.md` file (used during S-0001 / S-0002) retired at S-0003 close — its 8 entries became ADRs 0013, 0014, 0015, 0017, 0018, 0019, 0020, 0021.
- **Idea surfaces but isn't ready for a file** → file a GitHub Issue with the `enhancement` label per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md). (Pre-S-0083 the project captured these in `product/docs/ideation.md`; that file retired at S-0083 per Issue #29 once the function had structurally migrated to Issues.)
- **Deprecated files** → absorption + delete pattern. (a) Absorb the reasoning into the right downstream artifact (an ADR for structural decisions; a doc revision for content; an engine_memory `decisions`-room drawer for the conversational story). (b) `git rm` the original. Recovery is via git tag (e.g., `pre-foundation-v0.0.0`) or `git show <commit>:<path>`. Update any references in `docs/CROSS_REFERENCES.md` and consuming docs in the same commit. *Escape hatch:* if a retired structural artifact (a schema, graph snapshot, migration export) would benefit from in-tree side-by-side comparison with a current artifact — and that need is referenced from a current ADR or doc — file it as `_archive/<descriptive-slug>/MANIFEST.md` + the artifact (one-off, not the default). The S-0003 retirement of `design-reasoning.md` and the S-0002 retirement of `CONTEXT.md` are absorption + delete examples; neither was archived because the reasoning was fully redistributed.
- **Dead ends** → don't record. Design docs are forward-looking; engine_memory `exploration` drawers carry the dead-end reasoning if anyone ever needs it.
- **Note dates only where the date is the artifact's content.** An ENGINE_LOG entry's date, a Resolved-tension marker's `Resolved: YYYY-MM-DD`, an ADR's `Date:` header field — these are the artifact doing its job. Inside body prose of governed files (per [`document-voice.md`](document-voice.md)), revision dates and session-attribution markers like `**Added: YYYY-MM-DD (S-NNNN)**` migrate to ENGINE_LOG and git history; the body describes present state, not the path the file took to it.

These updates each generate an ENGINE_LOG entry per the material-change criteria above.

## Partial closure (budget cap reached)

If a session hits its budget cap (per CLAUDE.md guidance) mid-work:

1. Halt at the next sensible boundary (don't leave the working tree in an unparseable state).
2. Run validate.py. Address any hard-fails.
3. Fill `outcome_summary` with what got done **and** what remains. Mark status `closed_partial`.
4. Update STATE.md's next-session work item to the unfinished portion plus context for the picking-up session.
5. Archive, commit (`<type>(<scope>): <summary> — partial close`), FF, push.

The next session picks up cleanly from STATE.md without re-deriving where things left off.

## Recovery (interrupted shutdown)

A clean close runs steps 1–14 in sequence. If the session crashes, hits a network error, or otherwise halts mid-shutdown, the observable state determines the recovery path.

### Pre-recovery sanity check (verify the prior close did not already land)

**Before invoking any recovery scenario below, verify the prior close did not already land upstream.** A fresh worktree opened immediately after a prior session closed cleanly may show post-eager-claim state (current.json present, register status in_progress, STATE.md pre-close) because the worktree's checked-out files reflect a commit that pre-dates the close — not because the close was halted. Running recovery on a stale checkout produces real corruption from a phantom problem (re-archiving an already-archived current.json, re-editing STATE.md atop the close narrative, duplicate ENGINE_LOG entries). The discovery surface that prompted this check was the post-S-0033 stale-checkout boundary case (HANDOFF.md, retroactively dispositioned at S-0041).

Run:

```bash
git fetch origin && git log --oneline origin/main -10
```

If a `chore(session): close S-NNNN` commit for the slot named in `register_state.json`'s `last_claimed` field is visible upstream, the prior session closed cleanly and the local checkout is stale, not halted. Update the local checkout to that commit (`git pull --ff-only` if the branch tracks origin/main, or `git reset --hard origin/main` on a throwaway branch) and proceed with the *next* session's work; do not run recovery.

The asymmetry that justifies the check: a halted shutdown leaves no upstream close commit (the halt prevented the push); a stale checkout always has the upstream close commit. One `git log` check distinguishes them.

Concrete trigger condition for the stale-checkout shape: `register_state.json`'s `current_status: in_progress` AND `current.json` exists locally AND `git log origin/main` shows a `close S-<that-slot>` commit. The genuine halt shape is the same minus the third clause.

### Recovery scenarios

1. **Halted before step 13 (archive).** `current.json` present; `register_state.json` `current_status: in_progress`. Resume from step 1 — write the diary entry, run the activity rollup, run `tools/validate.py`, complete the spot-check, run the cold-review pass for any modified Python under engine/ and any modified SQL under product/seed-graph/migrations/, finish updating STATE.md / ENGINE_LOG, run the side-discovery audit, fill `outcome_summary`, then archive and final-commit.

2. **Halted between archive (step 13) and final commit (step 14).** `archive/S-<NNNN>.json` present, `current.json` absent, `register_state.json` `current_status: closed`. The archive move sits unstaged or staged in the working tree. Stage and commit the planned final commit; FF main; push.

3. **Halted after final commit, before FF + push.** Final commit exists locally; `git log origin/main..HEAD` shows it. FF main and push. No state edits required.

4. **Split state.** Both `archive/S-<NNNN>.json` and `current.json` present, or `register_state.json` `current_status` disagrees with which file exists. This shape should not occur with a clean close. Reconcile manually — read both files, identify which carries the fuller `outcome_summary`, do not delete either blindly. Escalate per [`escalation-criteria.md`](escalation-criteria.md) if the right reconciliation is unclear.

The recovery procedure is documented for completeness; it has not been exercised on a real interrupted close.

## See also

- [`session-build-lifecycle.md`](session-build-lifecycle.md) — open-of-session protocol.
- [`tools-validate-interpretation.md`](tools-validate-interpretation.md) — soft-warn category meanings.
- [`health-check.md`](health-check.md) — what telemetry feeds the periodic audit.
