# ADR 0049 — Scope-lock at boot, descope/reorder audit at shutdown, session-end context telemetry

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0042

## Context

Two coupled failure modes have surfaced repeatedly across the project's session history:

**Failure mode A — silent scope erosion.** Sessions begin with an implicit scope (the build_plan/ chunk being prepared, the next-session work item in STATE.md), but the AI is free to descope or reorder mid-session without leaving an auditable trace. Concrete instance from the planning thread: S-0037 proposed doing Phase 5 before Phase 4.5 — not literal "skip" but reordering as the same descoping pressure wearing a different mask. Without an explicit boot-time declaration of scope and a shutdown-time delivery audit, the only signal the user has is reading every commit message and inferring intent. That signal is too noisy to catch the pattern across 5+ sessions.

**Failure mode B — context-load opacity.** CLAUDE.md commits to budget guidance (60%/70% targets for substantive work; 70%/80% for mechanical) and instructs sessions to halt at sensible boundaries when the cap is reached. But the AI cannot observe its own context state in real time — the harness does not expose context-window usage to running code (verified at S-0042). The "halt at the cap" guidance is half-implementable: the AI doing the halting has no instrument to know the cap is reached. It guesses, and the guesses are uncalibrated.

The two failure modes feed each other. A session that cannot read its own context state guesses about budget and rationalizes scope changes ("this feels too big"). Without a scope declaration to audit, the descoping is invisible. Without telemetry on actual context use, the user has no cross-session data to spot whether sessions are running too long (suggesting splits or tighter scopes) or too short (suggesting bundling).

The user's framing surfaced both in the same planning thread: "what's missing from the system that would get the work aligned and on track?" — followed by the sharper reframing on telemetry: "record context state at the end of every session and that telemetry can be assessed during health check to say 'sessions are running too long' or 'sessions are running too short' and then make grounded assessment on how those sessions are bundled going forward."

## Decision

The project mechanizes five coupled rules that close both failure modes. Each is non-blocking at the harness level (soft-warns, not hard-fails) but visible to the AI through stderr surfacing and the soft-warn lifecycle (per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)).

### 1. Scope declaration at boot

A new field, `declared_scope`, joins the schema of [`engine/session/current.json`](../session/current.json). The field is a string holding 1–3 sentences of prose stating what the session commits to deliver. For build-plan-tracked work, the prose contains a `phase:` token whose value matches a phase identifier in [`build_plan/MANIFEST.md`](../../build_plan/MANIFEST.md) (e.g., `phase: P_3` or `phase: 4.5`). For operational/engine-apparatus work that doesn't map to a build-plan phase, the prose has no `phase:` token and is unrestricted.

The eager-claim ritual (per [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md)) writes the field at slot-claim time, alongside `working_on`. The `session-build-lifecycle` Skill mirror is updated in the same shape.

[`engine/tools/validate.py`](../tools/validate.py) gains soft-warn checks at first-commit time:
- `empty_declared_scope` — fires when the field is missing or empty string.
- `phase_mismatch_declared_scope` — fires when `phase:` token is present but the named identifier doesn't appear in `build_plan/MANIFEST.md`. Substring match, case-insensitive, whitespace-tolerant.

The phase-mismatch check catches the S-0037 reordering vector specifically: a session that declares `phase: 5` while the build-plan's next-due is `4.5` surfaces the mismatch at first-commit, before the session has authored anything substantive.

### 2. Scope-delivery audit at shutdown

The `session-shutdown-sequence` (Layer 1 doc + Skill mirror) gains a new step before `outcome_summary` fill: the AI is prompted with the literal text `"Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?"`

The AI's structured answer is written to `engine/session/current.json` under a new field:

```json
"scope_delivery": {
  "delivered": true | false,
  "user_confirmed_changes": true | false,
  "explanation": "<free text>"
}
```

`delivered: false` triggers the `scope_delivery_non_yes` soft-warn regardless of `user_confirmed_changes` value. The warn is signal for cross-session aggregation, not punishment — even justified scope changes leave a trace so the trend is visible. The `user_confirmed_changes` flag is captured for future audit but does not affect the soft-warn.

When `delivered: false` and `user_confirmed_changes: true`, the entry passes the audit (no hard-fail) but the soft-warn still fires. When `delivered: false` and `user_confirmed_changes: false`, the same soft-warn fires; the user's review of the archive will surface the unjustified deviation.

### 3. Multi-session scope-erosion signal

