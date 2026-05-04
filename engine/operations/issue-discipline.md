# issue-discipline

> Layer 1 source-of-truth for the HANDOFF.md / GitHub Issues split per [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md). Names when each surface is the right destination, the label taxonomy, the body shape Issues must follow, and the cleanup-batch workflow.

## Why two surfaces, not one

HANDOFF.md and GitHub Issues serve adjacent but distinct purposes. Conflating them produces the failure mode ADR 0048 names: every HANDOFF entry creates implicit pressure for the next session to address it; that pressure produces a cleanup treadmill (multiple sessions clearing one item each instead of one session batching).

- **HANDOFF.md** is for *immediate, session-internal handoffs* — the next session must pick this up before doing anything else, because the closing session was halted at a sensible boundary mid-work, or because there's an in-flight recovery procedure, or because the work-item ownership transfers atomically across sessions.
- **GitHub Issues** is for *cross-session backlog* — bugs, tech-debt, cleanup, enhancements, health-check findings. The work belongs to no specific session; it sits in a labelled queue until a session decides to address it (often as a batch).

The decision rule: **if the next session must address this before doing its own scoped work, HANDOFF.md. Otherwise, Issue.**

## When to use HANDOFF.md

A new HANDOFF.md section is appropriate when *all three* hold:

1. **Immediacy.** The next session must pick this up before its own scoped work, not when convenient.
2. **Ownership transfer.** This work belongs to whichever session opens next, not to a backlog queue.
3. **Session-context dependency.** The information needed to act is best understood in the context of the session that surfaced it; offloading to a backlog risks losing the framing.

Concrete shapes that meet all three:

- Partial-closure: the current session hit its budget cap mid-work; the next session must continue from where this one left off. The `outcome_summary` and `STATE.md` next-session work item carry the structural pointer; HANDOFF carries any context the structural pointers can't fit.
- Mid-recovery handoff: a shared-state recovery is in flight (e.g., a `core.bare = true` repair or a chromadb segment rebuild) that the next session must complete before claiming a slot.
- Cross-session coordination: an external dependency (Apple Developer Program enrollment, a Supabase project setup) that the next session must check on before proceeding.

If any of the three doesn't hold, the right destination is an Issue.

## When to use a GitHub Issue

A new Issue is appropriate when:

- The work is real and worth tracking but doesn't need to be the next session's first move.
- The work could batch with similar items in a future cleanup session.
- The information needed to act can be captured self-contained in the Issue body.

Concrete shapes that fit:

- A bug observed in one part of the codebase while working in another (out-of-scope, but real).
- Tech-debt surfaced by health-check or by code-review in passing.
- A small cleanup item discovered during unrelated work.
- A feature idea that needs to land but doesn't need to land *now*.
- A health-check finding that suggests follow-up.

The default for cross-session deferrals is `gh issue create`. HANDOFF is the exception, not the rule.

## Label taxonomy

Eight type labels and one priority label (extended at S-0051):

| Label | Meaning |
|---|---|
| `bug` | Code or behavior that violates a contract. |
| `enhancement` | A desired addition that doesn't exist yet. |
| `tech-debt` | Code or structure that works but has known fragility. |
| `cleanup` | Small, well-scoped maintenance items that batch naturally. |
| `health-check-finding` | Surfaced by a health-check audit; downstream of a cadence-fired audit session. |
| `upstream` | The bug is real and affects the project but is not in-project actionable. Pairs with `bug` typically; signals "do not pick this up in a cleanup batch." |
| `documentation` | Doc improvements, doc bugs, doc cleanup. Use when the work is doc-specific and batches naturally with other doc work (ADR refresh sweeps, ops-doc restructures, cross-references audits). Compatible with `cleanup` for small batchy items. |
| `question` | A genuine open question that needs deliberation before action takes shape. Pairs with another type label when the type is known but the shape isn't. Resolves by becoming an ADR (decision settled), being relabeled to a typed action issue, or being closed `wontfix` (decision made: no action). |
| `priority:urgent` | Used sparingly. Triggers the LOUD boot surface. Reserved for items that block other work or where silent persistence has a real cost. |

Labels are mutually compatible. An issue may carry multiple type labels (e.g., `bug` + `tech-debt` for a bug that won't get fixed soon and now counts as debt). The taxonomy is open to refinement; adding a label is a workflow change, not a contract change (no ADR needed).

`priority:urgent` is the only priority label. Resist creating a multi-tier priority scheme — every label that exists must be used consistently or the noise eats the signal. The two-tier "urgent or not" matches the boot surface's two-tier "FYI or LOUD."

### Reactive-only labels

Three GitHub stock labels are retained as reactive-only — applied at triage time, not authored:

- `duplicate` — applied when reading an existing issue and recognizing it duplicates another.
- `invalid` — applied when reading an issue and concluding it doesn't describe a real problem.
- `wontfix` — applied when deciding (often at issue close) that the work won't be done.

These do not have authoring procedures because the trigger is reading an existing issue, not surfacing a new one. They appear in `gh label list` for triage convenience and are not surfaced in the boot backlog count.

The S-0051 audit dropped two community labels that had no project-applicable trigger: `good first issue` and `help wanted`. The project is solo-developer + AI; these are recreated via `gh label create` if collaboration scope changes.

## Issue body shape

Every Issue must be self-contained — a future session reading it cold should have everything needed to act without re-deriving context. The body sections below are required:

```markdown
## Context

What was the AI/user doing when this surfaced? One paragraph.

## Symptom

What happens that shouldn't (for bugs), or what's missing that should exist
(for enhancements/tech-debt/cleanup), in concrete observable terms.

## Proposed approach

What seems like the right shape of the fix or addition. May be loose if
the right approach genuinely isn't known yet — flag the uncertainty.

## Affected files

List of repo-relative file paths the issue touches. One per line. The
collision-detection scanner uses these for path-overlap matching against
session scope.

- path/to/file.py
- path/to/other/file.md

## Cross-references

- Related HANDOFF.md entries
- Related ADRs
- Related session archives
- Related external bug reports (for `upstream` issues)
```

The "Affected files" section is load-bearing for the collision-detection scanner. If the affected files genuinely aren't known (a high-level enhancement idea that hasn't surfaced concrete touchpoints), the section says `- (not yet identified)` rather than being omitted — the literal text signals to the scanner there's nothing to match.

