---
name: session-shutdown-sequence
description: Close a Paideia build session — write the session diary, audit, spot-check, cold-context review pass for modified Python and SQL, update STATE.md and ENGINE_LOG.md, fill outcome_summary plus structured outcome_summary_soft_warns, archive current.json, final commit + FF + push. Invoke when substantive work has reached a commitable checkpoint and the session is ready to close.
disable-model-invocation: true
---

# session-shutdown-sequence

> Canonical executable form of the Paideia build-session close procedure. The Layer 1 source-of-truth prose lives at [`engine/operations/session-shutdown-sequence.md`](../../../engine/operations/session-shutdown-sequence.md) per [ADR 0036](../../../engine/adr/0036-expression-contract-for-inward-documents.md). This skill body is the procedural form per [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md). Updates flow doc → skill, never the reverse.

## When to invoke

At the end of every build session — once substantive work is at a commitable checkpoint, before the conversation ends. Run in order. Do not skip steps; the shutdown produces the durable artifacts that downstream sessions read.

## Sequence

> **Ordering note (per Issue #126, S-0163).** The MemPalace diary write (step 1), the activity rollup (step 2), and the pushback/lesson capture (within step 1) all run BEFORE the audit pass (step 3). Pre-S-0163 the audit ran first — which fired a false `mempalace_diary_write_skipped` / `mempalace_diary_write_skipped_routine` (the diary genuinely had not been written yet) and, for routine sessions, appended a false entry to `engine/session/diary_pending_index.json`. Sequencing the diary write + rollup before the audit means `validate.py --final-check` sees a complete `mempalace_activity` field and the diary-write check passes truthfully.

### 1. Write session diary entry

Per [`mempalace-operations.md`](../../../engine/operations/mempalace-operations.md) "Project usage scope". The MemPalace diary carries the AI's first-person reflection on the session — distinct from `outcome_summary` (outcome-focused) and ENGINE_LOG (third-person artifact narrative). What surprised me, what I noticed but didn't act on, what feels load-bearing for the next session, where my judgment was uncertain.

Build sessions only. Default-mode (exploration) sessions skip — no slot, no formal close.

Call `mempalace_diary_write` with `agent_name: "claude"` (project convention). Content shape: 150-400 words, first person. Recommended structure:

- **What I worked on this session** — high-level enough to be findable by `mempalace_diary_read` at the next session's boot.
- **What surprised me** — premises that didn't hold, side-discoveries.
- **What I noticed but deferred** — observations next-session-relevant. (If actionable enough, also surface in HANDOFF.md or as a follow-up task in `outcome_summary`.)
- **Where my judgment was uncertain** — places I made a call I'd want a fresh-eyes review on.

After the diary write, run the **`pushback` / `lesson` capture check** (added at S-0041 per the second project health check audit's adoption-gap finding — the tags were defined at S-0032 with zero applications across S-0033 → S-0040 because the convention was too implicit to reach the AI's authoring loop without an explicit prompt). Ask explicitly:

- **Did this session produce a `pushback` moment?** (Verbatim exchange where AI surfaced an unnamed risk specifically, user heard it, conversation changed direction. Self-pushback also qualifies.) If yes, capture now via `mempalace_add_drawer` per the [`pushback` tag definition](../../../engine/operations/mempalace-tagging-conventions.md). Verbatim user framing + verbatim AI pushback + verbatim user acceptance + one-line summary.
- **Did this session produce a `lesson` candidate?** (Procedural failure with non-obvious cause + working fix; bug whose cause was obvious-once-named also qualifies if identification was the value.) If yes, capture now via `mempalace_add_drawer` per the [`lesson` tag definition](../../../engine/operations/mempalace-tagging-conventions.md). Failed approach + non-obvious reason + working fix + optional ADR/ops-doc pointers.

Both capture decisions are explicit yes/no asks at every shutdown — judgment-alone produced zero captures across the eight sessions between tag definition (S-0032) and the audit (S-0041). When the answer is no, no drawer is written. When yes, the drawer lands here so capture is durable before the archive moves at step 13.

**Diary write is mechanically enforced as of S-0078** (per ADR 0056). The previous posture (`diary_skipped: 1` self-recorded soft-warn) was load-bearing in name only — Issue #27 confirmed that 12 of 16 Phase 5 routine sessions silently skipped the diary write AND skipped the `diary_skipped` self-record, leaving the persistent-warn surface inert. Now `validate.py --final-check` (step 3) reads `mempalace_activity.diary_write_calls` from current.json and hard-fails (`mempalace_diary_write_skipped`) if zero. The previous `diary_skipped` field has been renamed to `mempalace_diary_write_skipped` across existing archives via `engine/tools/migrate_diary_skipped_archive_field.py`.

**Acknowledgement-token escape hatch.** Legitimate edge cases exist (MCP server unreachable; routine session that early-exits with nothing meaningful to reflect on; fresh repo). The AI bypasses the hard-fail by writing a one-line acknowledgement into `outcome_summary` of `current.json` BEFORE the step-3 validate call: `mempalace_unavailable_acknowledged: <one-line reason>`. The validator scans for the token; if present, the hard-fail downgrades to a soft-warn (`mempalace_diary_write_acknowledged_skip`) — which still participates in the 3-of-5 escalation per ADR 0042, so persistent acknowledged skips fire the same surface as unacknowledged ones.

### 2. MemPalace activity rollup (per ADR 0056, S-0078)

Run `python3 engine/tools/scan_mempalace_activity.py`. The tool reads `engine/session/current_mempalace.jsonl` (per-session telemetry written by `engine/tools/hooks/post-mempalace-tool-use.sh` on every `mcp__mempalace__*` MCP call), counts calls per tool, and writes the structured `mempalace_activity` field into `engine/session/current.json`. Must run AFTER step 1 (so the diary-write and pushback/lesson-capture calls are counted) and BEFORE step 3 (so `validate.py --final-check` sees the complete field).

Idempotent — re-running overwrites the rollup. Absence of the JSONL file (no MemPalace calls fired this session) writes a zero-count rollup; the audit's adoption check interprets zero counts per the ADR's severity rules.

### 3. Audit pass

Run `python3 engine/tools/validate.py --final-check` from the repo root. The `--final-check` flag includes the MemPalace adoption checks per ADR 0056 (S-0078) — the two soft-warns (`mempalace_boot_query_skipped`, `mempalace_diary_read_skipped`) and the hard-fail (`mempalace_diary_write_skipped` — with acknowledgement-token escape hatch). Because step 1 wrote the diary and step 2 rolled the activity field, this pass sees the diary write truthfully and does not false-fire.

Resolve any hard-fails — these are blocking by default in the pre-commit hook anyway, so reaching shutdown means the working tree should already be clean of hard-fails. The `mempalace_diary_write_skipped` hard-fail can be downgraded by adding `mempalace_unavailable_acknowledged: <reason>` to `outcome_summary` (see step 1's escape-hatch guidance) and re-running validate. If somehow a hard-fail surfaces (e.g., a file referenced in CROSS_REFERENCES.md that was intended but not authored), fix it before continuing.

Soft-warns are not blocking but must be recorded — they feed health-check telemetry. Note the per-category counts; write them into `outcome_summary_soft_warns` at step 11.

### 4. Spot-check

For every artifact created or modified in this session, ask:

- **Confidence labels honest?** If a doc claims "settled," it's settled; if it's a working hypothesis, it says so. Don't overclaim certainty.
- **Type framing correct?** A reference doc reads as reference (declarative). A procedure reads as procedure (imperative). A decision record reads as a decision (Status field, Context, Consequences).
- **Cross-references resolve?** Every link or `path/file.md` mention points at something real. Particularly important for `product/docs/CROSS_REFERENCES.md` and `engine/operations/cross-references.md` — the validator catches missing files but not wrong paths to existing ones.
- **Voice consistent with the file's purpose?** Operations docs are AI-facing; design docs are human-and-AI-facing; ADRs are decision-of-record.

The audit catches structural mistakes. The spot-check catches judgment mistakes.

### 5. Cold-context review pass (Python under engine/ or SQL under product/seed-graph/migrations/)

Layer 3 of the universal expression contract per [ADR 0039](../../../engine/adr/0039-universal-expression-contract-across-ai-authoring-patterns.md). Two pattern rows currently carry a Layer 3 cold-review trigger: Python/engine per [ADR 0038](../../../engine/adr/0038-expression-contract-for-ai-authored-code.md) + [`code-discipline.md`](../../../engine/operations/code-discipline.md), and SQL/migrations per [`migration-discipline.md`](../../../engine/operations/migration-discipline.md). Sessions that did not modify either scope skip this step. Sessions that modified both run both branches.

#### Python/engine branch

Identify modified Python files: `git diff --name-only <session-base>..HEAD | grep -E '^engine/.*\.py$'`. The `<session-base>` is the commit immediately preceding the eager-claim — typically `git merge-base origin/main HEAD~`, or simply `HEAD~N` where N is the number of commits this session has produced.

Launch a sub-agent (Explore type) with no session context. The agent's brief is the cold-review prompt template in [`code-discipline.md`](../../../engine/operations/code-discipline.md). The agent reads each modified file's contract block, then reads the implementation, then reports per-file whether the code matches its contract or where the contract and code drift apart. Cite specific contract claims and code lines for each mismatch.

#### SQL/migrations branch

Identify modified SQL files: `git diff --name-only <session-base>..HEAD | grep -E '^product/seed-graph/migrations/.*\.sql$'`.

Launch a sub-agent (Explore type) with no session context. Brief: the cold-review prompt template in [`migration-discipline.md`](../../../engine/operations/migration-discipline.md). The agent reads each modified migration's contract comment block, then reads the migration body, then reports per-file whether the body matches the contract and whether the migration honors the discipline (CASCADE on FKs to users(id), RLS-enable on public.* tables, CHECK constraint shape on enum-modeled columns, transaction wrap, JSONB constraint shape, idempotency).

#### Recording findings

Record findings in `engine/session/current.json`'s `outcome_summary`:

- **All matches.** Append `"cold-review pass (<branch>): <N> file(s), all match contract."` to `outcome_summary`.
- **Mismatches found.** Append the per-file findings verbatim, then a one-sentence response per finding distinguishing addressed-in-session from deferred-to-follow-up. Material drift that warrants follow-up — code or SQL that contradicts a contract block in a way the session did not catch — surfaces as a new HANDOFF.md entry or a follow-up-task line in `outcome_summary` so the next session sees it.

The pass is fresh-eyes by construction: the sub-agent has no memory of the authoring session's premises and so cannot share its blind spots. Cold-review surfaces premise drift; lint/type/test/SQL-gate checks do not.

### 6. Update `engine/STATE.md`

Edit the `## Current` table:

- **Last build session** → `S-<this session's id> (<date>) — <one-line summary>`.
- **Last commit on main** → leave the placeholder pointing at `git log --oneline -1 main`; the next session reads it live.

Edit the `## Next session work item` block:

- Replace with the next session's scope. Be concrete: what files get authored, what files get retired, what success looks like. The next session reads this cold; it should be sufficient.
- If this session uncovered new work that should sit before what was previously next, surface it here and update `ROADMAP.md` if the change crosses a phase boundary.

The `post-state-edit.sh` hook (per [ADR 0043](../../../engine/adr/0043-hook-architecture.md)) will surface a stderr reminder if either the "Last build session" row or the "Next session work item" block is empty or placeholder. The reminder is informational; the AI may proceed if the apparent emptiness is intentional (rare).

### 7. Update `engine/ENGINE_LOG.md`

`ENGINE_LOG.md` is the dated-narrative layer for material engine changes — the renamed `CHANGELOG.md` per [ADR 0037](../../../engine/adr/0037-engine-product-wall-and-changelog-rename.md). The `CHANGELOG.md` filename is reserved for future learner-visible product release content (first entry at Phase 9).

Under `[Unreleased]`, add entries by category (Added / Changed / Removed / Deprecated / Fixed / Security). Material-change criteria — log it if it meets *any* of these:

- New top-level file or directory.
- New or removed ADR.
- New or removed entry in `engine/operations/` or `product/docs/`.
- Breaking change to a schema, predicate, or commitment.
- New session-protocol behavior (hooks, commands, register fields, skills).
- New or changed ENGINE_LOG-tracked design commitment.

Skip these — not material:

- In-session commit messages on application code (Phase 9+; tracked in git only).
- Typo fixes, formatting cleanups, link repairs.
- Minor wording revisions inside an existing doc.

For SQL migrations: log the session-level filenames as authored. Supabase migration version tracking is separate and automatic.

### 8. Side-discovery audit

Run `python3 engine/tools/audit_side_discoveries.py` from the repo root. The script scans this session's commit messages (range `<eager-claim-SHA>..HEAD`) for follow-up markers — `flagged`, `follow-up`, `follow up`, `TODO`, `FIXME`, `deferred`, `noted for`, `future session`, `next session`, `pending`, `out of scope` — and matches each hit against the `side_discoveries` field in `engine/session/current.json`. Markers preceded within ~12 chars by `no` / `not` / `nothing` / `no longer` are filtered as obvious negations.

The pattern this addresses: side-discoveries the AI flags during a session land in commit messages or end-of-session prose ("flagged for follow-up") and vanish without a mechanical surface that triggers future action. Naming an explicit disposition for each match forces the AI to either route the discovery to the right surface (`engine/scheduled_audits.json`, `product/docs/tensions.md`, HANDOFF.md, an inline fix-commit) or explicitly accept it as a no-op with stated reasoning. Authored at S-0033 per [HANDOFF.md](../../../HANDOFF.md) Item 2.

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

If a marker truly is a false positive, use `acceptable_no_action` with a short reasoning. The audit is hard-fail by design: undispositioned markers block the close. The script does not introduce a new soft-warn category.

#### 8a. HANDOFF-disposition audit

Run `python3 engine/tools/audit_handoff_dispositions.py`. Diffs `HANDOFF.md` across this session's range and finds every newly-added section header. Each must carry a `**Disposition:**` line in one of four forms:

- `fixed-in-session @ <SHA>`
- `deferred-with-user-confirmation`
- `out-of-scope`
- `not-actionable`

The pattern this addresses: writing a HANDOFF.md prose entry for a bug whose fix is in context, instead of fixing inline. Per CLAUDE.md "Default to fix-in-context" — adding a HANDOFF entry that names a bug + names a fix without applying the fix is the deferral signal.

Hard-fail at exit 2 if any new section is missing or has an unrecognized disposition. Resolve by **applying the fix in this session** and using `fixed-in-session @ <SHA>`, or — if deferral is warranted — flag the user, get confirmation, and use `deferred-with-user-confirmation`. Also runs in pre-commit at `closing` mode so the close commit cannot land if dispositions are missing.

#### 8b. Archive structured-fields audit

Run `python3 engine/tools/audit_archive_structured_fields.py`. Validates that `engine/session/current.json` has `outcome_summary_soft_warns` present and non-null. Empty dict (`{}`) is permitted (clean session, no warnings).

Per [Issue #13](https://github.com/StarshipSuperjam/paideia/issues/13) (S-0055): defends [ADR 0042](../../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md)'s persistent-warn surface against silent field-absence lapses. The S-0052 audit found S-0043–S-0047 each lacked the field; the surface counts categories *inside* the field and cannot detect a missing key.

Hard-fail at exit 2 if absent or null. Resolve by populating from validate.py output (or `{}` if genuinely zero warnings). Also runs in pre-commit at `closing` mode against the staged archive content.

### 9. Scope-delivery audit (per ADR 0049)

Before outcome_summary, the AI is prompted explicitly with the literal text:

> *Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?*

Write a structured answer to `engine/session/current.json`:

```json
"scope_delivery": {
  "delivered": true,
  "user_confirmed_changes": false,
  "explanation": "Yes — all four interventions plus telemetry landed cleanly."
}
```

`delivered: false` triggers the `scope_delivery_non_yes` soft-warn at the close-commit's validate.py run, regardless of `user_confirmed_changes`. The warn is signal for cross-session aggregation, not punishment. The persistent-warn surface escalates 3-of-5 firings into the boot-time multi-session erosion signal in `session-start.sh`.

### 10. Defer-handle audit (per ADR 0049 Decision 6, S-0100 amendment / Issue #54)

After scope-delivery, before outcome_summary, the AI is prompted explicitly with the literal text:

> *Did your `outcome_summary` use any hedge-shaped phrasing — references to "future session", "next session will", "revisit when", "deferred indefinitely", or similar? If yes, declare `next_session_handle` as either an Issue number (`#NN`), a specific session ID (`S-NNNN`), or explicit `null` (when the phrasing is intentional forward-pointer prose, not a deferral).*

Write the answer to `engine/session/current.json` as the `next_session_handle` field:

```json
"next_session_handle": "#54"
```

Three valid values:
- `"#<num>"` — GitHub Issue number tracking the deferred fix.
- `"S-<NNNN>"` — specific scheduled session that picks up the work (4-digit pad). Either an existing archive OR the next-claim slot.
- `null` — explicit "no defer" when hedge phrasing in `outcome_summary` is intentional forward-pointer prose.

The `validate_outcome_summary_unhandled_defer` audit at `--final-check` enforces the contract per the disposition table in [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md). Closes Pushback Cluster A from the S-0097 audit (the user adjudicated structured-field formulation over keyword-scan-only at S-0098 — anchors on a positive contract "must declare the handle" rather than a negative "must not use these words").

The prompt is asked at every shutdown — same discipline as step 9. Judgment-alone produced zero captures across eight sessions in the S-0041 audit; explicit prompting is the load-bearing surface.

### 11. Fill `outcome_summary` and `outcome_summary_soft_warns`

`outcome_summary` is ~50 words of prose. What got done, anything noteworthy for the next session, what tradeoffs surfaced. Honest summaries beat flattering ones — health-check trend analysis and the next session's boot procedure both depend on them.

`outcome_summary_soft_warns` is the structured trend canon per [ADR 0042](../../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md). **Per [ADR 0045](../../../engine/adr/0045-shared-state-integrity-discipline.md) (S-0035 onward), aggregate across every `validate.py` invocation in this session's `engine/tools/validate-history.jsonl` entries (per-category max-count) — not just the final pre-commit run.** This catches boot-time probe firings (e.g., `chromadb_palace_health` under suspicion) that resolve before shutdown but should still register for cross-session 3-of-5 detection. Shape:

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
  "mempalace_boot_query_skipped": 0,
  "mempalace_diary_read_skipped": 0,
  "mempalace_diary_write_skipped": 0,
  "outcome_summary_unhandled_defer": 0,
  "next_session_handle_unknown_issue": 0,
  "next_session_handle_unknown_session": 0,
  "next_session_handle_malformed": 0
}
```

All known soft-warn categories appear in the block, even with zero counts; absent keys signal "this category did not exist at this session's close" rather than "this category fired zero times." The boot-time persistent-warn surface (per `soft-warn-lifecycle.md`) reads this field across the last 5 archives. `chromadb_palace_health` and `repo_config_health` are the shared-state probe categories per ADR 0045. `skill_layer1_parity_drift` is the Skill ↔ Layer-1 procedure-parity category per ADR 0089. The three `mempalace_*_skipped` categories are emitted by `validate.py --final-check` per ADR 0056 (S-0078) reading `mempalace_activity` written by `scan_mempalace_activity.py` at step 2; the previous self-recorded `diary_skipped` was renamed to `mempalace_diary_write_skipped` and is now mechanically detected from telemetry.

**Aggregation procedure:** filter `validate-history.jsonl` to entries with this session's `session_id` (or by timestamp window if any are tagged "outside-session"); for each category appearing in any entry, take the max count.

### 12. Scan drawer citations (per ADR 0056 S-0093 amendment, Issue #39)

After step 11 fills `outcome_summary` AND step 1 wrote the diary entry, run `python3 engine/tools/scan_mempalace_citations.py`. The tool scans `outcome_summary`, today's diary entry (via `mempalace.mcp_server.tool_diary_read`), and commit messages from `git log <eager-claim-sha>..HEAD --format=%B` for three citation patterns (drawer IDs, S-NNNN archive references, tag-named references). Writes the nested `mempalace_citations` block under the existing `mempalace_activity` field in `engine/session/current.json`. Idempotent — re-running overwrites the block.

The closing commit's pre-commit hook re-runs `validate.py --final-check`; the audit category `mempalace_zero_citations_after_search` reads the citations block written by this step. If `mempalace_activity.search_calls > 0` AND `mempalace_activity.mempalace_citations.total == 0`, the soft-warn fires. Gated on session id ≥ S-0093.

### 13. Archive the claim

```bash
git mv engine/session/current.json engine/session/archive/S-<NNNN>.json
```

Edit the archived file to add a `closed_at` timestamp and update `status` to `closed` (or `closed_partial` if the session hit a budget cap mid-work):

```json
{
  "id": "S-<NNNN>",
  "started_at": "...",
  "closed_at": "<ISO-8601 UTC>",
  "status": "closed",
  "outcome_summary": "...",
  "outcome_summary_soft_warns": { ... }
}
```

Update `engine/session/register_state.json`:

```json
{
  "next_id": "<unchanged from claim>",
  "last_claimed": "S-<NNNN>",
  "current_status": "closed"
}
```

### 14. Final commit + main FF + push

Conventional Commits with the session ID:

```
<type>(<scope>): <summary>

S-<NNNN> close: <one-line outcome>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Then push the close commit via the build-mode lifecycle wrapper (per [ADR 0076](../../../engine/adr/0076-build-mode-lifecycle-push-wrapping.md)):

```bash
python3 engine/tools/build_lifecycle_push.py close
```

The wrapper mechanically shape-verifies HEAD (close subject pattern, archive/S-NNNN.json created, current.json deleted, register_state.json flips `in_progress` → `closed`) before pushing. On success it performs the parent-side FF best-effort. Exit codes 0 / 2 / 3 / 4 / 5 per the wrapper's CLI contract. The wrapper bypasses the harness's "Default Branch Push" classifier via subprocess-spawned git from a permitted python tool — same pattern as `routine_lifecycle_push.py` (ADR 0054) for routine sessions.

No per-push confirmation — the `/start-engine` invocation at session boot already authorized the shutdown push.

### 15. Close-side worktree preservation (per ADR 0076 Amendment v2, S-0143)

**The closing session's worktree is NOT swept at close.** It survives close push + parent FF + archive so the user can return for follow-up. Both [`engine/tools/routine_worktree_sweep.py`](../../../engine/tools/routine_worktree_sweep.py) and [`engine/tools/sweep_worktrees.sh`](../../../engine/tools/sweep_worktrees.sh) carry a caller's-own-worktree pre-flight that refuses sweep when invoked against the caller's CWD — defense-in-depth in case any consumer accidentally targets it at close.

Accumulated prior-session worktrees are reaped at the **next session's boot** by [`engine/tools/hooks/session-start.sh`](../../../engine/tools/hooks/session-start.sh) invoking `sweep_worktrees.sh --apply --quiet` (gated on no-conflict; conservative pre-flight). Run `bash engine/tools/sweep_worktrees.sh` (dry-run, no `--quiet`) to see the full multi-line preserve-report per still-preserved worktree (path + branch + merged/ahead/behind + dirty files + last commit + guidance).

Pre-S-0143 history: the original ADR 0076 Amendment (S-0142) wired build-mode close to invoke `routine_worktree_sweep.py` on its own worktree. That destroyed the closing session's working folder before the user could follow up; S-0142 was the first natural exercise and the defect surfaced immediately. The Amendment v2 at S-0143 reverses the close-side invocation and shifts cleanup to next-session boot.

The session is fully closed after the close push completes.

## Updating design docs during a session

Design docs in `product/docs/` (`architecture.md`, `pedagogy.md`, `tensions.md`, etc.) follow a maintenance protocol that applies throughout the session:

- **Strong idea clarified or strengthened** → add to the relevant downstream file. If it rises to a core commitment, surface in `product/docs/MISSION.md` and `ROADMAP.md`.
- **New tension** → add to `product/docs/tensions.md` with enough context for a future session. Date the entry.
- **Tension resolved** → re-mark in place with `Resolved: YYYY-MM-DD` and absorb to the relevant downstream file. Don't delete from `tensions.md`.
- **New commitment + reasoning** → both *what* and *why* land in an ADR per [`adr-authoring.md`](../../../engine/operations/adr-authoring.md). Conversational story lands in MemPalace under the `decision` tag.
- **Idea surfaces but isn't ready for a file** → file a GitHub Issue with the `enhancement` label per [ADR 0048](../../../engine/adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md). (Pre-S-0083 captured in `product/docs/ideation.md`; retired at S-0083 per Issue #29.)
- **Deprecated files** → absorption + delete pattern. Absorb reasoning into the right downstream artifact, then `git rm` the original. Recovery via git tags or `git show <commit>:<path>`. Update references in cross-reference maps in the same commit.
- **Dead ends** → don't record. Design docs are forward-looking; MemPalace `exploration` drawers carry dead-end reasoning if anyone needs it.
- **Note dates only where the date is the artifact's content.** ENGINE_LOG entry dates, Resolved-tension markers, ADR Date headers — these are the artifact doing its job. Inside body prose, revision dates and session-attribution markers migrate to ENGINE_LOG and git history.

These updates each generate an ENGINE_LOG entry per the material-change criteria above.

## Partial closure (budget cap reached)

If the session hits its budget cap (per CLAUDE.md guidance) mid-work:

1. Halt at the next sensible boundary (don't leave the working tree in an unparseable state).
2. Run validate.py. Address any hard-fails.
3. Fill `outcome_summary` with what got done **and** what remains. Mark status `closed_partial`.
4. Update STATE.md's next-session work item to the unfinished portion plus context for the picking-up session.
5. Archive, commit (`<type>(<scope>): <summary> — partial close`), FF, push.

The next session picks up cleanly from STATE.md without re-deriving where things left off.

## Recovery (interrupted shutdown)

A clean close runs steps 1–14 in sequence. If the session crashes or halts mid-shutdown, the observable state determines the recovery path.

### Pre-recovery sanity check (verify the prior close did not already land)

**Before invoking any recovery scenario below, verify the prior close did not already land upstream.** A fresh worktree opened immediately after a prior session closed cleanly may show post-eager-claim state (current.json present, register status in_progress, STATE.md pre-close) because the worktree's checked-out files reflect a commit that pre-dates the close — not because the close was halted. Running recovery on a stale checkout corrupts state from a phantom problem.

Run `git fetch origin && git log --oneline origin/main -10`. If a `chore(session): close S-NNNN` commit for the slot named in `register_state.json`'s `last_claimed` field is visible upstream, the prior close landed cleanly and the local checkout is stale — not halted. Update the local checkout (`git pull --ff-only` or `git reset --hard origin/main` on a throwaway branch) and proceed with the *next* session's work; do not run recovery.

The asymmetry: a halted shutdown leaves no upstream close commit (the halt prevented the push); a stale checkout always has the upstream close commit. One `git log` check distinguishes them.

### Recovery scenarios

1. **Halted before step 13 (archive).** `current.json` present; `register_state.json` `current_status: in_progress`. Resume from step 1 — running the diary write, the activity rollup, `validate.py`, the spot-check, the cold-review pass, the side-discovery audit, and the `outcome_summary` fill in order.

2. **Halted between archive (step 13) and final commit (step 14).** `archive/S-<NNNN>.json` present, `current.json` absent, `register_state.json` `current_status: closed`. Stage and commit the planned final commit; FF main; push.

3. **Halted after final commit, before FF + push.** Final commit exists locally; `git log origin/main..HEAD` shows it. FF main and push. No state edits required.

4. **Split state.** Both archive and current files present, or `register_state.json` `current_status` disagrees with which file exists. Reconcile manually — read both, identify which carries the fuller `outcome_summary`, do not delete either blindly. Escalate per [`escalation-criteria.md`](../../../engine/operations/escalation-criteria.md) if the right reconciliation is unclear.

## See also

- [`engine/operations/session-shutdown-sequence.md`](../../../engine/operations/session-shutdown-sequence.md) — Layer 1 source-of-truth prose.
- [`engine/operations/session-build-lifecycle.md`](../../../engine/operations/session-build-lifecycle.md) — open-of-session protocol.
- [`engine/operations/tools-validate-interpretation.md`](../../../engine/operations/tools-validate-interpretation.md) — soft-warn category meanings.
- [`engine/operations/health-check.md`](../../../engine/operations/health-check.md) — telemetry feeds the periodic audit.
- [ADR 0042](../../../engine/adr/0042-soft-warn-lifecycle-archive-canon.md) — structured archive field this skill writes.
- [ADR 0044](../../../engine/adr/0044-skill-conversion-recipe-vs-reference.md) — recipe-vs-reference partition this skill instantiates.
