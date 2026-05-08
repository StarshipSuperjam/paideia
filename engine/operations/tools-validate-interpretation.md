# Interpreting `tools/validate.py` output

> The validator is the project's structural conscience. It runs in the pre-commit hook on every commit and on demand. This file documents what each output category means and the response posture for each.

## Exit codes

| Exit | Meaning | Response |
|---|---|---|
| `0` | Clean — no hard-fails, no soft-warns | Proceed. |
| `1` | Soft-warns only — no hard-fails | Allowed by hook (configurable via env), but every soft-warn must be acknowledged in `outcome_summary` at session close. |
| `2` | At least one hard-fail | Blocking. Pre-commit hook rejects the commit. Fix and retry. |

## Hard-fails (always blocking)

Hard-fails are structural mistakes that, if committed, would degrade the project's machinery. Always fix before the commit lands.

Categories:

- **Missing required top-level file** — README, LICENSE, ENGINE_LOG, SECURITY, STATE, ROADMAP, HANDOFF must all exist. If you're intentionally retiring one, that's an architectural decision; ADR it first. (`ENGINE_LOG.md` was named `CHANGELOG.md` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md); the `CHANGELOG.md` filename is now reserved for the future learner-visible product release log.)
- **`session/register_state.json` missing or malformed** — required keys: `next_id`, `last_claimed`, `current_status`. Format must parse as JSON.
- **`session/current.json` missing keys** — when present (during an in-progress session), must have `id`, `started_at`, `status`, `working_on`. `id` must match `^S-\d{4}$`.
- **Graph-audit hard-fails** — duplicate node IDs, dangling edge references, prerequisite cycles in the `pedagogical_prerequisite` subgraph (detected via Kosaraju SCC). Active when `SUPABASE_DB_URL` is set in the environment; absent env var records `graph_audit_skipped` and runs no DB query (non-seed-authoring sessions are not gated on DB connectivity). See [ADR 0016](../adr/0016-graph-construction-needs-live-validation.md) for the full contract.
- **`mempalace_diary_write_skipped`** — diary-write hard-fail per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) (S-0078); **engine mode only** per S-0091. Fires when `mempalace_activity.diary_write_calls == 0` AND `outcome_summary` lacks the `mempalace_unavailable_acknowledged: <reason>` token AND `current.json` `mode` is not `routine`. Gated by `--final-check`. Engine asymmetry justified: interactive fix path is immediate (write the diary or write the token + reason); the hard-fail catches AI laziness in skipping the only first-person reflection layer. Recoverable by invoking `mempalace_diary_write` and re-running `validate.py --final-check`, OR by adding `mempalace_unavailable_acknowledged: <one-line reason>` to `outcome_summary` and re-running. Routine sessions hit the soft-warn `mempalace_diary_write_skipped_routine` instead — see below.

If a hard-fail blocks a commit and the fix is non-obvious, escalate per [`escalation-criteria.md`](escalation-criteria.md). Don't bypass the hook (`--no-verify`) — investigate the root cause.

## Soft-warns (signal, not blocker)

Soft-warns indicate slipping discipline or expected gaps. Each one rolls up into a category count recorded in `outcome_summary` at session close. Trend analysis (per [`health-check.md`](health-check.md)) consumes the per-category counts to detect drift.

Categories and meaning:

### `expected_future_file_missing`

A file expected to exist in a future session (per `EXPECTED_FROM_S0002` in `validate.py`) hasn't been authored yet. Expected during the session that's *about to* author it; should drop to zero after that session closes.

Example: during S-0001 the warns for `CLAUDE.md`, `docs/MISSION.md`, `docs/CROSS_REFERENCES.md`, `docs/operations/README.md` are expected. After S-0002 closes, all four should resolve.

If still warning after the session that was supposed to author the file: investigate. Either the file got missed or the file's authored but at a different path than expected.

### `engine_log_format`

`ENGINE_LOG.md` missing the `[Unreleased]` section header. Always recoverable — add the header. (Named `changelog_format` before [ADR 0037](../adr/0037-engine-product-wall-and-changelog-rename.md) renamed `CHANGELOG.md` → `ENGINE_LOG.md`.)

### `state_format`

`STATE.md` missing the "Current phase" field. Recoverable — restore the field. Indicates structural drift.

### `cross_reference_broken`

A markdown link in `docs/CROSS_REFERENCES.md` points at a `.md` file that doesn't exist. Recoverable — either the target path is wrong, or the target file was renamed/retired without updating CROSS_REFERENCES.md.

### `adr_missing_status`

An ADR file (matching `adr/NNNN-*.md`) doesn't contain a `Status:` line. Active from S-0003 onward. Recoverable — add a Status field per [`adr-authoring.md`](adr-authoring.md).

### `adr_index_inconsistent`