## Creating an Issue

```bash
gh issue create \
  --title "<short imperative>" \
  --label "bug,upstream" \
  --body "$(cat <<'EOF'
## Context

...

## Symptom

...
EOF
)"
```

The CLI returns the new issue's URL; capture the `#<num>` for any HANDOFF disposition that references it.

## Cleanup-batch workflow

A session dedicated to clearing backlog items follows this shape:

1. **List candidates.** `gh issue list --label cleanup --state open --json number,title,body,labels` returns the queue. Filter further by additional labels if narrowing (e.g., `--label cleanup --label health-check-finding`).
2. **Pick a batch.** Choose N items that share a touch surface (same module, same kind of fix). The batch's `declared_scope` at boot names the chosen issues by number.
3. **Address each item.** Per item: read the body, make the fix, reference the issue in the commit message (`Fixes #<num>` or `Refs #<num>`).
4. **Close issues.** `gh issue close <num>` with an optional `--comment` referencing the resolving commit. GitHub auto-closes when a commit message uses `Fixes #<num>` and lands on the default branch.
5. **Shutdown audit.** The session's `outcome_summary` records the batch — issue numbers addressed, any that escalated to substantive work that didn't fit (re-opened with a comment).

Cleanup-batch sessions are user-initiated, not auto-triggered. The boot surface's FYI line carries the count; the user decides when the count crosses a threshold worth dedicating a session to.

## Boot-time backlog visibility

Per ADR 0048, the `SessionStart` hook emits the backlog count at every boot:

- **Default FYI line, always shown:** `[session-start] Issues backlog: N bugs, N tech-debt, N cleanup, N enhancement, N health-check, N docs, N question (M urgent; K upstream-blocked).` Single line, low ceremony. Bugs that are also `upstream`-tagged are subtracted from the bug count and surfaced separately as `upstream-blocked` — a reader scanning the surface sees the actionable bug count, not a noise-padded total. Updated at S-0051 from the original 4-category form.
- **Urgent LOUD block, only when `priority:urgent` count > 0:** the same surface treatment as ADR 0045's hard-broken probe findings — multi-line attention block listing each urgent issue's `#<num>: <title>` plus its non-priority labels.

A `gh` CLI failure (no auth, no network, repo not on GitHub) emits a stderr note; the boot proceeds. The visibility surface is best-effort.

## Scope-collision detection at first commit

Per ADR 0048, [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) runs from the pre-commit hook on the first commit after the eager-claim. The check soft-warns when an open issue body contains either a keyword from the session's `declared_scope` (per ADR 0049) or a file path from this commit's staged diff. Output:

```
[validate] Open issue #<num> "<title>" appears to touch this session's scope: <matched-keyword|file-path>.
```

Non-blocking. The session decides whether to fix the colliding issue first, in parallel, or to proceed and trust the existing scope is independent.

## Migration from existing HANDOFF.md

The four HANDOFF.md entries as of S-0041 are all dispositioned `Resolved`; no migration to Issues is needed for already-resolved entries. Future sessions follow this doc's discipline at authoring time — HANDOFF only when all three immediacy/ownership/context criteria hold.

The `tracked-as-issue #<num>` disposition exists for the case where a HANDOFF section was authored before realizing the work was cross-session. The session creates the Issue, references it via the new disposition, and the audit accepts the entry as cleanly handed off.

## See also

- [ADR 0048](../adr/0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — the citable contract this document operationalizes.
- [ADR 0049](../adr/0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — sibling intervention; the `declared_scope` field this doc's collision-detection consumes.
- [`engine/tools/audit_handoff_dispositions.py`](../tools/audit_handoff_dispositions.py) — the disposition audit at session shutdown; accepts the new `tracked-as-issue #<num>` form.
- [`engine/tools/scan_issue_backlog.py`](../tools/scan_issue_backlog.py) — boot-time backlog scanner.
- [`engine/tools/scan_issue_collisions.py`](../tools/scan_issue_collisions.py) — first-commit collision scanner.
- [`HANDOFF.md`](../../HANDOFF.md) — the file whose scope this doc narrows.
- [`CLAUDE.md`](../../CLAUDE.md) "Default to fix-in-context" — the standing rule this doc complements.
