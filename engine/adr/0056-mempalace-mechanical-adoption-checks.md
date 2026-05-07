# ADR 0056 — MemPalace mechanical adoption checks

- **Status:** Accepted
- **Date:** 2026-05-06
- **Deciders:** S-0078

## Context

[CLAUDE.md](../../CLAUDE.md)'s "Two-layer decision recording" rule and [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md)'s "Project usage scope" both name three deliberate uses of MemPalace at every build session:

1. **Boot query** — `mempalace_search` against terms derived from `engine/STATE.md`'s next-session work item (CLAUDE.md startup ceremony step 3, `session-build-lifecycle.md` step 3).
2. **Boot diary read** — `mempalace_diary_read agent_name="claude" last_n=3` to surface the prior three sessions' first-person reflections (`session-build-lifecycle.md` step 3b, adopted at S-0032).
3. **Shutdown diary write** — `mempalace_diary_write` with the AI's reflection on the session (`session-shutdown-sequence.md` step 7, adopted at S-0032).

Plus the manual-capture asks at shutdown step 7 (`pushback` and `lesson` drawers via `mempalace_add_drawer`, adopted at S-0041 after the S-0032–S-0040 zero-capture gap).

Pre-S-0078 all of these were posture-only. The only mechanical surface was a self-recorded `diary_skipped: 1` soft-warn count in `outcome_summary_soft_warns` (per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)) — which assumed the AI honestly recorded its own omission and trusted the persistent-warn 3-of-5 surface to escalate.

[Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27), filed at S-0076 by the Phase 5 closeout author and confirmed mechanically by the S-0077 health-check audit, surfaced the gap end-to-end:

- Of 16 Phase 5 routine sessions, 12 silently skipped the diary write (S-0050, S-0054, S-0058, S-0059, S-0061, S-0063, S-0066, S-0068, S-0071, S-0073, S-0074, S-0075).
- The 12 missed sessions ALSO skipped the `diary_skipped: 1` self-record. Both directions failed.
- The persistent-warn 3-of-5 surface stayed inert across the entire Phase 5 window.
- The audit's `mempalace_search` probes for `pushback` / `lesson` drawers from the Phase 5 window returned empty — the manual-capture asks at shutdown step 7 were also being skipped silently.

The root cause Issue #27 identified: [`.claude/skills/routine-mode-lifecycle/SKILL.md`](../../.claude/skills/routine-mode-lifecycle/SKILL.md) step 11 enumerated a SUBSET of canonical shutdown steps that omitted the diary write and pushback/lesson capture asks. Routine sessions followed the enumeration in practice; the lead-in clause "Same as `/start-engine` close per `session-shutdown-sequence`" was procedurally honored as "do exactly what's enumerated below."

Interactive sessions slip in the same direction but more quietly — `session-build-lifecycle.md` step 3 (boot query) and step 3b (diary read) were posture-only with no detection mechanism, so an interactive session that skipped them left no trace at all. Worse than the routine case, where at least the absence of a diary entry was visible to anyone querying `mempalace_diary_read`.

The cumulative memory loss across S-0032 → S-0077 spans both modes: missed diary entries, ADR-companion `decision` drawers that were never written, `pushback` moments that were never captured, `lesson` candidates that vanished. The user's prompt at S-0078 framed the issue: "Use of mempalace by all sessions seems to have slipped out of convention. I noticed routine sessions missing it, but the health check I just ran also seems to have missed it even though it analyzed the git issue describing it. I need to make it mechanical for all session types."

The S-0077 audit upgraded Issue #27 to address-before-Phase-6-master-plan priority because Phase 6 is the next routine-mode-heavy phase; the gap would compound across it.

