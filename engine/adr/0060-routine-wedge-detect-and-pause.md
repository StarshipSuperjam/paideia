# ADR 0060 — Routine wedge detect-and-pause

- **Status:** Accepted
- **Date:** 2026-05-10
- **Deciders:** S-0118

## Context

S-0117 was eager-claimed by routine fire at 2026-05-10T03:00Z for `AUDIT-HT` (final routine evidence file in T-PHASE-5-AUDIT). The session got through step 8 (eager-claim push `e0b4a27`) but never reached step 9 — likely halted on context cap mid-authoring of the largest evidence deliverable (96 edges + 10 nodes + 3 syllabus traces). State persisted: `register_state.json.current_status: in_progress`, `current.json.id: S-0117`, `auto_target.json[AUDIT-HT].status: in_progress`, no archive.

The routine-mode-lifecycle skill body (`.claude/skills/routine-mode-lifecycle/SKILL.md`) had no recovery branch for "previous routine fire halted post-eager-claim." Step 5 eligibility selection requires `status == pending`; with AUDIT-HT pinned at `in_progress` no task was eligible. Every subsequent hourly fire of `paideia-engine-loop` ran through the boot procedure, found no eligible task at step 5, wrote a HANDOFF entry, and exited — producing one HANDOFF append per hour with no clearing mechanism. The wedge persisted until Issue #58 was filed and the user paused the routine and adjudicated the recovery interactively at S-0118.

The clean recovery requires master-plan-revision-class judgment that routine mode explicitly defers (per [ADR 0051](0051-routine-mode-and-engine-loop.md)). Routine mode CAN modify `auto_target.json[*].status` and `[*].blocked_reason`, but changing AUDIT-HT's status from `in_progress` to anything else from a non-S-0117 session declares S-0117's claim invalid without S-0117's assent — that's overstepping in the same way running shutdown on S-0117 would be. The detect-and-pause approach this ADR specifies stays within those constraints: read-only on shared state apart from idempotent HANDOFF/Issue authoring.

The S-0117 wedge itself was resolved at S-0118 boot via an administrative-close commit (`48a6ac9`) that archived `current.json` with `status: closed_void`, flipped `register_state.current_status` to `closed`, and decomposed AUDIT-HT into AUDIT-HT-1 (hubs 1–5) + AUDIT-HT-2 (hubs 6–10 + 3 traces) so the next routine fire would claim a smaller deliverable under context cap. The decomposition prevents recurrence-by-the-same-cause; this ADR mechanizes detect-and-pause so any future halted-routine wedge auto-resolves to a single Issue + a single HANDOFF entry rather than spamming HANDOFF appends every hour until a human notices.

## Decision

Insert a new boot step `0c. Wedge detection` between step 0b (concurrency lock acquisition per ADR 0052) and step 1 (target precondition check) in the routine-mode-lifecycle skill body. The step delegates to a new mechanical tool, `engine/tools/routine_wedge_detect.py`, which inspects shared state for the wedge shape and routes the routine to a clean exit when detected.

The mechanism is **detect-and-pause**, not auto-administrative-close. See "Alternatives considered" below for why.

### Wedge shape (mechanical predicate, all conjuncts)

A halted-routine wedge is detected when ALL of the following hold:

1. `engine/session/register_state.json` exists and parses, with `current_status == "in_progress"`.
2. `engine/session/current.json` exists and parses, with `id` matching `^S-\d{4}$` and `status == "in_progress"`.
3. The current.json's `id` does NOT have a corresponding `engine/session/archive/<id>.json` at HEAD.
4. The lock at the path `routine_lock.py` uses (per ADR 0052) is acquirable — i.e., no other routine session currently holds the worktree.
5. The current.json names a `task_id` (routine-mode session field), AND `auto_target.json[task_id].status == "in_progress"`.
6. HEAD is at-or-behind `origin/main` with no local commits ahead. (If HEAD is ahead, the calling routine has uncommitted lifecycle work; that's not a wedge — it's a partial-shutdown edge case the boot-freshness gate handles per ADR 0052.)

Any conjunct missing → not a wedge → tool exits 0 → routine boot proceeds to step 1 normally.

All conjuncts hold → wedge → tool authors idempotent artifacts and exits 2 → routine boot exits cleanly without claiming.

### Idempotent artifact authoring

When a wedge is detected, the tool authors two artifacts; both are idempotent — second-and-subsequent invocations detect the existing artifact and skip authoring:

