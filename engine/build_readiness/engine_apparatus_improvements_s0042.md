# Engine apparatus improvements — build-readiness report

> Authored by S-0042 (gate + build, single-session per the planning-thread compression noted below) for S-0042's own implementation per [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md). The build session reads this at boot. Tier 1 is fully resolved; if any Tier 1 surfaces during implementation, halt and escalate.

## Compression note

ADR 0040 names a temporal split — gate session precedes build session. This work is the exception ADR 0040's amendment discipline accommodates: the planning thread that produced [`/Users/shanekidd/.claude/plans/i-m-seeing-some-recurring-clever-axolotl.md`](../../.claude/plans/i-m-seeing-some-recurring-clever-axolotl.md) executed steps 1–5 of the gate procedure conversationally — three Explore agents in parallel (`Audit current deferral + health-check machinery`, `Measure deferral rate across recent sessions`, `Verify orphan files and surface other orphans`), user-directed Tier 1 resolution (sharpening the orphan definition from "anyone reference it?" to "is it doing work?"), Tier 2 decisions on disposition form / label taxonomy / scope-anchor mechanism, Tier 3 forward pointers on multi-session scope-erosion thresholds. The compression is honest: no separate gate slot consumed, but the substance of steps 1–5 is in the planning artifact and re-stated below.

The cold-review pass (step 8) is run after this report is complete, against the citations below.

## Pre-session decisions (Tier 1 resolutions)

- **Orphan definition is "is it doing work?", not "is anything pointing at it?"** — User-directed correction during planning. The reference-count axis alone reproduces the failure mode the rebuild is trying to fix (see citation below). The scanner must compute multiple axes (reference-count + last-substantive-modification age + register-emptiness + ops-doc-citation-count + stale-pending-marker age) and the audit prompt must lead with the operative diagnostic question, not categorical triage. Authored artifact: Intervention 2 in the plan.

  *Citation:* User correction in this conversation thread on `ideation.md` and `prep-paideia-prompt-pack.md`. The pattern matches the failure mode named in [`engine/operations/health-check.md`](../operations/health-check.md):L? (the doc has substantive prompting but no mechanical floor — verified by Agent A in the planning thread).

- **HANDOFF.md scope tightens to session-internal handoffs only.** Cross-session deferrals — bugs, tech-debt, cleanup, enhancements — route to GitHub Issues with a label taxonomy (`bug`, `enhancement`, `tech-debt`, `cleanup`, `health-check-finding`, `upstream`, plus `priority:urgent`). The `upstream` label marks bugs that are real and affect the project but are not in-project actionable (the canonical first instance: the mempalace 3.3.3 wing-filter and wing-naming bugs documented in S-0040). Disposition audit grows a `tracked-as-issue #<num>` form. Resolved against the user's framing: "every HANDOFF entry creates pressure for 'next session must address this' → cleanup treadmill." Authored artifact: new ADR (drafted in this session) + Intervention 1.

  *Citation:* User framing in this conversation thread + the explorer agent's audit confirmation that `audit_handoff_dispositions.py` enforces form, not user-consultation intent (verified at [`engine/tools/audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py)).

