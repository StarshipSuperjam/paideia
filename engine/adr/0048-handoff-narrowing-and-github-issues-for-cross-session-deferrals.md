# ADR 0048 — HANDOFF.md narrowed to session-internal handoffs; GitHub Issues absorb cross-session deferrals

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0042

## Context

The HANDOFF.md surface, originally introduced for partial-closure scenarios, has accumulated a second function: cross-session deferrals — bugs found in one session that the AI judges out-of-scope to fix in-context, tech-debt items observed in passing, cleanup work surfaced during health-checks. Disposition discipline at S-0036 ([`audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py)) catches the form (every new section must carry a valid `**Disposition:**` line) but does not catch the underlying behavior the user has called out repeatedly: every HANDOFF entry creates an implicit "the next session must address this" pressure, and that pressure produces a cleanup treadmill — multiple cleanup/scaffolding sessions per substantive build session, each session clearing one or two HANDOFF items rather than batching.

Concrete telemetry from the planning thread that produced this ADR:

- S-0027 → S-0041 archive shows a 2.25:1 cleanup-to-substantive ratio (9 cleanup, 4 substantive, 3 health-check).
- 5 of those 9 cleanup sessions explicitly displaced roadmap work (the displaced work each time was the next-due build_plan/ chunk).
- HANDOFF.md as of S-0041 carries 4 entries, all dispositioned as `Resolved:`. The post-S-0036 disposition discipline has held — the failure mode is not malformed entries; it is the volume of entries.

The shared mechanism: **the audit enforces form, not intent.** A session can write 10 HANDOFF entries with valid `deferred-with-user-confirmation` dispositions and never have actually consulted the user. The audit passes. The next session sees 10 items waiting and feels obligated to address them.

The user's framing identifies the underlying pattern: deferrals will happen — both because LLM-trained behavior favors task-completion-via-shortest-viable-path, and because some deferrals are genuinely warranted under the three named exceptions (substantial scope, contract change, budget cap reached). The intervention point is not "prevent deferrals entirely" — that fight is unwinnable. The intervention point is the **destination**: route deferrals somewhere that batches naturally, gives the user backlog visibility, and supports cleanup-batch sessions instead of cleanup-treadmill sessions.

GitHub Issues already exists. The repo (`https://github.com/StarshipSuperjam/paideia`) is on GitHub. The `gh` CLI is available locally. Issues support labels (label-based batching), bodies (self-contained context), and the `gh issue list` query surface (boot-time backlog visibility). The infrastructure is already paid for; the work is wiring it in.

## Decision

The project narrows HANDOFF.md's scope and routes cross-session deferrals to GitHub Issues. Four mechanisms land:

### 1. HANDOFF.md scope narrows to session-internal handoffs only

HANDOFF.md is reserved for **partial-closure scenarios** — work the next session must pick up immediately because the current session was halted at a sensible boundary mid-work (per CLAUDE.md "Budget guidance"), or because the closing session genuinely needs the next session to take a hand-off action before doing anything else (a shared-state recovery procedure in flight, an external dependency mid-coordination).

Cross-session deferrals — bugs, tech-debt, cleanup, enhancements, health-check findings — route to GitHub Issues instead. The default is `gh issue create` with appropriate labels, not a HANDOFF.md section.

The four pre-existing HANDOFF.md dispositions remain valid for any session-internal handoff that genuinely needs the file. New: `tracked-as-issue #<num>` joins the disposition vocabulary, recording cases where a HANDOFF entry was authored before realizing the work was cross-session and the right destination was an Issue.

### 2. Issue label taxonomy

A small, deliberate label set with well-defined semantics:

- **`bug`** — code or behavior that violates a contract.
- **`enhancement`** — a desired addition that doesn't exist yet.
- **`tech-debt`** — code or structure that works but has known fragility.
- **`cleanup`** — small, well-scoped maintenance items that batch naturally (the primary candidate for cleanup-batch sessions).
- **`health-check-finding`** — surfaced by a health-check audit; downstream of a cadence-fired audit session.
- **`upstream`** — the bug is real and affects the project but is not in-project actionable (e.g., the mempalace wing-filter and wing-naming bugs from S-0040). Pairs with `bug` typically; signals "do not pick this up in a cleanup batch."
- **`priority:urgent`** — used sparingly. Triggers the LOUD boot surface. Reserved for items that block other work or where silent persistence has a real cost.

Labels are mutually compatible (one issue may carry multiple labels, e.g., `bug` + `upstream`). The taxonomy is open to refinement without superseding this ADR — adding a label is a workflow change, not a contract change.

### 3. Boot-time backlog visibility

The `SessionStart` hook ([`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) per [ADR 0043](0043-hook-architecture.md)) gains two surfaces sourced from `gh issue list`:

- **Default FYI line, always shown:** `[session-start] Issues backlog: N bugs, N tech-debt, N cleanup, N enhancement (M urgent).` Single line, low ceremony. The user sees backlog growth across sessions without it dominating the boot output.
- **Urgent LOUD block, only when `priority:urgent` count > 0:** the same surface treatment as ADR 0045's hard-broken probe findings — multi-line attention block listing each urgent issue's `#<num>: <title>` plus its non-priority labels. Forces visibility on items that need attention now.

The mechanism is non-blocking. A `gh` failure (no auth, no network, repo not on GitHub) emits a stderr note and the boot proceeds — the visibility surface is best-effort, not load-bearing.

### 4. Scope-collision detection at first commit

A new helper ([`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py)) runs from the pre-commit hook on the first commit after the eager-claim — the moment when `engine/session/current.json`'s `declared_scope` field is freshly written (per ADR 0049, sibling to this one). Strategy:

1. Extract keywords from `declared_scope` (whitespace-tokenized, lowercase, drop common stopwords).
2. Collect file paths from this commit's `git diff --cached --name-only`.
3. Query open issues whose body contains any extracted keyword OR any touched file path.
4. Soft-warn per match: `[validate] Open issue #<num> "<title>" appears to touch this session's scope: <matched-keyword|file-path>.`

The collision warning catches the case the user specifically named in the planning thread: starting work on something that depends on a broken thing nobody flagged. Non-blocking; informational. The session decides whether to fix the colliding issue first, in parallel, or to proceed and trust the existing scope is independent.

## Consequences

The deliverables this ADR commits to all land at S-0042:

- **New:** [`engine/operations/issue-discipline.md`](../operations/issue-discipline.md) (Layer 1 source-of-truth on when HANDOFF vs. Issue, label taxonomy, batch workflow), [`engine/tools/scan_issue_backlog.py`](../tools/scan_issue_backlog.py), [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py), tests for both new tools.
- **Modified:** [`engine/tools/audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py) (fifth disposition pattern `tracked-as-issue #<num>` added to `_VALID_DISPOSITION_PATTERNS`; hint message at session-shutdown grows the fifth bullet), [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) (calls `scan_issue_backlog.py` after the cadence/probes block; surfaces the FYI line plus LOUD block when urgent count > 0), [`engine/tools/validate.py`](../tools/validate.py) (runs `scan_issue_collisions.py` from the first-commit path; new `issue_collision` soft-warn category in [`engine/operations/tools-validate-interpretation.md`](../operations/tools-validate-interpretation.md)), [`CLAUDE.md`](../../CLAUDE.md) "Default to fix-in-context" section (HANDOFF vs. Issue routing decision), [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) (mirror the routing change).

CLAUDE.md's "Posture vs machinery" section grows another row: cross-session-deferral routing moves from posture (the AI was supposed to know HANDOFF was for session-internal handoffs only) to machinery (the disposition vocabulary, the Layer 1 ops doc, the batch workflow, the boot visibility surface, and the collision detection are mechanical surfaces the AI cannot drift past).

The validator's check count rises from 17 to 18 (`issue_collision`). Default-mode runtime gains the cost of a `gh issue list` JSON fetch (~200ms typically; bounded by GitHub API latency). This is comfortably within the 3s pre-commit budget. A `gh` failure emits a stderr note and the check is skipped — non-blocking.

The label taxonomy is created during S-0042 verification via `gh label create`. Subsequent label additions are workflow changes, not contract changes; this ADR does not need supersession to add or rename a label.

The wing-filter and wing-naming bugs from the S-0040 HANDOFF entry are filed as the first real Issues during S-0042 verification — labels `bug` + `upstream`, body cross-references the HANDOFF entry and the workaround in [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md). This serves both as a test of the full `gh issue create` flow and as a permanent visibility surface for a known-active limitation that currently lives only in resolved-HANDOFF + ops-doc form.

The intervention does **not** fix the underlying LLM-trained tendency toward descoping. Sessions will still attempt to defer work when fix-in-context is the right call. What this ADR does is reroute the inevitable deferrals into a destination that supports user-controlled batching, surfaces cumulative backlog as a visible signal at every boot, and warns when a session's scope appears to depend on something already known broken. The user retains the load-bearing pushback responsibility that CLAUDE.md's standing pushback rule formalizes; this ADR makes that pushback better-informed by surfacing the data the user needs.

### Amendment at S-0051: FYI line corrected; taxonomy extended; community labels dropped

The original FYI line (`N bugs, N tech-debt, N cleanup, N enhancement (M urgent)`) had two defects discovered during the S-0051 audit:

1. `count_by_label` collected 6 type categories at the time, but `format_fyi_line` emitted only 4. `health-check-finding` was silently suppressed — a count that mattered for cadence-fired audits never reached the surface.
2. `bug` issues that were also tagged `upstream` folded into the bug count without disambiguation. A reader scanning "3 bugs" had no signal that 2 of them might be upstream-blocked and therefore not in-project actionable.

The corrected line emits 7 type categories (`N bugs, N tech-debt, N cleanup, N enhancement, N health-check, N docs, N question`), subtracts upstream-tagged bugs from the bug count, and surfaces the upstream total separately in the parenthetical: `(M urgent; K upstream-blocked)`. The behavior is now: a reader sees the in-project actionable bug count and the upstream-blocked count as separate signals. The 7th and 8th categories (`docs`, `question`) reflect taxonomy additions made the same session — `documentation` and `question` labels gained authoring procedures in [`engine/operations/issue-discipline.md`](../operations/issue-discipline.md) for doc-specific work and in-band uncertainties respectively.

Two GitHub stock community labels (`good first issue`, `help wanted`) were dropped via `gh label delete` during the same session — they had never been applied and have no plausible trigger in a solo-developer + AI workflow. Three reactive-only stock labels (`duplicate`, `invalid`, `wontfix`) were retained and explicitly framed in `issue-discipline.md` as triage-time-applied (no authoring procedure). `gh label list` now reflects 12 labels: 8 type + 1 priority + 3 reactive-only.

This is an amendment, not a supersession — adding/dropping labels and correcting a surface format are workflow changes, not contract changes (the ADR taxonomy clause already declared them so).

## See also

- [ADR 0040](0040-build-readiness-gate-before-substantive-build-sessions.md) — sibling intervention; the gate prevents some deferrals by surfacing decisions before authoring; this ADR handles the deferrals that survive.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — the `issue_collision` soft-warn inherits the canon (archive-as-canon, 3-of-5 surface threshold, max-count aggregation).
- [ADR 0043](0043-hook-architecture.md) — the `SessionStart` hook this ADR extends; the FYI line and LOUD block sit alongside the cadence and persistent-warn surfaces.
- [ADR 0045](0045-shared-state-integrity-discipline.md) — surface treatment for the urgent-issue LOUD block borrowed from this ADR's hard-broken probe surface pattern.
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — sibling intervention authored in the same session; provides the `declared_scope` field this ADR's collision detection consumes.
