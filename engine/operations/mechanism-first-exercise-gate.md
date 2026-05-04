# Mechanism-first-exercise gate — pre-flight before unattended use of a novel cross-cutting mechanism

> The operational surface for [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). The gate runs once per qualifying mechanism, before that mechanism is used unattended for the first time. Its deliverable is a gate report at `engine/build_readiness/<mechanism>_first_exercise.md` that the next session using the mechanism (in unattended mode) reads at boot.
>
> Sibling to [`build-readiness-gate.md`](build-readiness-gate.md). Both gates triage findings into Tier 1 / Tier 2 / Tier 3, both produce reports under `engine/build_readiness/`, both are user-conversational rather than auto-mode. They differ in trigger: build-readiness is *phase-triggered*; this gate is *mechanism-triggered*. They can both apply to a single phase if a new mechanism lands as part of that phase.

## When the gate fires

The gate fires when a new mechanism qualifies as "novel cross-cutting" per ADR 0053's trigger criterion. The criterion is disjunctive — any single trigger suffices:

| Trigger | Examples that would qualify |
|---|---|
| Introduces a new session mode | `routine` joining `build`/`exploration` (ADR 0051 — would have qualified) |
| Introduces a new validator soft-warn category that depends on session-side discipline | `descope_unflagged` (ADR 0049 — qualified) |
| Introduces a new state file the boot procedure reads | `auto_target.json` (ADR 0051 — qualified), `routine.lock` (ADR 0052 — qualified) |
| Authoring ADR's Consequences list spans ≥ 3 ops docs OR ≥ 5 tooling files | ADR 0045 shared-state integrity (would have qualified — touches scrub_env, mempalace-hook-wrapper, validate.py health probes, plus 3 ops docs) |

The check happens at ADR authoring time. Cross-cutting ADRs must include a trigger-criterion evaluation block in their Consequences section — either declaring "qualifies; gate session needed before unattended use" with the mechanism named, or "does not qualify because [criterion check]" with the negative finding stated. Silent omission is the failure mode this gate exists to prevent.

The gate fires **once** per qualifying mechanism, not per-phase or per-session.

## Procedure

### 1. Confirm the trigger and read the authoring ADR

The gate session opens by reading the ADR that introduces the mechanism. Confirm the trigger-criterion evaluation block (from ADR 0053) is present and identifies the qualifying trigger(s). Note the mechanism's claimed scope, its authored discipline (procedural rules + mechanical safeguards), and the unattended use case the gate is preparing for.

### 2. Fire the mechanism once interactively against real state

The load-bearing step. Not theoretical analysis — actual end-to-end execution under human observation.

For a routine-mode-style mechanism (the canonical case): the gate session runs the mechanism's boot procedure manually (typing the slash command, walking each step). For a validator-soft-warn-style mechanism: the gate session triggers the warn condition deliberately (write a commit that would fire the warn, observe the surface). For a state-file-style mechanism: the gate session writes the file with realistic contents, runs the boot procedure, observes how the boot reads and acts on it.

The exercise must be against *real state* — the actual repo, the actual DB if applicable, the actual git remote, real worktree shape. Synthetic fixtures are insufficient because the failure modes are real-state failure modes (env vars not propagating to subshells, git fetch behavior under the actual remote config, etc.).

If the mechanism cannot be fired interactively because it requires unattended dispatch (a Claude Code Routine, a cadence-fired scheduled task), the gate session sets up the dispatch in a controlled mode (e.g., Manual cadence with a single user-triggered fire) and observes the result. Unattended *operation* is what the gate validates; unattended *dispatch* is just the trigger.

### 3. Observe and instrument

During the exercise, record what the mechanism actually did:

- What state did each step read?
- What did each step write (files, commits, DB rows)?
- Where did the AI pause for input vs. proceed without input?
- Which tools were invoked, with what arguments, exit codes?
- Where did the discipline machinery fire (validators, hooks, audits)?
- Where did the AI's behavior diverge from the procedural rules in the ADR / Skill?

The findings come from comparing observed behavior against the authoring ADR's claimed contract. Each divergence is a candidate finding.

### 4. Triage findings into Tier 1 / Tier 2 / Tier 3

Same triage rubric as the build-readiness gate (per [`build-readiness-gate.md`](build-readiness-gate.md) §3):