A separate but related Issue, [#20](https://github.com/StarshipSuperjam/paideia/issues/20) (S-0065 origin; S-0077 strengthening evidence), flagged that every new structured-field ADR (ADR 0042's `outcome_summary_soft_warns`, ADR 0051's `mode`) accumulated an audit-coverage gap unless [`engine/tools/audit_archive_structured_fields.py`](../tools/audit_archive_structured_fields.py) was extended in the same session. Adding a new field for this work without parameterizing the audit would perpetuate exactly that pattern.

## Decision

End-to-end mechanization of the three deliberate uses of MemPalace, applied uniformly across interactive (`/start-engine`) AND routine (`/start-routine`) session modes. Default-mode (exploration) sessions remain exempt — they have no formal slot or shutdown sequence.

The mechanism partitions across four layers:

### Layer 1 — Telemetry (PostToolUse hook)

A new `PostToolUse` hook matched on `mcp__mempalace__.*` invokes [`engine/tools/hooks/post-mempalace-tool-use.sh`](../tools/hooks/post-mempalace-tool-use.sh) on every MemPalace MCP call. The hook appends one JSONL line per call to `engine/session/current_mempalace.jsonl`:

```json
{"ts": "<iso>", "tool": "mcp__mempalace__mempalace_search", "args_summary": "<truncated 200 chars>"}
```

Always exits 0; never blocks the harness. Per-session, gitignored, cleared at archive. Same architectural pattern as the existing `post-adr-write.sh` and `post-state-edit.sh` PostToolUse hooks per [ADR 0043](0043-hook-architecture.md).

### Layer 2 — Rollup (`scan_mempalace_activity.py`)

[`engine/tools/scan_mempalace_activity.py`](../tools/scan_mempalace_activity.py) runs at session-shutdown step 0 (before the audit pass). Reads `current_mempalace.jsonl`, counts calls per tool, writes the structured `mempalace_activity` field into `engine/session/current.json`:

```json
"mempalace_activity": {
  "search_calls": 3,
  "diary_read_calls": 1,
  "diary_write_calls": 1,
  "add_drawer_calls": 2,
  "status_calls": 0,
  "list_drawers_calls": 0,
  "other_calls": 0,
  "total_calls": 7,
  "first_call_ts": "...",
  "last_call_ts": "..."
}
```

Idempotent — re-running overwrites the rollup. The field carries forward into the archive. (Pre-S-0083 this tool was symmetric in shape and lifecycle to `scan_context_telemetry.py`; that tool retired at S-0083 per the ADR 0049 amendment, but the rollup-write-then-archive shape inherited from it remains the canonical pattern for shutdown-step structured field captures.)

### Layer 3 — Audit (`validate.py --final-check`)

`validate.py` gains a `validate_mempalace_adoption()` function and a `--final-check` CLI flag. The flag is gated — pre-commit hook invocations (no flag) skip the adoption check so mid-session commits don't nag. The shutdown sequence invokes `validate.py --final-check` at step 1 after Layer 2 has written the `mempalace_activity` field.

Three categories:

| Category | Severity | Trigger |
|---|---|---|
| `mempalace_boot_query_skipped` | soft-warn | `mempalace_activity.search_calls == 0` |
| `mempalace_diary_read_skipped` | soft-warn | `mempalace_activity.diary_read_calls == 0` |
| `mempalace_diary_write_skipped` | **hard-fail** | `mempalace_activity.diary_write_calls == 0` AND no acknowledgement-token in `outcome_summary` |
| `mempalace_diary_write_acknowledged_skip` | soft-warn | `mempalace_activity.diary_write_calls == 0` AND `mempalace_unavailable_acknowledged: <reason>` is present in `outcome_summary` |

**Severity asymmetry rationale.** Boot query and diary read fail more gracefully — they can be re-invoked mid-session, and the cost of missing them is "context not retrieved" rather than "data lost." Diary write is the only first-person reflection layer; once a session closes without it, the reflection is irretrievable except via expensive transcript-crawl. Hard-fail there forces the issue while it's still cheap.

**Acknowledgement-token escape hatch.** Legitimate edge cases exist (MCP server unreachable; routine session that early-exits with nothing meaningful to reflect on; fresh repo before MemPalace init). The AI bypasses the hard-fail by writing one line into `outcome_summary` of `current.json` before re-running validate: `mempalace_unavailable_acknowledged: <one-line reason>`. The validator scans for the token; if present, the hard-fail downgrades to a soft-warn (`mempalace_diary_write_acknowledged_skip`). Misuse is detectable — persistent acknowledged-skips fire the same 3-of-5 escalation per ADR 0042 as unacknowledged ones.

### Layer 4 — Structural-fields audit (parameterization; closes Issue #20)

[`audit_archive_structured_fields.py`](../tools/audit_archive_structured_fields.py) is refactored from a single hardcoded check (`outcome_summary_soft_warns`) to a declarative `REQUIRED_ARCHIVE_FIELDS` list:

```python
REQUIRED_ARCHIVE_FIELDS = [
    {"field": "outcome_summary_soft_warns", "since_session": "S-0055", "shape": "dict", "adr": "ADR 0042"},
    {"field": "mode",                       "since_session": "S-0048", "shape": "str",  "adr": "ADR 0051"},
    {"field": "mempalace_activity",         "since_session": "S-0078", "shape": "dict", "adr": "ADR 0056"},
]
```

The audit walks the field set per session; for each row whose `since_session` is `≤` the session's id, it validates presence and shape. A new `--archive-history` flag walks every `engine/session/archive/S-*.json` and emits a Markdown report — informational mode for cross-archive forensics. Future structured-field ADRs add a row to the list in the same session per [ADR 0053](0053-mechanism-first-exercise-gate.md) mechanism-first-exercise-gate framing — no audit code change.

### Field migration

The pre-S-0078 self-recorded `diary_skipped` is renamed to `mempalace_diary_write_skipped` across every existing archive via [`engine/tools/migrate_diary_skipped_archive_field.py`](../tools/migrate_diary_skipped_archive_field.py). One-shot migration; idempotent; surgical text-based key removal preserving formatting and UTF-8 (regex-based to avoid `json.dumps` re-serialization churn).

### Companion SKILL/ops-doc updates (closes Issue #27)

- [`.claude/skills/routine-mode-lifecycle/SKILL.md`](../../.claude/skills/routine-mode-lifecycle/SKILL.md) step 5.5 (boot query) and step 5.6 (diary read) inserted between eligibility selection and plan authoring. Step 11 (shutdown) re-enumerated to explicitly include diary write + pushback/lesson capture asks (the Issue #27 root cause was the omission of these from the SUBSET enumeration that routine sessions followed in practice).
- [`.claude/skills/session-build-lifecycle/SKILL.md`](../../.claude/skills/session-build-lifecycle/SKILL.md) steps 3 and 3b annotated with mechanical-backstop notes ("backstopped by `mempalace_*_skipped` soft-warn").
- [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) step 0 added (rollup) and step 1 amended to invoke `validate.py --final-check`.
- Layer 1 source-of-truth ops docs (`session-build-lifecycle.md`, `session-shutdown-sequence.md`, `routine-mode-operations.md`, `mempalace-operations.md`, `soft-warn-lifecycle.md`) updated correspondingly per ADR 0044 doc-then-skill flow.

## Consequences

### Positive

- The cross-mode silent-slip pattern Issue #27 named is mechanically blocked. The hard-fail on diary write is the load-bearing piece (irretrievable data); the soft-warns on boot query and diary read participate in the existing 3-of-5 boot-time persistent-warn surface so silent slips become loud.
- Future health checks query `jq '.mempalace_activity'` over archives instead of grepping prose in `outcome_summary` — structural data, not narrative artifact.
- Issue #20 closes as a side effect — the parameterized `audit_archive_structured_fields.py` accepts new structured-field rows without code changes, so future structured-field ADRs add a row, not a code path.
- Routine and interactive sessions converge on a single MemPalace contract; one mechanism covers both modes.

### Negative

- One additional shutdown step (Layer 2 rollup) and one additional CLI flag (`--final-check`) on `validate.py`. Procedural surface area grows, but the new step is mechanical (idempotent, runs in <100ms typical) and the flag is gated to one invocation point.
- The `mempalace_diary_write_skipped` hard-fail is the first hard-fail validate.py adds for a "did the AI invoke an MCP tool" check. Prior hard-fails were structural (file present, key shape correct) — semantic enforcement of MCP-tool invocation is a new pattern. The acknowledgement-token escape hatch keeps the surface non-rigid for legitimate edge cases, but its discipline is itself posture (the AI is responsible for using the token honestly, not abusing it as a routine bypass).
- The migration script normalizes one detail of the old `diary_skipped` storage (it is removed entirely when zero, since zero == absent per ADR 0042). For 32 of 32 affected archives this is a no-op semantically; only the formatting differs.

### Cascade analysis (per ADR 0041)

- **ADR 0042** is amended-by-citation, not superseded — the new soft-warns participate in its 3-of-5 escalation surface and 10-session promotion criterion unchanged. The structured field shape is extended (new categories) but the contract holds.
- **ADR 0043** (hook architecture) gains a new PostToolUse matcher; the architecture pattern is unchanged. No supersession.
- **ADR 0044** (skill conversion partition) — the doc-then-skill flow is honored; Layer 1 ops docs lead, SKILL bodies follow.
- **ADR 0049** (scope-lock + descope-reorder audit) — `validate.py --final-check` is invoked alongside the existing `scope_delivery` audit at shutdown. No conflict.
- **ADR 0051** (routine-mode and engine loop) — routine boot procedure gains steps 5.5/5.6; routine shutdown SKILL gains the explicit diary write + pushback/lesson capture asks. The architectural distinction between `/start-engine` and `/start-routine` is preserved; only the shared MemPalace use is now uniformly enforced.
- **ADR 0053** (mechanism first-exercise gate) — this ADR triggers a first-exercise readiness note (per its trigger criterion #4: Consequences span ≥5 tooling files). See [`engine/build_readiness/mempalace_mechanical_adoption_first_exercise.md`](../build_readiness/mempalace_mechanical_adoption_first_exercise.md).
- Issue #27 closes; Issue #20 closes.

### Cross-cutting

- The mechanism is the third structured-field ADR after ADR 0042 and ADR 0051. The parameterization of `audit_archive_structured_fields.py` (Layer 4) is the discipline that prevents the next one from accumulating an audit-coverage gap. The next structured-field ADR adds a row to `REQUIRED_ARCHIVE_FIELDS` in the same session — no code change required.

### Amendment — S-0087 (S-0086 audit scale-back verdict)

The [S-0086 MemPalace adversarial review](../docs/audits/mempalace-adversarial-review-S-0086.md) — the first concrete application of [ADR 0057](0057-adversarial-stance-for-health-check-audits.md)'s adversarial-stance posture — reached a **scale back** verdict against the project's MemPalace surface, weighing both historical fit AND fit-to-CONTINUE per dual-temporal-frame discipline. Load-bearing core (search, add_drawer, diary read/write, read-only inspection, Stop/PreCompact hooks; ADR 0057 cadence-audit `pushback`/`lesson` substrate; ADR 0051 routine-mode boot diary read; two-layer decision recording per CLAUDE.md) earns its weight; dead-weight perimeter does not.

**Retirement program** (executed at S-0087; cleanup-side at downstream sessions per the issue close-out campaign):

- **KG family retired** (`mempalace_kg_query` / `kg_add` / `kg_invalidate` / `kg_stats` / `kg_timeline`) — zero forward-fit dependencies (Phase 6/7/DEC.1 specify Postgres + pgvector for runtime structural state).
- **Tunnels family retired** (`mempalace_find_tunnels` / `list_tunnels` / `create_tunnel` / `delete_tunnel` / `traverse`) — single-project install with no cross-wing-linking use case.
- **AAAK-for-project-drawers retired**; diary-wing AAAK carve-out preserved (`wing_claude` only) — AAAK's compression earns its weight in a single high-volume wing, not across one-off project captures.
- **Mined ops-doc drawers + orphaned per-worktree wings** flagged for cleanup execution at downstream sessions per Issues [#40](https://github.com/StarshipSuperjam/paideia/issues/40), [#41](https://github.com/StarshipSuperjam/paideia/issues/41), [#42](https://github.com/StarshipSuperjam/paideia/issues/42) per ADR 0048 issue-discipline routing.

**Contract scope unchanged.** ADR 0056's four-layer mechanical adoption checks (telemetry / rollup / audit / parameterization) still apply — the audit categories continue to fire on the scoped surface; what changes is **which surface** the contract covers. The scoped surface is now declared at [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Project usage scope" rather than implicit in the broader MemPalace tool registry.

**New audit category — `mempalace_retired_surface_used`** (soft-warn, fires when `mempalace_activity.kg_calls > 0` OR `mempalace_activity.tunnel_calls > 0`). Defense-in-depth against the retirement contract; MCP-server-side per-tool filtering is not yet feasible at the harness layer (the MCP server registers the full tool surface), so discipline + soft-warn detection are the load-bearing surface against scope regression. Participates in the 3-of-5 persistent-warn surface per ADR 0042.

**Rollup extended.** [`engine/tools/scan_mempalace_activity.py`](../tools/scan_mempalace_activity.py) gains `kg_calls` and `tunnel_calls` named buckets in `TOOL_KEY_MAP` and `EMPTY_ROLLUP`. The `audit_archive_structured_fields.py` `REQUIRED_ARCHIVE_FIELDS` row for `mempalace_activity` is unchanged — the new bucket fields ride that row per Layer 4 parameterization.

**Cross-references:** [Issue #43](https://github.com/StarshipSuperjam/paideia/issues/43) (this amendment + ops-doc updates); [Issue #42](https://github.com/StarshipSuperjam/paideia/issues/42) (KG/tunnels/AAAK execution-side retirement docs); [Issue #45](https://github.com/StarshipSuperjam/paideia/issues/45) (G1 soft-warn).

### Amendment — S-0089 (escape-hatch token tightening + boot/close MCP probes)

The S-0087 + S-0088 archives both used the `mempalace_unavailable_acknowledged:` escape hatch to downgrade the `mempalace_diary_write_skipped` hard-fail. In both cases the AI claimed unavailability based on the absence of `mcp__mempalace__*` from its deferred-tool list at session start; in both cases the substrate was actually live (the S-0088 conversation's resume hook surfaced 30 mempalace tools that the boot hook had not). The acknowledgement-token text lived in `outcome_summary` and the burial pattern only became visible on user pushback at S-0088 close: *"0056's escape hatch is a soft fail but it needs to be an obvious warning to me so that I can fix the issue and get the diary logged."*

The original mechanism's 3-of-5 persistent-warn escalation cedes 2 free sessions to the burial pattern by design — too lazy. The S-0089 tightening closes that gap on three fronts:

**1. Boot-time MCP-availability probe** in [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh). Runs `mempalace status` at every session boot. LOUD attention block when the CLI is missing or `status` fails — same surface treatment as ADR 0045's hard-broken probe findings. Mode differentiation does not apply at boot (the hook fires before `/start-engine` or `/start-routine`); the LOUD shape is uniform so the user sees it at the earliest possible moment regardless of session type.

**2. Close-time substrate probe** in `validate.py --final-check` via the new helper `_check_mempalace_substrate_alive()` (uses `python3 -m mempalace status` to bypass PATH issues per the existing ruff/mypy/pytest precedent). New soft-warn category `mempalace_substrate_at_close` fires whenever the substrate is unreachable, independent of diary-write state — the substrate could have been alive at boot and broken by close. Mode differentiation applies: engine sessions get a LOUD ⚠️-prefixed body with "DO NOT BURY THIS" header; routine sessions get a one-line standard body.

**3. Token validity tightening.** The `mempalace_unavailable_acknowledged:` token now only downgrades the `mempalace_diary_write_skipped` hard-fail when `mempalace status` actually fails at close-time. If the substrate is reachable, the token is INVALID — the AI claimed unavailable but reality contradicts — and a new hard-fail (`mempalace_diary_write_skipped_invalid_token`) blocks the close. The AI is forced to either (a) invoke `mempalace_diary_write` immediately (since MCP is live), or (b) investigate the upstream MCP-load timing issue rather than burying the failure.

**4. LOUD body for engine `mempalace_diary_write_acknowledged_skip`.** Even when the token is genuinely valid (substrate truly down), engine-session bodies now carry the LOUD ⚠️ prefix — single-session use is investigation-worthy on its own under the tightened contract, not "wait for 3-of-5".

**Coverage.** All session types — interactive build (`/start-engine`) AND routine (`/start-routine`). Engine sessions get LOUD; routines get standard one-line bodies because routines run unattended and the user reviews their archives later (LOUD attention blocks would just clutter archive review).

**Cross-references:** S-0087 + S-0088 archives (the burial pattern this hardens against); user pushback at S-0088 close ("each session to warn me at session start if mempalace MCP is unavailable. engine sessions should hard warn, routine sessions should soft warn"); the [`mempalace status`](https://github.com/MemPalace/mempalace) upstream subcommand whose contract this amendment relies on as the substrate-availability probe.

### Amendment — S-0090 (routine-protection refinement of S-0089's invalid-token hard-fail)

User clarified at S-0089 close: *"It's easy for me to fix the MCP connection issue. Seems that Claude Desktop has to be periodically rebooted to keep that working. I just need to know when it happens. I don't want that to kill routine sessions running overnight or while I'm AFK though."*

S-0089's `mempalace_diary_write_skipped_invalid_token` HARD-FAIL was over-correction. The user's S-0088-close framing was "obvious, not buried" — which the LOUD body achieves. Hard-failing the close blocks routines that hit intermittent MCP (substrate down when AI tried to write diary, alive at close-time) — exactly the routine-killing scenario the clarification rules out.

**S-0090 conversion:**

- The invalid-token branch (token + substrate-alive at close) is renamed to `mempalace_diary_write_skipped_substrate_intermittent` and converted from HARD-FAIL to SOFT-WARN.
- Mode-aware body shape preserves visibility:
  - **Engine (interactive):** LOUD ⚠️ "MCP INTERMITTENT — DO NOT BURY THIS" body. The live operator sees the contradiction (substrate alive + token claiming unavailable) and can act — invoke diary write immediately, or investigate the upstream MCP-load timing race.
  - **Routine:** standard one-line body. The routine session running overnight closes cleanly with the warn surfaced in archive review for the user's later inspection. Reboot Claude Desktop is the user's known fix per the S-0090 clarification.
- The S-0087/S-0088 burial pattern remains structurally hard to repeat. The LOUD body for engine sessions surfaces the contradiction explicitly; engine sessions cannot bury a LOUD ⚠️ "DO NOT BURY THIS" message in `outcome_summary`.

**Other paths unchanged:**

- No token + no diary write: still HARD-FAIL (`mempalace_diary_write_skipped`). The AI must add the token if it can't write — the routine-mode-lifecycle skill body has this branch; failure here means the skill body is buggy.
- Token + substrate-down: still soft-warn (`mempalace_diary_write_acknowledged_skip`); LOUD for engine, standard for routine. Honest closure path when substrate is genuinely unreachable.
- `mempalace_substrate_at_close` independent surface: unchanged. Continues firing whenever `mempalace status` fails at close, regardless of diary-write state.

**Coverage.** All session types — interactive build (`/start-engine`) AND routine (`/start-routine`). The "soft-warn closes; LOUD for engines" posture is the load-bearing surface for both modes; the close-must-proceed posture is load-bearing for both modes per the S-0090 routine-protection clarification.

**Cross-references:** S-0089 archive (the over-correction this softens); user clarification at S-0089 close ("I just need to know when it happens. I don't want that to kill routine sessions"); validate.py `validate_mempalace_adoption()` body shape.

### Amendment — S-0091 (close the no-token-no-diary hard-fail in routine mode + LOUD body uniformity + pending-diary index)

User pushback at S-0090 close: *"I want every engine session to warn me clearly whenever MCP to mempalace drops. I don't want it to stop the work from happening, but I don't want the mention to be lost in the noise of the session. … For routine sessions I don't want any hard failures of mempalace MCP access because that holds up the whole line of routine sessions. However, I have to know that happened clearly in the session text so that when I review I can reconnect MCP and tell the session to do their diary entry later."*

S-0090 left two gaps relative to that requirement:

1. **The no-token-no-diary path still hard-failed in routine mode.** When the AI in a routine session failed to write the diary AND failed to add the acknowledgement token (e.g. MCP dropped mid-session and the skill body's token-write branch didn't fire), `mempalace_diary_write_skipped` blocked the close — exactly the routine-line-halting scenario the user rules out.
2. **Routine archive bodies were "standard one-line"** for the substrate-availability soft-warns (substrate_at_close, acknowledged_skip, substrate_intermittent). Routine archives are reviewed by the user *more* carefully than engine session output (engine sessions are interactive; the user is in the loop). A buried one-line entry in `outcome_summary_soft_warns` is exactly the visibility failure mode the S-0088 "obvious, not buried" pushback was against.

**S-0091 changes:**

- **New soft-warn category `mempalace_diary_write_skipped_routine`** (routine mode only). Predicate is identical to the original `mempalace_diary_write_skipped` hard-fail (no diary write AND no token), but routine mode emits a soft-warn with a LOUD `⚠️ ROUTINE DIARY DEFERRED — DO NOT BURY THIS` body and appends an entry to a new index file at `engine/session/diary_pending_index.json`.
- **Engine retains the `mempalace_diary_write_skipped` hard-fail.** The asymmetry is justified by the unattended-vs-interactive difference: engine sessions have an immediate fix path (write the diary now, or write the token + reason); the hard-fail catches AI laziness in skipping the only first-person reflection layer. Routine mode's exemption does NOT generalize.
- **LOUD body uniformly for substrate-availability soft-warns** (substrate_at_close, acknowledged_skip, substrate_intermittent, diary_write_skipped_routine). The S-0089/S-0090 engine/routine differentiation is dropped — archive review is the routine-side visibility surface, and the `⚠️ … DO NOT BURY THIS` prefix costs nothing extra in routine archives while serving the user's "clearly in session text" requirement directly.
- **New pending-diary index** at `engine/session/diary_pending_index.json`. Schema: `{"schema_version": 1, "pending": [{"session_id": str, "closed_ts": str, "reason": str, "outcome_summary_excerpt": str (≤200 chars), "archive_path": str}]}`. Mutable, committed to git (like `register_state.json`). Operational allowlist entry in [`engine/tools/check_routine_scope.py`](../tools/check_routine_scope.py) `OPERATIONAL_ALLOWLIST` so routine-mode commits can write to it regardless of the active task's `scope_lock.allowed_paths`.
- **Boot-time surface in `engine/tools/hooks/session-start.sh`.** When the index is non-empty, emits a LOUD attention block listing the count + session IDs at every subsequent session boot until the user processes the index.
- **Recovery procedure** documented at `engine/operations/routine-mode-operations.md` "Deferred diary recovery": user reconnects MCP (typically Claude Desktop reboot), opens an interactive session, points at the index, AI reads each pending archive, authors a diary entry from the archived `outcome_summary` + `work_done` + `mempalace_activity` fields, calls `mempalace_diary_write`, and removes the entry from the index.

**Coverage table** (post-S-0091):

| Path | Engine | Routine | Closes? |
|---|---|---|---|
| Boot-probe substrate down | LOUD stderr | LOUD stderr | Yes |
| Substrate down at close (independent) | LOUD ⚠️ soft-warn | LOUD ⚠️ soft-warn | Yes |
| No diary + token + substrate-down | LOUD ⚠️ acknowledged_skip soft-warn | LOUD ⚠️ acknowledged_skip soft-warn | Yes |
| No diary + token + substrate-alive (intermittent) | LOUD ⚠️ substrate_intermittent soft-warn | LOUD ⚠️ substrate_intermittent soft-warn | Yes |
| **No diary + no token** | **HARD-FAIL** (interactive fix immediate) | **LOUD ⚠️ skipped_routine soft-warn + index entry** | Engine: **NO**. Routine: **Yes** |

**Pushback-rule observation.** The S-0089 → S-0090 → S-0091 sequence is a third consecutive contract refinement on the same ADR within ten sessions. Each refinement was user-driven and necessary; each refinement also had a structural lesson the prior session could have anticipated. The diary entry for S-0090 named the lesson explicitly: *"any contract-tightening should evaluate against routine-overnight scenario before landing | hard-fail is acceptable only when AI-discipline alone can satisfy it."* S-0091 is that lesson applied to the residual hard-fail S-0090 left standing.

**Out of scope** (S-0091 deliberate non-changes):

- No new slash command for the recovery procedure. Documented manual procedure suffices; a `/resume-deferred-diary` command can be a follow-up Issue if ergonomics warrant.
- No prepared-diary-text persistence. The recovering session reconstructs from the archive's structured fields rather than from a saved-text field. Adequate fidelity, no skill-side modifications.
- No retroactive archive mutation for sessions that closed pre-S-0091 with skipped diaries. Past archives stay as-is; the index starts empty.
- No change to the boot-time substrate health probe (already LOUD across modes per [ADR 0045](0045-shared-state-integrity-discipline.md)).

**Cross-references:** S-0090 archive (the residual hard-fail this closes); user pushback at S-0090 close ("I'm not confident that this solves my concern…"); plan file `~/.claude/plans/i-m-not-satisfied-with-modular-flute.md`; [`engine/tools/validate.py`](../tools/validate.py) `validate_mempalace_adoption()` body shape; [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) "Deferred diary recovery" section.

### Pushback rule (per CLAUDE.md)

The user's framing ("I need to know how to recover the lost memories") raised a separate concern about retroactive recovery of diary entries / decision drawers / pushback drawers / lesson drawers from the S-0032 → S-0077 window. That work is bounded as Part B of the approved plan and explicitly deferred to S-0079+ (see plan file at `~/.claude/plans/use-of-mempalace-by-velvety-pebble.md`); the recovery audit script and transcript-crawl executor are not part of S-0078's scope. Mechanization first stops the bleeding; recovery is bounded historical cleanup that fits cleanly in a separate session.

## Alternatives considered

### Alt 1 — Hard-fail across all three categories

Considered and rejected. The user-confirmed decision was "Mixed: soft-warn for query/read, hard-fail for diary write." Rationale: boot query and diary read are recoverable mid-session (soft-warn surfaces the gap; the AI can re-invoke); diary write is irretrievable post-close. Hard-failing all three makes legitimate edge cases (fresh repo, MCP server down) into session-blocking incidents requiring escape-hatch acknowledgement; mixed enforcement preserves the gradient.

### Alt 2 — Soft-warn across all three (matching existing `diary_skipped` pattern)

Considered and rejected. The Phase 5 evidence (12/16 routine sessions skipped diary write AND skipped the soft-warn self-record) demonstrates that pure soft-warn doesn't escalate when the AI is also responsible for emitting it. Mechanical detection (Layer 2 + Layer 3) closes the self-report gap; the diary-write hard-fail forces the irretrievable case while it's still cheap to fix.

### Alt 3 — Audit at every commit (not just shutdown)

Considered and rejected. The boot query and diary read happen ONCE at session boot; firing the soft-warn at every commit would nag for the entire session. Gating behind `--final-check` keeps the noise floor low and gives a single authoritative check at shutdown.

### Alt 4 — Wrap every MCP call rather than PostToolUse hook

Considered and rejected. Wrapping every MCP tool call would be invasive (every tool needs its own wrapper) and fragile (new MemPalace tools wouldn't be covered until the wrapper is updated). The PostToolUse hook is non-invasive, fires on every `mcp__mempalace__*` call regardless of how the AI invokes it, and matches an existing project pattern (`post-adr-write.sh`, `post-state-edit.sh`).

## See also

- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the soft-warn lifecycle this ADR extends.
- [ADR 0043](0043-hook-architecture.md) — the hook architecture pattern this ADR uses for Layer 1.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — the doc-then-skill flow honored across the SKILL/ops-doc updates.
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — the prior `scope_delivery` audit that runs alongside the new MemPalace audit at shutdown.
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — the routine-mode lifecycle whose SKILL is the Issue #27 root-cause fix target.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — the first-exercise gate this ADR triggers.
- [ADR 0057](0057-adversarial-stance-for-health-check-audits.md) — the adversarial-stance posture whose first concrete application produced the S-0086 audit and the scale-back verdict the S-0087 amendment records.
- [`engine/build_readiness/mempalace_mechanical_adoption_first_exercise.md`](../build_readiness/mempalace_mechanical_adoption_first_exercise.md) — the first-exercise readiness note for this mechanism.
- [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Project usage scope" + "Mechanical adoption checks" sections — the operational form of this ADR (post-S-0087-amendment scope).
- [`engine/docs/audits/mempalace-adversarial-review-S-0086.md`](../docs/audits/mempalace-adversarial-review-S-0086.md) — the audit underlying the S-0087 amendment.
- [Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27) — closes.
- [Issue #20](https://github.com/StarshipSuperjam/paideia/issues/20) — closes.
- [Issue #43](https://github.com/StarshipSuperjam/paideia/issues/43) — S-0087 amendment + ops-doc updates.
