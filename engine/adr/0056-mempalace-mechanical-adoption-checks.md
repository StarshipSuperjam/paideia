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
- [`engine/build_readiness/mempalace_mechanical_adoption_first_exercise.md`](../build_readiness/mempalace_mechanical_adoption_first_exercise.md) — the first-exercise readiness note for this mechanism.
- [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Mechanical adoption checks" section — the operational form of this ADR.
- [Issue #27](https://github.com/StarshipSuperjam/paideia/issues/27) — closes.
- [Issue #20](https://github.com/StarshipSuperjam/paideia/issues/20) — closes.
