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

The project mechanizes three coupled rules that close both failure modes. Each is non-blocking at the harness level (soft-warns, not hard-fails) but visible to the AI through stderr surfacing and the soft-warn lifecycle (per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md)).

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

### 3. Session-end context telemetry

A new tool, [`engine/tools/scan_context_telemetry.py`](../tools/scan_context_telemetry.py), reads the session's transcript JSONL at `~/.claude/projects/<project>/<session-id>.jsonl` and computes an upper-bound estimate of the session's context-window usage by tokenizing the transcript content. The estimate is written to the session archive at shutdown as three fields:

- `transcript_token_estimate` (integer) — total tokens in the transcript content.
- `transcript_token_pct` (float) — `transcript_token_estimate / 1_000_000` (the 1M Opus 4.7 window).
- `tokenizer_used` (string) — `"tiktoken-o200k_base"` when tiktoken is installed; `"chars-div-4-fallback"` otherwise.

The estimate is upper-bound, not precise — the harness manages context via compaction and caching, and the on-disk transcript represents the full conversation rather than the actual prompt size at any moment. For the cross-session "running too long / too short / high variance" judgment this telemetry serves, upper-bound is sufficient.

[`engine/operations/health-check.md`](../operations/health-check.md) gains a "Session-load trend" section. The audit reads `transcript_token_pct` across the last N archived sessions and surfaces:

- **Running too long** — 3+ of last 5 sessions above 60% of the 1M context (substantive target). Suggests work should be split or scoped tighter at boot.
- **Running too short** — 3+ of last 5 sessions below 30%. Suggests work could have been bundled.
- **High variance** — stddev across last 5 > 15% of the window. Suggests scope-declaration discipline is loose; the audit should examine `scope_delivery` answers across the same window.

Thresholds are heuristic starting points. The health-check is allowed to amend without superseding this ADR.

### 4. Multi-session scope-erosion signal