An ADR file in `adr/` either is not referenced from `adr/README.md`'s per-phase tables, or its `Status:` core keyword (Accepted / Superseded / Deprecated / Proposed) differs from the index's status column for that ADR. Active from S-0020 onward.

Recoverable — either add the missing index row (most common case: a new ADR was authored without the index update), or align the `Status:` field to match the index. The check normalizes around the four core status keywords; markdown-link decoration inside the status column is tolerated. False positives should refine the check rather than be papered over.

### `superseded_adr_currency`

A doc cites an ADR whose `Status:` is now `Superseded by ADR NNNN`, and the citation does not mark itself as historical. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Recoverable — re-point the citation to the new ADR, or add a `(superseded by ADR NNNN)` qualifier if the reference is intentionally historical, or rewrite the surrounding paragraph if the supersession changes substance. The check excludes `*/adr/*.md` and `engine/ENGINE_LOG.md`.

False positives: a superseded-ADR mention that legitimately reads as historical context but the surrounding 50 chars do not include "superseded" or the new ADR id. Suppress by adding the qualifier or by widening the surrounding context to include the marker.

### `adr_back_reference_orphan`

An ADR with `Status: Accepted` has zero citations from `.md` files outside `*/adr/*`. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). The warn names a question, not a defect: is this ADR load-bearing for future work, or is it dead weight?

Suppress with the `Orphan-OK` annotation per [`cascade-discipline.md`](cascade-discipline.md):

```markdown
- **Orphan-OK:** <reason>; revisit at <session-id-or-phase>
```

The annotation is a deferral, not a permanent exemption. The periodic health check audits the orphan-OK list.

### `adr_consequences_deliverable_audit`

An ADR's Consequences section anticipated a deliverable "around S-NNNN," that session is closed (per `engine/session/archive/`), and a deliverable file path also named in the ADR text is absent on disk. Active from S-0029 onward per [ADR 0041](../adr/0041-cascade-analysis-discipline.md). Heuristic regex: catches the literal "tools/foo.py around S-0025" shape; does not catch promises in different prose forms.

Recoverable — either land the deliverable (with closing-commit handshake per [`cascade-discipline.md`](cascade-discipline.md): cite the ADR id in the commit message), or amend the ADR's Consequences section to remove the now-obsolete promise, or document the deferral with a new expected session.

### `chromadb_palace_health`

The shared-state probe at [`engine/tools/probe_palace.py`](../tools/probe_palace.py) reported a level-1 (suspect) condition — palace path missing, no collections, or another anomaly that doesn't constitute outright corruption. Active from S-0035 onward per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md). Probe runs at every `validate.py` invocation in the default check set and in the `--health-probe-only` mode used by the SessionStart hook.

The probe escalates to a **hard-fail** (not a soft-warn) when the palace is definitely broken — chromadb refuses to import, `PersistentClient` raises on open, `get_collection() / count()` raises, or the probe segfaults at SIGSEGV (the S-0034 chromadb_rust_bindings signature on a corrupt HNSW segment). Definite corruption blocks the commit so the build session must address it before proceeding; the soft-warn level is reserved for ambiguous states that don't yet warrant blocking.

Per the S-0084 amendment to ADR 0045, the probe also promotes its overall exit code from 0 (healthy) to 1 (suspect) when HNSW divergence ≥ 10% is detected via `mempalace repair-status` — that condition surfaces here as well, with the divergence line as the soft-warn body, AND in the dedicated `mempalace_hnsw_divergence` category below.

Recoverable — `mempalace mine <dir>` to re-populate from source jsonl files; or move the suspect segment dir aside (`palace/<segment-uuid>.broken/`) and re-run the probe so chromadb rebuilds from SQLite-stored embeddings (the S-0034 recovery procedure). For the divergence-promoted case, see `mempalace_hnsw_divergence` below.

### `mempalace_boot_query_skipped`

No `mempalace_search` call was recorded during the session. Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md). Sourced from `mempalace_activity.search_calls == 0` on `current.json`. Gated by `--final-check` (the shutdown step's audit invocation, not pre-commit hook fires).

Recoverable mid-session by invoking `mempalace_search` once with the next-session work item terms; the post-tool-use hook captures the call into the session's JSONL, the rollup picks it up at shutdown, and the warn clears.

### `mempalace_diary_read_skipped`

No `mempalace_diary_read` call was recorded. Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md). Same telemetry path as the boot-query skip; same recovery (invoke once via the MCP tool with `agent_name="claude" last_n=3`).

### `mempalace_diary_write_skipped_routine`

**Routine mode only**, per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) S-0091 routine-protection refinement. Fires when `mempalace_activity.diary_write_calls == 0` AND `outcome_summary` lacks the `mempalace_unavailable_acknowledged:` token AND `current.json` `mode == "routine"`. Engine sessions hit `mempalace_diary_write_skipped` (hard-fail) instead — the asymmetry is justified by the unattended-vs-interactive difference.