**(a) GitHub Issue** — search by title pattern `^Routine wedge: halted prior session leaves <task_id> in_progress with no recovery path` (the canonical title from Issue #58). If a matching open issue exists, do NOT file a duplicate. If none, run `gh issue create` with labels `bug` + `priority:urgent` and a body referencing the wedge state (current.json id, task_id, register_state contents) plus a link to ADR 0060 for adjudication context.

**(b) HANDOFF.md entry** — search the file body for `### Routine wedge detected (S-<id>)` (canonical heading from this ADR). If a matching section exists, do NOT append a duplicate. If none, append a new section naming the wedged session, the task, the suggested recovery (administrative close per the S-0117/S-0118 precedent — this ADR + the S-0117 administrative-close commit shape are the worked example), and a `**Disposition:** tracked-as-issue #<n>` line citing the Issue from step (a).

The pre-commit hook's `audit_handoff_dispositions.py` (per CLAUDE.md "Default to fix-in-context") validates the disposition line. The HANDOFF append is followed by an immediate commit with subject `chore(session): wedge-detect-and-pause for S-<id>` — this commit is the only mutation the tool makes to the repo; everything else is read-only.

### Rollback safety

The tool does NOT modify `register_state.json`, `current.json`, `auto_target.json`, the wedged session's archive, or any non-`HANDOFF.md` tracked file. The HANDOFF append commit is the entire mutation surface. If the tool is interrupted mid-author or mid-commit, no shared state is corrupted — the worst case is no Issue / no HANDOFF entry on the first detection (subsequent fires will re-attempt). If `gh issue create` fails (no auth, network outage), the tool logs the failure to stderr but proceeds to author the HANDOFF entry without an Issue cross-reference; the next interactive `/start-engine` boot's Issue-backlog scan will surface the wedge from HANDOFF alone.

### Tool exit codes

- `0` — no wedge detected. Routine boot proceeds to step 1.
- `2` — wedge detected; idempotent artifacts authored (or already present). Routine boot calls `routine_lock.py release` and exits 0 cleanly without claiming a slot. The harness's hourly fire produces a brief log and exits; no HANDOFF spam.
- `3` — refusal due to ambiguous shape (multiple conjuncts borderline; e.g., HEAD ahead of origin/main with a non-eager-claim subject). Tool refuses to make a wedge call; routine boot writes a HANDOFF entry naming the ambiguity and exits without claiming. The next interactive session adjudicates manually.
- `5` — generic failure (gh CLI invocation error, file system error). Tool surfaces the cause to stderr; routine boot writes HANDOFF and exits cleanly.

## Consequences

- **HANDOFF spam eliminated.** Future halted-routine wedges produce exactly ONE Issue + ONE HANDOFF entry across all subsequent hourly fires until a human adjudicates. The Issue carries `priority:urgent` so it surfaces in the SessionStart hook's backlog warning at every interactive boot.
- **Routine fires past a wedge cost nothing structural.** Each fire runs the boot through step 0c, hits the wedge predicate, sees the existing Issue/HANDOFF (idempotent skip), and exits in well under one second. Network call to `gh` is the only non-trivial cost on first detection; subsequent fires are file-system-only.
- **The wedge state itself remains for human adjudication.** This is deliberate. Auto-administrative-close (the alternative) would synthesize an archive without the halted session's `outcome_summary` input — that's the load-bearing field for downstream telemetry (soft-warn lifecycle per ADR 0042, scope-erosion signal per ADR 0049). Synthesizing it from cold context produces incorrect telemetry that downstream sessions read as truth.
- **First-exercise readiness gate per [ADR 0053](0053-mechanism-first-exercise-gate.md).** A new readiness note at `engine/build_readiness/routine_wedge_detect_first_exercise.md` records the trigger criterion (next routine fire that would otherwise hit a wedge condition) and the Tier 1 / Tier 2 / Tier 3 triage. The first real-world exercise of the wedge-detect path closes the readiness note.
- **`engine/operations/routine-mode-operations.md` is the Layer 1 source-of-truth doc** for the boot step; the skill body at `.claude/skills/routine-mode-lifecycle/SKILL.md` mirrors the doc per ADR 0044 (doc → skill, never reverse).
- **Defense-in-depth coverage.** The S-0117 wedge had no detection at any layer: the boot-freshness gate (ADR 0052) checked `origin/main` freshness but not whether `register_state.in_progress` reflected an active session; the concurrency lock (ADR 0052) only matched true concurrent fires; `validate.py --health-probe-only` checked palace and repo health but not session-state coherence. This ADR closes the coherence gap.
- **MemPalace `decision`-tagged drawer** captured at S-0118 close per the project's two-layer decision-recording rule, summarizing the wedge-detect-and-pause approach and why auto-administrative-close was rejected.

### Files affected

- New: `engine/adr/0060-routine-wedge-detect-and-pause.md` (this file).
- New: `engine/tools/routine_wedge_detect.py`.
- New: `engine/tools/test_routine_wedge_detect.py`.
- New: `engine/build_readiness/routine_wedge_detect_first_exercise.md`.
- Modified: `engine/operations/routine-mode-operations.md` — insert step 0c.
- Modified: `.claude/skills/routine-mode-lifecycle/SKILL.md` — mirror step 0c.

## Alternatives considered

### Auto-administrative-close (aggressive recovery)

**What it would do.** On wedge detection, the current routine fire administratively closes the prior slot: archive `current.json` to `archive/<id>.json` with `status: closed_partial` or `closed_void`, flip `register_state.current_status` to `closed`, mark the wedged task `blocked: <reason>` (or unflip its in_progress status), commit, push. Future fires find clean state and proceed normally.

**Why rejected.**

1. **Outcome-summary synthesis.** The session-archive structured-fields contract (`outcome_summary_soft_warns`, `outcome_summary`, `mempalace_activity`, `next_session_handle`, `mode`) requires non-trivial values that depend on what the halted session did. Synthesizing them from cold context — with no access to the halted session's transcript or mempalace activity — produces archive data that downstream sessions consume as truth. The persistent-warn surface (ADR 0042), scope-erosion signal (ADR 0049), and MemPalace adoption checks (ADR 0056) all read structured archive fields. Bad synthesis silently corrupts those signals.
2. **Routine-mode posture violation.** Master-plan revisions are explicitly reserved for interactive sessions per ADR 0051. Auto-administrative-close from a routine session would close a slot AND modify the master plan (via `auto_target.json[*].status` reset on the wedged task). The first action is mechanically bounded — a routine session can edit `register_state.json` — but the second crosses into adjudication: choosing "reset to pending" vs "decompose" vs "deliver interactively" is a judgment call that requires human input.
3. **Recovery-recovery loop risk.** If auto-close itself fails (network error mid-push, filesystem error mid-archive-write), the next routine fire would face TWO wedges: the original halted session AND the failed auto-close. The detect-and-pause mechanism has no recursive failure mode: a failed Issue file is silently retried; a failed HANDOFF append leaves shared state untouched.
4. **Loss of the `closed_partial` archive contract.** Per CLAUDE.md "Budget guidance" and `session-shutdown-sequence.md`, `closed_partial` is reserved for sessions that legitimately finish partial work and document the partial-completion notes themselves. Auto-administrative-close stamps `closed_partial` without partial work being authored — diluting the archive's signal.

The auto-close path could be revisited if (a) detect-and-pause produces enough wedge frequency that a human cleanup queue accumulates, AND (b) a synthesis approach for the structured fields earns adoption (e.g., reading the halted session's `current_mempalace.jsonl` and `outcome_summary` placeholder if present). Neither condition is currently true.

### Wedge-detect-only (no pause; just file Issue and proceed to step 1)

**What it would do.** On wedge detection, file the Issue (idempotent) but continue the routine boot to step 1. The eligibility check at step 5 would then fail naturally (no `pending` task), and the routine would write its current HANDOFF "no eligible task" message and exit.

**Why rejected.** The current behavior IS this — and it produces HANDOFF spam. The point of step 0c is to stop step 5 from re-firing the spam path. Detect-and-pause is the minimum mechanism that suppresses the spam; detect-only doesn't.

### Boot-freshness-gate amendment (extend ADR 0052 instead)

**What it would do.** Add the wedge-shape check inside `routine_boot_freshness.py` as another conjunct of "fresh state."

**Why rejected.** The boot-freshness gate's contract is narrow: HEAD is at `origin/main` (mechanically advanced via `git merge --ff-only`). Adding shape conjuncts that aren't about HEAD freshness expands the tool's responsibility surface in a way ADR 0052 deliberately bounded ("eliminating the staleness vector"). A separate tool with a separate ADR keeps each mechanism's contract reviewable.

## References

- [Issue #58](https://github.com/StarshipSuperjam/paideia/issues/58) — the wedge bug report (S-0117).
- S-0117 administrative-close commit `48a6ac9` — the worked example of the recovery shape this ADR mechanizes detection for.
- [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) — soft-warn lifecycle and structured-field archive contract (load-bearing reason auto-administrative-close was rejected).
- [ADR 0044](0044-skill-conversion-recipe-vs-reference.md) — Layer 1 doc → Skill mirror policy.
- [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) — issue-discipline + HANDOFF disposition contract.
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — routine-mode posture (master-plan revision restriction).
- [ADR 0052](0052-routine-boot-freshness-and-concurrency-defense.md) — three-layer routine-boot defense; companion mechanism.
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — mechanism-first-exercise gate.
- [ADR 0056](0056-mempalace-mechanical-adoption-checks.md) — mempalace adoption checks (load-bearing for outcome-summary synthesis rejection).