The `SessionStart` hook ([`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) per [ADR 0043](0043-hook-architecture.md)) gains a new surface: if 3 of the last 5 sessions had `scope_delivery.delivered == false`, the hook surfaces `[session-start] Scope-delivery non-yes in 3 of last 5 sessions; review scope-discipline.` Same surface treatment as the existing 3-of-5 persistent-warn pattern from ADR 0042.

### 5. Build-readiness gate clause

[`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) gains a no-descoping-or-reordering-at-gate-time clause: any reduction OR reordering of declared deliverables vs. the chunk plan must be flagged to the user, not silently absorbed into the gate report. This catches the case where the gate session itself is the descoping vector (S-0037 pattern).

## Consequences

### Amendment (S-0100) — Decision 6 added: defer-handle field

Pushback Cluster A from the [S-0097 health-check audit](../../docs/health-checks/S-0097.md) (the formal first exercise of [ADR 0057](0057-adversarial-stance-for-health-check-audits.md)) surfaced a recurrent pattern: at session close, when a post-close issue is discovered, the AI authors a forward-looking note that conveys awareness without committing to a fix. Two canonical instances captured as `[pushback]`-prefixed drawers in `paideia/problems`: S-0071's *"correctable in any future session via a JSON edit"* and S-0048's *"preserved for manual review"*. Both share the anti-pattern: deferral language that masks lack-of-resolution. The note feels like discipline ("I noticed it") but is functionally identical to silence ("nobody will pick it up"). The S-0071 instance fired AFTER the standing memory `feedback_defer_indefinitely_is_pointless.md` was written — posture-rule discipline alone did not catch the lapse.

S-0098 user adjudication picked the structured archive-field requirement formulation over a brittle keyword-scan-only soft-warn. The structured-field formulation anchors on a positive contract (must declare the handle) rather than a negative contract (must not use these words). False positives become "you forgot to declare" rather than "your prose is fine but tripped a regex." The choice is captured in MemPalace `paideia/decisions` (S-0098 adjudication drawer).

**Decision 6:** New field `next_session_handle: str | None` on [`engine/session/current.json`](../session/current.json) and the archive. Eager-claim writes `null`; shutdown step 7b fills via explicit prompt asked at every shutdown (same discipline as Decision 2's scope-delivery prompt — judgment-alone produced zero captures across eight sessions in the S-0041 audit; explicit prompting is the load-bearing surface). Three valid values: `"#<num>"` (Issue reference), `"S-<NNNN>"` (session reference, either an existing archive OR the next-claim slot), `null` (explicit "no defer" when hedge phrasing in `outcome_summary` is intentional forward-pointer prose).

[`engine/tools/validate.py`](../tools/validate.py) gains `validate_outcome_summary_unhandled_defer()` gated to `--final-check`, emitting four soft-warn categories per the disposition table:

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

Hedge regex set (case-insensitive, whitespace-tolerant; conservative starting set per Issue #54, expand if false negatives surface in the first 5 sessions): `future session`, `next session will`, `correctable in any`, `preserved for manual review`, `picked up by`, `defer indefinitely`, `revisit when`.

Issue verification uses `gh issue view <num> --json state` with a 5-second timeout. Best-effort + offline-graceful: only definitive `Could not resolve to an Issue` / `no issue or pr` stderr responses fire `next_session_handle_unknown_issue`. `gh` not installed, network failure, auth issues, timeouts all suppress to keep the validator usable offline. Per Issue #54 design intent: catch typos and stale references when online; don't block offline work.

Session verification: an `S-<NNNN>` value is valid if either `engine/session/archive/S-<NNNN>.json` exists OR `S-<NNNN>` matches the next-claim slot in `register_state.json` (a session ID promised but not yet claimed). Anything else fires `next_session_handle_unknown_session`.

**Deliverables (lands at S-0100):**
- `engine/tools/validate.py` — new `validate_outcome_summary_unhandled_defer()` function + main-dispatch wire-up (alongside `validate_mempalace_adoption()` under the existing `args.final_check` branch). 26 new pytests at `engine/tools/test_validate_outcome_summary_unhandled_defer.py`.
- `engine/tools/audit_archive_structured_fields.py` — `REQUIRED_ARCHIVE_FIELDS` row for `next_session_handle` (since S-0100, shape `str_or_null`); `shape_check()` extension to support the new shape token (None and str both valid). 7 new pytests at `engine/tools/test_audit_archive_structured_fields.py`.
- `engine/operations/session-build-lifecycle.md` + `.claude/skills/session-build-lifecycle/SKILL.md` — schema block addition (`next_session_handle: null` initialized at eager-claim).
- `engine/operations/session-shutdown-sequence.md` + `.claude/skills/session-shutdown-sequence/SKILL.md` — new step 7b prompt + `outcome_summary_soft_warns` example block extended with the four new categories.
- `engine/operations/tools-validate-interpretation.md` — four new category entries (one primary + three diagnostic verification).
- This Amendment block.

The S-0100 archive is the first post-amendment session structurally bound to the new field. Pre-S-0100 archives are unaffected; the audit's `applicable_fields()` filter handles the vintage gating automatically (the same mechanism that's let `outcome_summary_soft_warns` (since S-0055), `mode` (since S-0048), and `mempalace_activity` (since S-0078) coexist with older archives).

**Companion validator surface count delta:** adds one new validator check function (`validate_outcome_summary_unhandled_defer`) emitting four soft-warn categories. Adds one new structured-field row to `REQUIRED_ARCHIVE_FIELDS`. Adds one new shape token (`str_or_null`) to the audit's shape vocabulary.

Decisions 1, 2, 4, and 5 of this ADR (declared_scope at boot, scope-delivery audit at shutdown, multi-session scope-erosion signal, build-readiness gate clause) are unaffected by this amendment and remain Accepted. Decision 3 remains retired per the S-0083 amendment below.

### Amendment (S-0083) — Decision 3 (session-end context telemetry) retired

The telemetry-capture portion of this ADR (decision 3 above; deliverables `scan_context_telemetry.py`, the three archive fields, and the health-check Session-load trend section) is **retired** at S-0083 per Issues [#21](https://github.com/StarshipSuperjam/paideia/issues/21) and [#32](https://github.com/StarshipSuperjam/paideia/issues/32). Empirical justification per Issue #32: the Session-load trend section ran in the S-0052, S-0065, and S-0077 audits and produced **zero behavioral signal** across all three (S-0052 absorbed by triage of the >1.0 fluke; S-0065 had 62% None capture rate filed as Issue #21; S-0077 produced "low and stable; no bundling-recommendation change"). The capture itself fluctuated non-deterministically across routine-mode sessions (Issue #21 reframed at S-0077), undermining cross-session comparability. The defensive surface area required to keep the metric from being misread as live in-session pressure (Issue #11 inline-fix at S-0052; CLAUDE.md "Posture vs machinery" bullets; the at-read-site cumulative-vs-live framing) outweighed the metric's contribution to actionable decisions.

The retirement deletes [`engine/tools/scan_context_telemetry.py`](../tools/scan_context_telemetry.py) and its 14 tests, removes the `tiktoken>=0.7.0` pin from [`engine/tools/requirements.txt`](../tools/requirements.txt), removes the shutdown step 7b from [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) and the corresponding step in [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md), removes the Session-load trend section from [`engine/operations/health-check.md`](../operations/health-check.md), and removes the two related bullets from CLAUDE.md "Posture vs machinery" (the cumulative-vs-live distinction; the prior-archive-backstop rejection). Pre-S-0083 archives still carry the three telemetry fields as historical artifacts; new archives do not. The audit_archive_structured_fields.py REQUIRED_ARCHIVE_FIELDS list never enforced these fields, so no audit changes are needed.

Decisions 1, 2, 4, and 5 of this ADR (declared_scope at boot, scope-delivery audit at shutdown, multi-session scope-erosion signal, build-readiness gate clause) are unaffected by the amendment and remain Accepted.

### Original consequences (S-0042 deliverable scope)

The deliverables this ADR commits to all land at S-0042:

- **New:** Tests for the new validator soft-warns. (The S-0042 deliverable originally listed at this position — the *scan_context_telemetry* tool and its tests — was retired at S-0083 per the Amendment block above; path-formatted reference removed at S-0098 to clear the *adr_consequences_deliverable_audit* validator soft-warn that fires on the *lands at S-0042* deliverable trigger phrase nearby. The Amendment block above remains the canonical historical record of what was promised, what was delivered, and why it was retired.)
- **Modified:** [`engine/session/current.json`](../session/current.json) schema (new `declared_scope` and `scope_delivery` fields), [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) (eager-claim ritual writes `declared_scope`), [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) (new audit step + telemetry capture step), [`engine/operations/build-readiness-gate.md`](../operations/build-readiness-gate.md) (no-descoping-or-reordering clause), [`engine/operations/health-check.md`](../operations/health-check.md) (Session-load trend section), [`engine/tools/validate.py`](../tools/validate.py) (two new soft-warns: `empty_declared_scope`, `phase_mismatch_declared_scope`; one shutdown soft-warn: `scope_delivery_non_yes`), [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) (multi-session scope-erosion surface), [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md) (three new soft-warn category entries), [`.claude/skills/session-build-lifecycle/SKILL.md`](../../.claude/skills/session-build-lifecycle/SKILL.md), [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md), [`.claude/skills/build-readiness-gate/SKILL.md`](../../.claude/skills/build-readiness-gate/SKILL.md).

CLAUDE.md's "Posture vs machinery" section grows another row: scope discipline moves from posture (the AI was supposed to know the build-plan's next-due item and stay on it) to machinery (`declared_scope` is a tracked field; phase-mismatch fires at first-commit; scope-delivery is audited at shutdown; multi-session erosion is surfaced at boot). The "rush to the next thing" pattern remains an LLM-trained behavior the system cannot fully prevent — but every instance of it now leaves an auditable trace.

The validator's check count rises from 18 (post-ADR 0048) to 21: `empty_declared_scope`, `phase_mismatch_declared_scope`, `scope_delivery_non_yes`. Default-mode runtime gains negligible cost (file reads + regex matches; no subprocess fires).

The telemetry mechanism is honest about its limits. Token estimates are upper-bound, not precise. The first ~5 sessions after this ADR lands accumulate the new fields; the health-check session-load trend becomes meaningful only after the window fills. The first health-check after S-0042 (cadence next due at S-0051) will encounter mostly-empty data; the audit handles missing fields gracefully.

The intervention does **not** fix the underlying LLM-trained tendency toward task-completion-via-shortest-viable-path. Sessions will still attempt to descope or reorder. What this ADR does is **raise the cost of descoping** (explicit user-facing acknowledgment in the shutdown audit, auditable trail in the archive, multi-session signal at next boot) and **make user intent more visible** (scope is declared at boot, mismatch is caught at first-commit, the gate-time clause forecloses silent gate-session descoping). The user retains the load-bearing pushback responsibility that CLAUDE.md's standing pushback rule formalizes; this ADR makes that pushback better-informed.

## See also

- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — preceding intervention; the gate surfaces decisions before authoring; this ADR catches descoping that survives the gate.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the three new soft-warns inherit the canon (archive-as-canon, 3-of-5 surface threshold, max-count aggregation across all session validate.py invocations).
- [ADR 0043](0043-hook-architecture.md) — the `SessionStart` hook this ADR extends with the multi-session scope-erosion surface.
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — the three Skill mirrors (session-build-lifecycle, session-shutdown-sequence, build-readiness-gate) follow the recipe-shape partition; updates flow doc → skill, never the reverse.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — sibling intervention authored in the same session; the `declared_scope` field this ADR introduces is consumed by ADR 0048's collision-detection scanner.