Body is uniformly LOUD: `⚠️ ROUTINE DIARY DEFERRED — DO NOT BURY THIS`. Side effect: the validator appends an entry to [`engine/session/diary_pending_index.json`](../session/diary_pending_index.json) so the next session boot's SessionStart hook surfaces the count + IDs at every subsequent boot.

Recovery is *not* in-session — routines cannot recover their own dropped MCP. Recovery procedure: reconnect MCP (typically Claude Desktop reboot), open an interactive session, follow the "Deferred diary recovery" procedure at [`engine/operations/routine-mode-operations.md`](routine-mode-operations.md). The recovery session reads each pending archive, authors a diary entry from the structured fields, calls `mempalace_diary_write`, and removes the entry from the index.

Persistent firing across 3-of-5 sessions deserves investigation — the routine-mode-lifecycle skill body's token-write branch may be buggy, OR the MCP substrate is failing more often than expected.

### `mempalace_diary_write_skipped_substrate_intermittent`

No `mempalace_diary_write` call was recorded; `outcome_summary` carries the `mempalace_unavailable_acknowledged:` token claiming substrate unavailable; BUT `mempalace status` succeeds at close-time. The substrate is reachable now even though the AI claimed unavailable earlier — typically intermittent MCP resolved by rebooting Claude Desktop (the user's known cause per the S-0090 clarification). Active from S-0090 onward per the [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) Consequences amendment; was a hard-fail at S-0089 (`mempalace_diary_write_skipped_invalid_token`); converted to soft-warn at S-0090 per the user's routine-protection directive (*"I just need to know when it happens. I don't want that to kill routine sessions running overnight or while I'm AFK"*).

Body is uniformly LOUD per S-0091: `⚠️ MCP INTERMITTENT — DO NOT BURY THIS` prefix in both engine and routine modes. The S-0090 engine/routine differentiation is dropped — archive review is the routine-side visibility surface, and the LOUD prefix costs nothing extra in routine archives while serving the user's "clearly in session text" requirement directly.

Recoverable by invoking `mempalace_diary_write` and re-running `validate.py --final-check` (substrate is live, so the call should succeed). Single-session use is investigation-worthy on its own under the S-0090 contract; persistent firing across 3-of-5 sessions deserves the same escalation as other adoption checks.

### `mempalace_diary_write_acknowledged_skip`

No `mempalace_diary_write` call was recorded BUT `outcome_summary` carries the `mempalace_unavailable_acknowledged: <reason>` token, AND `mempalace status` confirms the substrate IS unreachable at close-time (the S-0089 contract tightening). Active from S-0078 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md); contract tightened at S-0089 per the Consequences amendment.

Body is uniformly LOUD per S-0091: `⚠️ DIARY WRITE SKIPPED — DO NOT BURY THIS` prefix in both engine and routine modes. The S-0089 engine/routine differentiation is dropped (see `mempalace_diary_write_skipped_substrate_intermittent` above for the rationale).

The token always downgrades the diary-write hard-fail to a soft-warn (so the session closes); the soft-warn category depends on the substrate state at close-time. Substrate unreachable → this category (`mempalace_diary_write_acknowledged_skip`); substrate reachable → `mempalace_diary_write_skipped_substrate_intermittent` (per S-0090). The S-0087/S-0088 burial pattern stays hard to repeat because both paths now have uniformly LOUD bodies surfacing the AI's claim alongside the substrate state.

Persistent firing across 3-of-5 sessions deserves investigation; single-session firing is itself investigation-worthy under the S-0089 contract.

### `mempalace_substrate_at_close`

The `mempalace status` substrate probe failed at session close (CLI not on PATH, palace dir missing, sqlite corrupt, chromadb open failure, or timeout). Active from S-0089 onward per the [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) Consequences amendment.

Independent of the diary-write check — this category surfaces broken substrate as its own signal so the user sees it at every close, not only when the acknowledgement token is used. The substrate could have been alive earlier in the session and broken by close (palace mid-prune, mid-rebuild, etc.).

Body is uniformly LOUD per S-0091: `⚠️ MEMPALACE SUBSTRATE DOWN — DO NOT BURY THIS` prefix in both engine and routine modes. Same single-session-signal treatment as the diary-write LOUD paths — not "wait for 3-of-5".

Recoverable — diagnose via `mempalace status 2>&1`, `ls ~/.mempalace/palace`, `mempalace repair-status`. Recovery: [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) per its documented procedure (S-0084 precedent). If the substrate is genuinely unreachable AND no recovery is possible mid-session, the acknowledgement-token path is the honest closure (per the [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) escape hatch + S-0089 tightening).