The `SessionStart` hook ([`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) per [ADR 0043](0043-hook-architecture.md)) gains a new surface: if 3 of the last 5 sessions had `scope_delivery.delivered == false`, the hook surfaces `[session-start] Scope-delivery non-yes in 3 of last 5 sessions; review scope-discipline.` Same surface treatment as the existing 3-of-5 persistent-warn pattern from ADR 0042.

### 4. Build-readiness gate clause

[`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) gains a no-descoping-or-reordering-at-gate-time clause: any reduction OR reordering of declared deliverables vs. the chunk plan must be flagged to the user, not silently absorbed into the gate report. This catches the case where the gate session itself is the descoping vector (S-0037 pattern).

### 5. Defer-handle field

A new field `next_session_handle: str | None` joins the schema of [`engine/session/current.json`](../session/current.json) and its archive form. Eager-claim writes `null`; the shutdown sequence fills the field via an explicit prompt asked at every shutdown (same discipline as Decision 2's scope-delivery prompt — judgment-alone produces zero captures; explicit prompting is the load-bearing surface). Three valid values:

- `"#<num>"` — Issue reference.
- `"S-<NNNN>"` — session reference (an existing archive OR the next-claim slot in `register_state.json`).
- `null` — explicit "no defer" when hedge phrasing in `outcome_summary` is intentional forward-pointer prose.

The field anchors a positive contract (must declare the handle) rather than a negative contract (must not use these words). False positives become "you forgot to declare" rather than "your prose tripped a regex."

[`engine/tools/validate.py`](../tools/validate.py) gains `validate_outcome_summary_unhandled_defer()` gated to the `--final-check` CLI flag, emitting four soft-warn categories per the disposition table:

| Hedge match in outcome_summary? | next_session_handle value | Action |
|--------------------------------|--------------------------|--------|
| No | (any) | No-op |
| Yes | key absent from JSON | `outcome_summary_unhandled_defer` (primary positive) |
| Yes | `null` | No-op (explicit "no defer") |
| Yes | `"#<num>"` verified exists | No-op |
| Yes | `"#<num>"` definitively missing | `next_session_handle_unknown_issue` |
| Yes | `"#<num>"` unverifiable (offline / gh missing / timeout) | No-op (offline-graceful) |
| Yes | `"S-<NNNN>"` archive exists OR matches next_id | No-op |
| Yes | `"S-<NNNN>"` matches neither | `next_session_handle_unknown_session` |
| Yes | other string / non-string non-null | `next_session_handle_malformed` |

Hedge regex set (case-insensitive, whitespace-tolerant): `future session`, `next session will`, `correctable in any`, `preserved for manual review`, `picked up by`, `defer indefinitely`, `revisit when`.

Issue verification uses `gh issue view <num> --json state` with a 5-second timeout. Definitive `Could not resolve to an Issue` / `no issue or pr` stderr responses fire `next_session_handle_unknown_issue`. `gh` not installed, network failure, auth issues, timeouts all suppress to keep the validator usable offline. Session verification: an `S-<NNNN>` value is valid if either `engine/session/archive/S-<NNNN>.json` exists OR `S-<NNNN>` matches the next-claim slot in `register_state.json`. Anything else fires `next_session_handle_unknown_session`.

The audit's `applicable_fields()` filter in `engine/tools/audit_archive_structured_fields.py` handles vintage gating — pre-introduction archives are not penalized for missing the field. The same mechanism lets `outcome_summary_soft_warns` (since S-0055), `mode` (since S-0048), `mempalace_activity` (since S-0078), and `next_session_handle` (since S-0100) coexist with older archives.

## Consequences

The deliverables this ADR commits to: [`engine/session/current.json`](../session/current.json) schema (`declared_scope`, `scope_delivery`, `next_session_handle`); [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) (eager-claim ritual writes `declared_scope`; `next_session_handle: null` initialized at eager-claim); [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) (scope-delivery prompt + defer-handle prompt); [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) (no-descoping-or-reordering clause); [`engine/tools/validate.py`](../tools/validate.py) (soft-warns `empty_declared_scope`, `phase_mismatch_declared_scope`, `scope_delivery_non_yes`, `outcome_summary_unhandled_defer`, `next_session_handle_unknown_issue`, `next_session_handle_unknown_session`, `next_session_handle_malformed`); [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) (multi-session scope-erosion surface); [`engine/tools/audit_archive_structured_fields.py`](../tools/audit_archive_structured_fields.py) (`REQUIRED_ARCHIVE_FIELDS` row for `next_session_handle` with shape `str_or_null`); [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) (seven new soft-warn category entries); [`.claude/skills/session-build-lifecycle/SKILL.md`](../../.claude/skills/session-build-lifecycle/SKILL.md), [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md), [`.claude/skills/build-readiness-gate/SKILL.md`](../../.claude/skills/build-readiness-gate/SKILL.md).

CLAUDE.md's "Posture vs machinery" section grows: scope discipline moves from posture (the AI was supposed to know the build-plan's next-due item and stay on it) to machinery (`declared_scope` is a tracked field; phase-mismatch fires at first-commit; scope-delivery is audited at shutdown; multi-session erosion is surfaced at boot; defer-handle is captured at close with hedge-detection backstop). The "rush to the next thing" pattern remains an LLM-trained behavior the system cannot fully prevent — but every instance of it now leaves an auditable trace. Default-mode runtime gains negligible cost (file reads + regex matches; the `gh issue view` calls are gated to `--final-check` and timeout-bounded).

The intervention does **not** fix the underlying LLM-trained tendency toward task-completion-via-shortest-viable-path or toward hedge-phrasing post-close. Sessions will still attempt to descope, reorder, or defer with forward-looking notes. What this ADR does is **raise the cost** (explicit user-facing acknowledgments at shutdown, auditable trail in the archive, multi-session signal at next boot) and **make user intent more visible** (scope is declared at boot, mismatch is caught at first-commit, the gate-time clause forecloses silent gate-session descoping, the defer-handle anchors a positive contract). The user retains the load-bearing pushback responsibility that CLAUDE.md's standing pushback rule formalizes; this ADR makes that pushback better-informed.

## See also

- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — preceding intervention; the gate surfaces decisions before authoring; this ADR catches descoping that survives the gate.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the three new soft-warns inherit the canon (archive-as-canon, 3-of-5 surface threshold, max-count aggregation across all session validate.py invocations).
- [ADR 0043](0043-hook-architecture.md) — the `SessionStart` hook this ADR extends with the multi-session scope-erosion surface.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — the three Skill mirrors (session-build-lifecycle, session-shutdown-sequence, build-readiness-gate) follow the recipe-shape partition; updates flow doc → skill, never the reverse.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — sibling intervention authored in the same session; the `declared_scope` field this ADR introduces is consumed by ADR 0048's collision-detection scanner.