- **Tier 1 — must close before unattended use.** The mechanism cannot run safely without human in the loop until this is fixed. Examples from routine-mode (had this gate existed at S-0045): `SUPABASE_DB_URL` missing from `.env` propagation chain (Issue #7); `check_target.py` queries wrong column (Issue #9); boot doesn't act on staleness warning (Issue #15).
- **Tier 2 — settle in advance and document.** The mechanism could improvise but doing so under unattended pressure produces compound drift. Examples: cadence frequency, lockfile timeout, recovery-path semantics, scope-lock convention edge cases.
- **Tier 3 — name as deferred forward-pointer.** Genuine future-session concern that wouldn't block this gate. Examples: cross-machine coordination, multi-mechanism interaction.

Triage is judgment-bound. The user reviews; user can escalate Tier 2 → Tier 1 or de-escalate Tier 1 → Tier 2 / Tier 3.

### 5. Resolve Tier 1 with the user, conversationally

The gate session is **not auto-mode** — it surfaces judgment calls. For each Tier 1 finding:

1. State the finding with citations and why it matters now.
2. Present resolution options with tradeoffs.
3. Use AskUserQuestion or direct conversation to settle.
4. Author the resolution artifact: the fix lands in this same gate session if it's bounded; otherwise it routes to a tracked Issue with `priority:urgent` and the unattended-use is gated on Issue closure.

The gate session does not push past unresolved Tier 1. If a Tier 1 requires multi-conversation reasoning, the gate session pauses and surfaces "this needs more conversation than this session can hold."

### 6. Author the gate report

`engine/build_readiness/<mechanism>_first_exercise.md`. Same template family as build-readiness reports.

```markdown
# Mechanism-first-exercise gate — <mechanism name>

- **Date:** <YYYY-MM-DD>
- **Session:** S-NNNN
- **Mechanism:** <name from authoring ADR>
- **Authoring ADR:** ADR NNNN
- **Trigger:** <which ADR 0053 sub-criterion qualified the mechanism>

## Exercise summary

<2-3 paragraphs: what was fired, what was observed end-to-end, what worked.>

## Tier 1 findings (must resolve before unattended use)

### Finding 1.1: <short title>
- **Observation:** <what was seen>
- **Why it matters:** <consequence under unattended dispatch>
- **Resolution:** <what was decided, with file citation if landed in this session, OR `tracked-as-issue #NNN` for deferred fix>
- **Status:** resolved-in-session @ SHA / pending-issue-closure / blocked

### Finding 1.2: ...

## Tier 2 decisions (settled in advance)

### Decision 2.1: <topic>
- **Question:** <the in-flight choice the mechanism would otherwise improvise>
- **Decision:** <concrete answer>
- **Rationale:** <why>

### Decision 2.2: ...

## Tier 3 forward-pointers (deferred, named for next session)

- <bullet 1>
- <bullet 2>

## Verdict

<one of: "Mechanism cleared for unattended use as of <date>" | "Mechanism gated on resolution of Tier 1 findings (#NNN, #NNN, ...)" | "Mechanism blocked; requires architectural revision per ADR 0053 amendment workflow">
```

The verdict line is the operational surface the next session reads. Sessions using the mechanism in unattended mode read this report at boot and refuse to proceed if the verdict is gating or blocked.

## Out of scope

- **Mechanism deprecation gate.** This procedure handles adoption only. Removing or replacing a cross-cutting mechanism is a different shape of risk.
- **Phase-triggered work.** That belongs to [`build-readiness-gate.md`](build-readiness-gate.md). The two gates are orthogonal triggers; both can fire for a single phase.
- **Soft-warn introduction without session-side discipline.** A new validator category that the validator itself fully resolves (no AI action required) does not satisfy the trigger criterion and does not need this gate.
- **Back-port to mechanisms that landed before this gate existed.** Per ADR 0053, the trigger-criterion check applies to new ADRs only; existing cross-cutting mechanisms get the check on next-touch (when their ADR is amended).

## Cross-references

- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — the contract this procedure instantiates.
- [ADR 0040](../adr/0040-build-readiness-gate-before-substantive-build-sessions.md) — the analogous phase-triggered gate.
- [`build-readiness-gate.md`](build-readiness-gate.md) — sibling procedure (phase-triggered).
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md), [ADR 0052](../adr/0052-routine-boot-freshness-and-concurrency-defense.md) — the routine-mode case study.
- Issues [#7](https://github.com/StarshipSuperjam/paideia/issues/7), [#8](https://github.com/StarshipSuperjam/paideia/issues/8), [#9](https://github.com/StarshipSuperjam/paideia/issues/9), [#10](https://github.com/StarshipSuperjam/paideia/issues/10), [#15](https://github.com/StarshipSuperjam/paideia/issues/15) — the five routine-mode infrastructure gaps a pre-flight gate would have caught.