### `mempalace_retired_surface_used`

The session invoked one or more MemPalace tools that the project retired from use at S-0087 — KG family (`mempalace_kg_query` / `kg_add` / `kg_invalidate` / `kg_stats` / `kg_timeline`) or tunnel family (`mempalace_find_tunnels` / `list_tunnels` / `create_tunnel` / `delete_tunnel` / `traverse`). Active from S-0087 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) Consequences amendment. Sourced from `mempalace_activity.kg_calls > 0` OR `mempalace_activity.tunnel_calls > 0` on `current.json`. Body names the specific call counts (e.g., `kg_calls=3, tunnel_calls=2`).

This is a defense-in-depth surface — MCP-server-side per-tool filtering is not yet feasible at the harness layer (the MCP server registers the full tool surface), so discipline + soft-warn detection is the load-bearing surface against scope regression. The contract is at [`engine/operations/mempalace-operations.md`](mempalace-operations.md) "Project usage scope" + [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) Consequences amendment.

Expected zero post-retirement; persistent firing across 3-of-5 sessions indicates undocumented project usage and the contract should be revisited (file Issue, amend ADR 0056). Single-session firing on a one-off retired-surface invocation: identify the call site and either remove it or amend the contract — both routes go through ADR adjudication, not silent acceptance.

### `mempalace_zero_citations_after_search`

The session invoked MemPalace boot search (`search_calls > 0`) but the citation scan at shutdown found zero drawer references in `outcome_summary` + today's diary entry + commit messages. Active from S-0093 onward per [ADR 0056](../adr/0056-mempalace-mechanical-adoption-checks.md) S-0093 amendment + [Issue #39](https://github.com/StarshipSuperjam/paideia/issues/39). Sourced from `mempalace_activity.search_calls > 0 AND mempalace_activity.mempalace_citations.total == 0` on `current.json`. The citations block is written by [`engine/tools/scan_mempalace_citations.py`](../tools/scan_mempalace_citations.py) at shutdown step 8b. The check is gated on session id ≥ S-0093 (pre-S-0093 archives lack the block by design).

This is the closed-loop counterpart to `mempalace_boot_query_skipped`. Boot-query-skipped fires when the call did not happen; zero-citations-after-search fires when the call happened but produced no observable behavior change. Either side firing is signal that the boot-search apparatus is not delivering value.

Expected zero in well-functioning sessions — the boot-search orchestrator surfaces drawers that bear on the work, the AI cites them in plan rationale or commit messages, and the citation scan picks them up. Persistent firing across 3-of-5 sessions per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) signals one of two regressions: (a) the boot-search formulations aren't surfacing drawers the session would cite — tune the formulation set in [`engine/tools/mempalace_boot_search.py`](../tools/mempalace_boot_search.py) (synonyms, similarity threshold, keyword-extraction heuristic); (b) retrieved drawers ARE being surfaced but the AI isn't weaving them into authored artifacts — discipline issue, surface in the next pushback drawer.

### `mempalace_hnsw_divergence`

The HNSW vector-index has diverged from the SQLite ground truth by ≥ 10%. The divergent drawers are invisible to `mempalace_search`'s semantic-similarity path; for queries that hit those drawers, search degrades to BM25 lexical matching. **This is a transient failure mode that requires action, not a working state to live with.** Active from S-0084 onward per the [ADR 0045](../adr/0045-shared-state-integrity-discipline.md) amendment for [Issue #31](https://github.com/StarshipSuperjam/paideia/issues/31). The signal is sourced from `probe_palace.py`'s extension, which shells out to upstream's read-only `mempalace repair-status` subcommand (contracted to never open a chromadb client) and parses the SQLite vs HNSW counts.

Threshold tiers:

- **≥ 10%** (soft-warn): body names the percentage and points at the supported restoration path.
- **≥ 30%** (LOUD-attention soft-warn): body adds the destructive-repair carve-out warning verbatim, naming the S-0078 forensic (99.7% loss observed when `mempalace repair --mode legacy` was run).