- **Scope-lock anchors to phase/chunk identifier, not just prose.** This catches reorderings (S-0037's phase-5-before-4.5 pattern) in addition to deletions. The `declared_scope` field at boot must include the explicit phase/chunk identifier the session claims to be working on; mismatch with build-plan next-due triggers a soft-warn at first commit. Authored artifact: Intervention 3.

  *Citation:* User reference to S-0037 in this conversation thread + the explorer agent's count showing 5 of 9 cleanup sessions displaced roadmap work in S-0027–S-0041.

- **Context-state telemetry is captured at session-end via transcript-tokenization, not real-time polling.** Claude Code does not expose context usage to hooks or subprocesses (verified by claude-code-guide agent). The transcript JSONL at `~/.claude/projects/<project>/<session-id>.jsonl` is read at shutdown, tokenized for an upper-bound estimate, and stored in the session archive. Health-check consumes the trend across N sessions for "running too long / too short / high variance" bundling judgments. Authored artifact: cross-cutting telemetry addition in plan.

  *Citation:* User reframing in this conversation thread ("record context state at the end of every session and that telemetry can be assessed during health check") + claude-code-guide agent's authoritative finding that no live polling surface exists.

## Tier 2 decisions

- **T2-A — disposition form pattern.** New fifth entry appended to `_VALID_DISPOSITION_PATTERNS` in [`engine/tools/audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py): `re.compile(r"^tracked-as-issue\s+#(\d+)$")`. Style mirrors the existing four patterns (which match against the *value* extracted by `DISPOSITION_RE`, not the full markdown line — see lines 97–108 of the script). The author-facing form in HANDOFF.md is `**Disposition:** tracked-as-issue #<num>` with one or more digits. Audit hint message at lines 332–343 grows a fifth bullet.

- **T2-B — Issue body shape.** Each Issue body must include a `### Affected files` section listing tracked file paths the issue touches (one per line, repo-relative). The collision-detection scanner uses these for path-overlap matching against the session's first commits.

- **T2-C — Boot surface format for backlog.** Single-line FYI when no urgent: `[session-start] Issues backlog: N bugs, N tech-debt, N cleanup, N enhancement (M urgent).` Multi-line LOUD block when urgent count > 0, listing each urgent issue's `#<num>: <title>` plus its non-priority labels. The LOUD treatment matches the persistent-warn surface and the shared-state hard-broken finding surface (per ADR 0045).

- **T2-D — Collision-detection trigger and shape.** Fires from the `pre-commit` hook on the *first* commit after the eager-claim — i.e., when `engine/session/current.json`'s `declared_scope` field is freshly written. Strategy: (1) extract keywords from `declared_scope` (whitespace-tokenized, lowercase, drop common stopwords like "the", "a", "of", "and", "in"); (2) extract phase/chunk identifier; (3) collect the file paths from this commit's `git diff --cached --name-only`; (4) query open issues, soft-warn if any issue body contains either an extracted keyword OR a touched file path. Output format: `[validate] Open issue #<num> "<title>" appears to touch this session's scope: <matched-keyword|file-path>.`

- **T2-E — Multi-axis orphan scanner output structure.** Per-candidate annotation in `engine/health_check/dead_weight_candidates_<session>.md`:
  ```
  ### <relative-path>
  - Axis: <reference-count|last-mod-age|register-emptiness|ops-doc-citation|stale-marker>
  - Signal: <human-readable why>
  - Last substantive change: <commit-sha date>
  - Inbound references: <count>
  ```
  The audit walks the file top-to-bottom and judges each candidate against the operative question.

- **T2-F — `declared_scope` schema in `current.json`.** New string field, 1–3 sentences of prose. For build-plan-tracked work, the prose must contain a `phase:` token whose value matches a phase identifier in [`build_plan/MANIFEST.md`](../../build_plan/MANIFEST.md) (e.g., `phase: P_3` or `phase: 4.5`). For operational/engine-apparatus work that doesn't map to a build-plan phase, the prose has no `phase:` token and is unrestricted. The validator's matching is substring (case-insensitive, whitespace-tolerant): if `phase:` appears, the validator scans the build-plan MANIFEST for the named identifier and soft-warns on no match. If `phase:` does not appear, the validator only checks the field is non-empty.

- **T2-G — Scope-delivery audit prompt at shutdown.** Exact text the AI is prompted with: `"Did you deliver the declared scope? If no, why not? Did anything get descoped, reordered, or deferred mid-session — even with user confirmation?"` AI's free-text answer is recorded in `current.json` under a structured field: `{"delivered": <bool>, "user_confirmed_changes": <bool>, "explanation": "<free text>"}`. The audit takes the AI's literal `delivered` boolean. `delivered: false` → `scope_delivery_non_yes` soft-warn regardless of `user_confirmed_changes` value (the warn is *signal* for cross-session aggregation, not punishment — even justified scope changes leave a trace so the trend is visible). `user_confirmed_changes` is captured for future audit but does not affect the soft-warn.

- **T2-H — Multi-session scope-erosion threshold.** 3 of last 5 sessions with non-yes scope-delivery → SessionStart hook surfaces `[session-start] Scope-delivery non-yes in 3 of last 5 sessions; review scope-discipline.` Same surface treatment as the existing 3-of-5 persistent-warn.

- **T2-I — Tokenizer choice for context telemetry.** Try `tiktoken` with `o200k_base` first (best Claude proxy publicly available); fall back to `len(transcript_text) // 4` if tiktoken not installed. Stored field `tokenizer_used` records which.

- **T2-J — Health-check session-load-trend thresholds.** "Running too long" = 3+ of last 5 sessions above 60% of 1M context (substantive target). "Running too short" = 3+ of last 5 sessions below 30%. "High variance" = stddev across last 5 > 15% of window. These are heuristic starting points; the health-check is allowed to amend without ADR.

## Tier 3 forward pointers

- **T3-A — gh CLI dependency.** This session assumes `gh` is installed and authenticated locally. Not added to a setup doc here; defer to a future ops doc edit if a fresh-clone session needs the `gh` setup walkthrough. Decide-before: first cross-machine session.

- **T3-B — Issue label creation.** Labels (`bug`, `enhancement`, `tech-debt`, `cleanup`, `health-check-finding`, `upstream`, `priority:urgent`) get created via `gh label create` during the verification step of this session. If the GitHub repo already has conflicting labels, harmonize ad-hoc (this is the kind of low-stakes choice the session should not escalate).

- **T3-B.1 — Seed Issues at verification time.** The MemPalace wing-filter bug and wing-naming bug from the S-0040 HANDOFF entry are filed as the first real Issues during the verification step — labels `bug` + `upstream`, body cross-references the HANDOFF entry and the workaround in `engine/operations/mempalace-operations.md`. This serves both as test of the full `gh issue create` flow and as a permanent surface for a known-active limitation that currently lives only in resolved-HANDOFF + ops-doc form.

- **T3-C — Real-world tuning of collision keyword extraction.** The first-pass keyword extraction is naive (whitespace + stopword filter). Refinement deferred to first false-positive surfacing. Decide-before: first session where collision-warn fires noisily.

- **T3-D — Backfilling `transcript_token_estimate` for prior archives.** Out of scope. Telemetry begins from S-0042 forward; the health-check section will gracefully handle missing fields until 5+ sessions accumulate the new data. Decide-before: first health-check that wants to use the trend (cadence next due at S-0051).

- **T3-E — Dead-weight triage outputs.** The first session that runs the new health-check will surface `ideation.md`, `sub-agent-validation.md`, `tools-sweep-worktrees.md`, top-level `docs/`, and unfired decide-triggers in `prep-paideia-prompt-pack.md`. Triage decisions (retire vs preserve vs convert to active use) are not made here — they are the next health-check's work. Decide-before: S-0051 health-check audit.

## Success criteria for the build session

Inherits from the approved plan's verification section, surfaced here for boot-time visibility:

- New disposition `tracked-as-issue #<num>` accepted by `audit_handoff_dispositions.py` (verified by unit test).
- `scan_orphans.py` surfaces all of: `ideation.md`, `sub-agent-validation.md`, `tools-sweep-worktrees.md`, top-level `docs/`, unfired decide-triggers in `prep-paideia-prompt-pack.md` when run against the current repo.
- `scan_issue_backlog.py` produces the FYI line and (when an urgent issue exists) the LOUD block; `scan_issue_collisions.py` surfaces the path-overlap warning when a test issue mentions a file in the session's scope.
- `validate.py` soft-warns on empty `declared_scope`; soft-warns on non-yes scope-delivery answer.
- `scan_context_telemetry.py` writes `transcript_token_estimate` and `transcript_token_pct` to `engine/session/archive/S-0042.json` at shutdown. Spot-check value against word-count / 0.75 sanity.
- All Skills (`session-build-lifecycle`, `session-shutdown-sequence`, `build-readiness-gate`) mirror their Layer 1 doc updates.
- Validator end-of-session: 0 hard-fails. Soft-warns are the new ones intentionally exercised during verification.
- Tests added for new tools and new validator rules; the full existing test suite still passes (run `pytest` to verify; do not hard-code a baseline count — use the actual current pass count at run time).

## Authored resolution artifacts (in S-0042)

- **New ADR** documenting the HANDOFF/Issues split (engine ADR; next number is 0048 — the index post-S-0041 stands at 47 ADRs total: ADRs 0001–0047).
- **17 file touches** per the plan's "Files to modify" table.
- **This report itself** at `engine/build_readiness/engine_apparatus_improvements_s0042.md`.

## Cold-review findings (per ADR 0040 step 8)

A fresh-context Explore agent reviewed this report against its citations. Findings:

- **Discrepancy — test count.** Original report claimed "196 tests still pass." Cold reviewer counted 177 test functions via grep; mismatch with the S-0041 outcome record. **Resolution:** removed the hard-coded count from the success criteria; test pass-count is verified at run time, not asserted in advance.
- **Spec-sharpening — T2-A regex.** Original specification mixed the disposition-extraction regex (which matches the markdown `**Disposition:**` line) with the pattern-validation regex (which matches the *value* extracted by the first regex). **Resolution:** T2-A now names the new fifth pattern as `re.compile(r"^tracked-as-issue\s+#(\d+)$")` to be appended to `_VALID_DISPOSITION_PATTERNS`, with explicit reference to the existing script's lines 97–108 to show the integration point.
- **Spec-sharpening — T2-F phase example.** Original used `phase: NA-engine-mechanism` as an example, which doesn't match any build-plan phase identifier. **Resolution:** clarified that the `phase:` token is required ONLY for build-plan-tracked work; for operational/engine-apparatus work the field is unrestricted prose with no `phase:` token. Validator's matching logic explicitly described.
- **Spec-sharpening — T2-G ambiguity.** Original parsed first-word-of-answer for yes/no, leaving "user-confirmed descoping" semantics ambiguous. **Resolution:** structured the field as `{delivered: bool, user_confirmed_changes: bool, explanation: str}`. The soft-warn fires on `delivered: false` regardless of user-confirmation status — the warn is signal for cross-session aggregation, not punishment.

All four resolutions land in this report; no changes to the plan's intent. The cold-review caught spec fragility that would have surfaced as build-time confusion if left unaddressed.

## See also

- [`/Users/shanekidd/.claude/plans/i-m-seeing-some-recurring-clever-axolotl.md`](../../.claude/plans/i-m-seeing-some-recurring-clever-axolotl.md) — the approved plan; the substantive contract this report formalizes.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the gate-protocol contract this report executes.
- [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle; the new soft-warns introduced here (`empty_declared_scope`, `scope_delivery_non_yes`) inherit the canon.
- [ADR 0045](../adr/0045-shared-state-integrity-discipline.md) — surface treatment for boot-time hard-broken findings; the urgent-issue LOUD surface mirrors this pattern.
- [`engine/operations/handoff-discipline.md`](../operations/handoff-discipline.md) (or successor) — the doc this work amends.
- [`engine/operations/health-check.md`](../operations/health-check.md) — the doc this work rewrites.
- [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) — boot procedure; amended for `declared_scope` writing.
- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) — shutdown protocol; amended for scope-delivery audit + telemetry capture.