**Do not auto-remediate via `mempalace repair --mode legacy`** under any divergence percentage. The supported restoration path is the project-internal direct-chromadb-rebuild tool — reads `(id, document, metadata)` tuples directly from `chroma.sqlite3`, deletes the collection preserving metadata, recreates, re-adds via `collection.add(documents=...)` to force fresh HNSW writes via the registered embedding function. Always run against a scratch palace copy first; atomic-rename swap to live gated on `mempalace repair-status` reporting status OK (within upstream's flush-lag tolerance). See [`engine/operations/mempalace-operations.md`](mempalace-operations.md) "Known issues" for forensic detail and the S-0084 first execution.

Recoverable — run [`engine/tools/mempalace_rebuild_hnsw.py`](../tools/mempalace_rebuild_hnsw.py) per the procedure documented there; soft-warn clears once divergence drops below 10%. If the rebuild itself surfaces an unexpected failure mode, file under the upstream tracker rather than reverting to a "live with BM25 fallback" posture.

### `mempalace_wing_count_growth`

Total MemPalace wing count has crossed an accumulation threshold. Active from S-0088 onward per [Issue #46](https://github.com/StarshipSuperjam/paideia/issues/46). The signal is sourced from `probe_palace.py`'s `[probe-palace] wings: N (total)` line, which counts distinct `wing` metadata values in the chromadb sqlite store directly (~2 s on a 47 K-drawer palace; the upstream `mempalace status` enumeration is too slow at boot scale). MemPalace stores all drawers in two chromadb collections with `wing` as a metadata field, so `len(client.list_collections())` is structurally always 2 — distinct-wing query is the only accurate accumulation surface.

Threshold tiers (configurable via `engine/session/register_state.json`'s `wing_count_growth_thresholds` block; bootstrap defaults `informational: 60`, `loud: 100`):

- **≥ informational** (soft-warn): body names the count and points at the cleanup tools (`engine/tools/prune_mempalace.py` for orphan-wings + ops-doc-drawer modes per Issue #40; the dedicated heavy historical-paths session per Issue #41).
- **≥ loud** (LOUD-attention soft-warn): body adds severity prose noting recall degradation and the discipline-rule that thresholds may only be adjusted *after* a cleanup batch lands — never raised to silence the surface.

The accumulation cause is the upstream wing-naming bug ([Issue #1](https://github.com/StarshipSuperjam/paideia/issues/1) / [Issue #2](https://github.com/StarshipSuperjam/paideia/issues/2)): each new worktree's auto-capture creates a new `wing_<hash>` per session, indefinitely. The Issue-#46 surface is the rate guardrail — symptoms accumulate between Issue-#40 / Issue-#41 cleanup batches; this soft-warn says "schedule the next batch."

Threshold reader silently falls back to the bootstrap defaults (60 / 100) when the register block is absent, malformed, or violates the `loud > informational > 0` contract — so a typo in operator-edited register_state.json can't poison the soft-warn.

Recoverable — run [`engine/tools/prune_mempalace.py`](../tools/prune_mempalace.py) per the procedure in [`engine/operations/mempalace-operations.md`](mempalace-operations.md) "Prune procedure"; the LOUD-tier finding clears once the count drops below the informational threshold.

### `health_check_overdue`

The cadence-aligned health-check audit slot has been consumed by other work and the audit slid past one full cadence. Active from S-0041 onward per [ADR 0022](../adr/0022-periodic-project-health-checks.md) Consequences amendment (overdue-catchup logic).

Fires when `(register_state.json.next_id - last_audit_session) > health_check_cadence`. The SessionStart hook (`engine/tools/hooks/session-start.sh`) surfaces both "due" (`slots_since == cadence`) and "overdue" (`slots_since > cadence`) at boot per the same amendment; this validator soft-warn is defense-in-depth so a silently-failing hook (the S-0033 / S-0034 vector pattern) cannot mask the slide. The validator stays silent at the natural-cadence slot — that case is the hook's "due" surface, not an overdue condition.

Skips quietly when `last_audit_session` is absent (legacy `register_state.json`, pre-S-0041); the `checks_run` field still records the attempt so cross-session telemetry distinguishes "field absent" from "check did not run."

Recoverable — run `engine/tools/health_check.py --session S-NNNN` (the report-emit bumps `last_audit_session`, clearing both the hook surface and this soft-warn) or document explicit deferral in `outcome_summary`.

### `repo_config_health`

The shared-state probe at [`engine/tools/probe_repo.py`](../tools/probe_repo.py) reported a level-1 (suspect) condition. Active from S-0035 onward per [ADR 0045](../adr/0045-shared-state-integrity-discipline.md). Currently no level-1 conditions are emitted (reserved for future calibration like dirty working tree or detached HEAD); all probe findings today reach hard-fail level.

The probe escalates to a **hard-fail** when `core.bare=true` is set on either the worktree's effective config or the parent clone's standalone `.git/config` (the S-0033 vector — masked by a worktree override but breaks parent-side boot operations like `merge --ff-only` and `push origin main`), or when HEAD does not resolve, or when basic `git rev-parse` queries fail.

Recoverable — the probe's stderr names the exact `git -C <repo> config --unset core.bare` command needed for the bare-misconfig case; HEAD-resolution failures are typically detached-HEAD or partial-checkout artifacts and are addressed by the appropriate `git checkout` or `git switch` operation.

### `issue_collision`

The Issue-collision scanner at [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) found one or more open GitHub Issues whose body or title contains either a keyword from this session's `declared_scope` (or fallback `working_on`) field in `current.json`, or a path from this commit's staged-files diff. Active from S-0042 onward per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

Each soft-warn body names the colliding Issue's number, title, and the matched keyword(s) or path(s). The signal is informational — non-blocking — surfaced so the AI can decide whether to (a) fix the colliding Issue first and reference it in the eventual commit, (b) work on it in parallel with the planned scope, or (c) proceed and trust the existing scope is independent of the Issue's named breakage.

A `gh` failure (no auth, no network, repo not on GitHub) silently skips the check; the scanner emits a stderr note and the validator records 0 collisions. The scanner-missing case (e.g., during `validate.py` migration) surfaces as a single soft-warn naming the missing path.

Recoverable per the choice the AI makes; the warn does not require resolution to commit.

### `empty_declared_scope`

A build session's `engine/session/current.json` is missing the `declared_scope` field or holds an empty string. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The field is the boot-time scope declaration: a 1-3 sentence statement of what the session commits to deliver, optionally including a `phase: <id>` token tying the work to a `build_plan/MANIFEST.md` identifier (or `phase: NA-...` for operational sessions).

The eager-claim ritual in [`session-build-lifecycle.md`](session-build-lifecycle.md) writes this field at slot-claim time. The soft-warn fires every commit until the field is populated.

Recoverable — open `engine/session/current.json`, add the `declared_scope` field with prose naming the session's deliverable. Skipped silently when `current.json` is absent (exploration mode).

### `phase_mismatch_declared_scope`

The `declared_scope` field contains a `phase:` token whose identifier doesn't appear in `build_plan/MANIFEST.md`. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). Catches the S-0037 reordering vector: a session declaring it's working on Phase 5 while the build-plan's next-due item is Phase 4.5 surfaces the mismatch at first-commit, before the session has authored anything substantive.

Matching is case-insensitive substring against the manifest text plus a heuristic token extraction (P_3, Phase 3, 3.0, 4.5, etc.). The literal prefix `NA` (e.g., `phase: NA-engine-apparatus`) is the explicit operational opt-out marker and skips the manifest match.

Recoverable — either correct the identifier to match the manifest, or replace it with `phase: NA-...` for operational/engine-apparatus work that doesn't map to a build-plan phase. If the session intends to reorder, update the build plan with explicit user-confirmed reorder before declaring scope on the new phase.

### `scope_delivery_non_yes`

A session's `engine/session/current.json` has `scope_delivery.delivered: false` at validator-run time. Active from S-0042 onward per [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md). The field is structured: `{delivered: bool, user_confirmed_changes: bool, explanation: str}`; the warn fires on `delivered: false` regardless of `user_confirmed_changes` because the warn is signal for cross-session aggregation, not punishment.

The shutdown audit step (added in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) per ADR 0049) prompts the AI with: *"Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?"* The structured answer goes into the field. The persistent-warn surface (per ADR 0042) escalates a 3-of-5 firing into the boot-time multi-session erosion signal in `session-start.sh`.

Recoverable — the warn is informational at the artifact level. The recoverable action is at the *next* session's planning: tighten scope, split the work, or address the systemic descoping-pressure pattern.

### `timestamp_helper_bypass`

A `Call` node in `engine/tools/**/*.py` (excluding `test_*.py` and the four allowlisted files) invokes `.isoformat(...)`, `.strftime(...)`, or `.fromisoformat(...)` directly. Per [ADR 0058](../adr/0058-canonical-timestamp-format-and-helper.md) + [`timestamp-discipline.md`](timestamp-discipline.md), all timestamp emission and parsing in the engine subtree routes through `engine/tools/timestamps.py` (`emit` / `emit_micros` / `parse` / `today`) so format knowledge concentrates in one place.

Recoverable: replace the bare call with the appropriate helper function, or — if the site has a legitimate non-canonical contract — add the file to `_TIMESTAMP_HELPER_BYPASS_ALLOWLIST` in `validate.py` with an inline comment naming what the helper would break if applied. The four current allowlist entries (`apply_migration.py`, `probe_push_gate.py`, `audit_mempalace_attribution.py`, `scan_mempalace_citations.py`) document the contract pattern.

Persistent firing across multiple sessions per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md)'s 3-of-5-archives surface signals new ad-hoc emission slipping in — investigate the offending file and either route through the helper or extend the allowlist with rationale.

### Graph-audit soft-warns (S-0037 onward, active when SUPABASE_DB_URL is set)

The seven categories ADR 0016 contracts. All seven register in `checks_run` even when zero findings fire, so cross-session telemetry distinguishes "category clean" from "category did not run" (the schema convention at [`session-shutdown-sequence.md`](session-shutdown-sequence.md)).

- `undeclared_predicate` — edge.type not in `product/seed-graph/migrations/PREDICATE_MANIFEST.md`. Recoverable: add the row to the registry in the same session that uses the predicate, paired with an ENGINE_LOG entry under `Added`. Per [`seed-chunked-authoring.md`](seed-chunked-authoring.md) step 5.
- `attribute_shape_inconsistency` — same-domain nodes with materially different attribute coverage. v1 metric: `teaching_notes` populated-vs-NULL split with the minority class above 30% within a domain tag. Phase 5 calibration is a [`engine/build_readiness/phase_4_graph_validation.md`](../build_readiness/phase_4_graph_validation.md) T3-C deferral.
- `missing_rigor_score` — node carries inbound `pedagogical_prerequisite` edges and `rigor_score_computed` is at the schema default `0.5` (per [`product/seed-graph/migrations/0002_nodes.sql`](../../product/seed-graph/migrations/0002_nodes.sql)). The architecture.md formula expects topology data; the warn fires on "could be computed but wasn't."
- `render_readiness_violation` — node label contains a scaffolding token (`service_node`, `synthetic`, `stub`). Per [ADR 0027](../../product/adr/0027-rendering-policy-prompt-layer-contract.md) applied to label authoring; recoverable by renaming the node before commit.
- `synthetic_review_queue` — node has `confidence_level = 'SYNTHETIC'` per [ADR 0030](../../product/adr/0030-confidence-level-evidentiary-mode-on-nodes.md). Not a defect — populates the Opus batch review consumer per [`product/docs/self-correction.md`](../../product/docs/self-correction.md).
- `orphan_leaf` — zero inbound + zero outbound `pedagogical_prerequisite` edges (other edge types do not count toward in/out degree for this category). Recoverable when downstream subdomains add edges that reach the leaf, or by re-evaluating whether the node belongs at the granularity principle.
- `suspicious_cross_domain_ratio` — subdomain (single domain tag) where >40% of inbound `pedagogical_prerequisite` edges originate from nodes carrying no overlap with that domain tag. Likely a missing service node on the inside of the subdomain; recoverable by introducing the service node and re-routing the cross-domain edges through it.

## Response posture

- **A soft-warn that recurs across multiple sessions** — formalized into a discipline per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). The boot-time persistent-warn surface flags categories firing in 3-or-more of the last 5 archives; categories firing in 10 consecutive archives reach the escalation criterion (promote to hard-fail, accept and annotate, or address inline) per [`soft-warn-lifecycle.md`](soft-warn-lifecycle.md).
- **A new hard-fail in CI on a commit that passed locally** — clock skew on `validate-history.jsonl` writes is fine to ignore; everything else is a real divergence to investigate.
- **Validator runtime > 3s** — Phase 4 graph audit budget is 3s on a 100-node test seed. If the structural-only checks (Phase 0+) start exceeding ~500ms, they've grown beyond their scope.

## Persistent-warn annotation

When the escalation criterion ([`soft-warn-lifecycle.md`](soft-warn-lifecycle.md), 10 consecutive archives) lands on "accept and annotate," the category gets an entry below explaining why the persistence is expected and what condition would resolve it. The boot surface respects the annotation by suppressing the surface for sessions that match the named condition.

The first three annotations land at the S-0077 audit (`docs/health-checks/S-0077.md` Fit section). Prior audits (S-0052, S-0065) referenced "annotated as expected per phase_5.md T2-C / scope breadth" in audit prose, but the canonical home below was empty — the annotations were conceptual rather than persisted in the document the boot-time persistent-warn surface actually reads. The S-0077 audit's reading of "the structured-data window has matured" trigger fired with three categories crossing the persistence threshold across multiple windows.

### `health_check_overdue` (annotated S-0077)

**Expected when:** at any session boot whose `last_audit_session` is more than `health_check_cadence` slots back (i.e., the trigger has fired but the audit hasn't been accepted yet — see [`health-check.md`](health-check.md) cadence-trigger logic).

**Resolution condition:** clears the moment `engine/tools/health_check.py --session S-NNNN` runs at audit close (the report-emit bumps `last_audit_session` and the next boot's hook + this validator both see `slots_since == 0`).

**Why annotated rather than addressed:** the soft-warn is the cadence-trigger's defense-in-depth (per the same hook silently failing — the S-0033/S-0034 vector pattern). It's structurally expected to fire whenever the user defers an audit through one or more sessions; promoting to hard-fail would block any session that overlaps the cadence window. The persistent-warn surface should suppress this category for the session that *is* the audit (the audit's own commits will fire it once before health_check.py bumps the field; this is correct).

### `issue_collision` (annotated S-0077)

**Expected when:** the session's `declared_scope` (or fallback `working_on`) and/or staged-files diff contains keywords or paths that broad-scope open Issues mention. The intentionally-broad keyword match in [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) catches scope-overlap risk so the AI can decide whether to fix-the-issue-first, work-in-parallel, or trust-independent-scope. Routine-mode sessions in particular fire this consistently because routine work has narrow paths but broad operational keywords (`session`, `start-engine`, `validate`, `routine-mode`, `boot`, etc.) that cross-cut most open Issues.

**Resolution condition:** declines naturally as the open-Issues backlog clears (cleanup-batch sessions) or as Issues are filed with narrower keyword surfaces. Does not require resolution to commit; the warn is informational by design per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md).

**Why annotated rather than addressed:** the warn's intentional broadness is the design choice from ADR 0048 — narrowing the keyword scanner would defeat the purpose (it's defense against "AI didn't realize the same concern was already filed"). The persistent-warn surface should suppress this category for build sessions that exhibit `issue_collision >= 5` with no >7 spike.

### `missing_rigor_score` (annotated S-0077)

**Expected when:** during phases that author concept nodes faster than the rigor-backfill cadence — Phase 5 partial-seed shape per [`engine/build_readiness/phase_5.md`](../build_readiness/phase_5.md) T2-C established the pattern; Phase 6 self-correction per [`product/docs/self-correction.md`](../../product/docs/self-correction.md) is the resolution surface.

**Resolution condition:** the Phase 6 self-correction backlog counter (per the Phase 5 closeout's "Forward pointers to Phase 6+" rigor-calibration deliverable) drains as Phase 6 routine sessions backfill `rigor_score_computed` against topology-bearing nodes. Does not require resolution to commit; structural per the architecture.md formula's expectation that topology data feeds the rigor score.

**Why annotated rather than addressed:** addressing in Phase 5 was the wrong shape — the rigor score depends on neighborhood structure (inbound edges), and partial seeds during phase build-up genuinely cannot compute the score reliably. The Phase 5 closeout deferred the calibration to Phase 6 as a pre-decided architectural choice, not a slip.

## Telemetry

Trend canon: committed `engine/session/archive/S-NNNN.json` field `outcome_summary_soft_warns` per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md). Read by `engine/tools/health_check.py` and the `/start-engine` boot procedure.

Per-invocation forensics: `engine/tools/validate-history.jsonl` (gitignored, per-clone). Useful for "when did this warn first appear" / "which commit introduced it" / "validator runtime drift."

## Closing-commit audits (hard-fail outside validate.py)

Two audits fire from the pre-commit hook only on `closing` commits (per `engine/tools/hooks/pre-commit`). They are structurally separate from validate.py but use the same exit-2-blocks-the-commit semantics.

- **`audit_handoff_dispositions.py`** (added at S-0036) — every new HANDOFF.md section in the session's range must carry a `**Disposition:**` line in one of five accepted forms. Per CLAUDE.md "Default to fix-in-context."
- **`audit_archive_structured_fields.py`** (added at S-0055 per [Issue #13](https://github.com/StarshipSuperjam/paideia/issues/13)) — the staged archive file (`engine/session/archive/S-NNNN.json`) must have `outcome_summary_soft_warns` present and non-null. Empty dict (`{}`) is permitted. Defends [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md)'s persistent-warn surface against silent field-absence lapses (S-0043–S-0047 lapse pattern).

Both audits also have manual invocation forms documented in [`session-shutdown-sequence.md`](session-shutdown-sequence.md) steps 6a and 6b — running them by hand before staging the close commit catches issues earlier than the hook.

## Tool invocation under venv

Tools that import `psycopg` (currently [`check_target.py`](../tools/check_target.py), [`validate.py`](../tools/validate.py), [`setup_env.py`](../tools/setup_env.py)) self-reexec under the project venv via [`engine/tools/_venv_reexec.py`](../tools/_venv_reexec.py) when invoked under a Python that lacks `psycopg`. Bare `python3 engine/tools/<x>.py` invocations work the same as if [`scrub_env.sh`](../tools/scrub_env.sh) had been sourced first. Per Issue #14 (S-0055): routine fires were resolving to system Python and emitting misleading `[FAIL] migration_applied — psycopg not available; cannot verify` output even though the migrations were genuinely applied.

The reexec is silent on success (the venv interpreter takes over without printing). If no `.venv/bin/python3` exists on the walk-up from `engine/tools/` to the filesystem root, the function returns silently and the caller's `import psycopg` raises the original `ImportError` — the prior behavior is preserved for genuinely-broken environments.

## See also

- [`session-shutdown-sequence.md`](session-shutdown-sequence.md) — where soft-warn counts get recorded.
- [`health-check.md`](health-check.md) — periodic audit consuming the JSONL telemetry.
- `tools/validate.py` — implementation.
