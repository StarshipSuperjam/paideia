# ADR 0052 — Routine-mode boot freshness and concurrency defense

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0055

## Context

[Issue #15](https://github.com/StarshipSuperjam/paideia/issues/15) was filed under the working assumption of an eager-claim *concurrency race*: two routine-mode sessions appeared to fire concurrently against `T-PHASE-5`, both claimed slot S-0054, and one's push to `origin/main` was rejected at FF-merge time, leaving an orphan branch (`claude/mystifying-easley-3f3789`) and worktree behind.

Mid-S-0055 the user corrected the diagnosis: **the prior session had already closed before the loser started**. Push of close-commit `3f17301` to `origin/main` was complete; both sessions were never alive at the same time. The actual failure mode is **boot-time staleness**: the loser routine booted in a worktree whose local HEAD was behind `origin/main` by the winner's three commits. The routine boot procedure read the on-disk `register_state.json`, which still showed `next_id=0054`, and proceeded to "claim" S-0054 again.

The same class of failure was surfaced by S-0051 / [Issue #10](https://github.com/StarshipSuperjam/paideia/issues/10). That issue shipped a staleness check at [`engine/tools/hooks/session-start.sh:98-141`](../tools/hooks/session-start.sh) — but the check is **informational only**: it emits a LOUD stderr attention block when HEAD is behind origin/main and proceeds. The routine-mode-lifecycle Skill has no boot step that acts on the warning. The AI inside the routine session was supposed to read and act, didn't, and produced the orphan.

[ADR 0051](0051-routine-mode-and-engine-loop.md) framed routine-mode's atomicity as "Eager-claim already handles concurrent-session serialization" — true for the canonical state (only one S-N archive can exist per slot) but incomplete: the loser cost (orphan branch + worktree + wasted compute) is real even when the canonical state is correct.

The user's S-0055 in-session direction was to fix the actual diagnosis (staleness) **and** add concurrency defense as belt-and-suspenders so future cadence tightening doesn't expose a real race. The previously-rejected lockfile-and-recovery approach was reinstated under the explicit "true concurrent fires haven't happened yet but I want defense-in-depth before tightening cadence" framing.

## Decision

Three-layer routine-boot hardening, in order of how often each fires:

### Layer 1 — Boot-freshness gate (primary; addresses the actual S-0054 failure mode)

New tool [`engine/tools/routine_boot_freshness.py`](../tools/routine_boot_freshness.py). Runs as Skill step 0a, before any shared-state read.

1. `git fetch --no-tags --quiet origin main` — best-effort. Network failure emits a stderr note and exits 0.
2. Compare HEAD to `origin/main`:
   - HEAD ≥ origin/main → no-op, exit 0.
   - HEAD strictly behind (FF possible) → `git merge --ff-only origin/main`, log `[routine-boot-freshness] fast-forwarded N commit(s)`, exit 0.
   - HEAD diverged from origin/main → exit 2. Routine boot must NOT proceed; write HANDOFF and exit cleanly.

Fast-forward is bounded — `git merge --ff-only` moves HEAD forward without merging or discarding anything — and is safe to mechanize. Diverged HEAD (impossible to ff) is a real anomaly that needs human adjudication; routine sessions cannot resolve it.

### Layer 2 — Lockfile serialization (defense-in-depth for true concurrent fires)

New tool [`engine/tools/routine_lock.py`](../tools/routine_lock.py). Runs as Skill step 0b.

`O_EXCL` atomic write to `.claude/routine.lock` containing `{pid, started_at_iso}`. If the lockfile exists and is fresh (mtime within `stale_after` seconds, default 3600 = 1 hour to cover worst-case session length), `acquire` returns False; the routine logs "another routine in progress, exiting cleanly" and exits without claiming. If the lockfile exists but is stale, `acquire` evicts it (logs the eviction) and re-acquires fresh. Released as the very last action of step 11 shutdown.

The lockfile is gitignored (runtime artifact, never tracked). It is per-checkout state, not a distributed lock; cross-machine concurrency would still rely on the eager-claim "first push wins" property as the residual.

### Layer 3 — Loser-recovery script (residual defense)

New tool [`engine/tools/routine_eager_claim_recovery.py`](../tools/routine_eager_claim_recovery.py). Invoked from Skill step 8's push-rejection branch.

Mechanically verifies the rejection has the eager-claim-race shape:
- HEAD has exactly one commit ahead of origin/main
- That commit's subject matches `chore(session): eager-claim S-NNNN — ...`
- origin/main HEAD also has an eager-claim commit for the **same slot**

If verified, performs `git reset --hard origin/main` on the worktree branch and exits 0. The routine session then exits cleanly without re-claiming; the next cadence fire claims fresh. If shape doesn't match (multi-commit-ahead, non-claim subject, slots differ), exits 2 — the session must escalate via HANDOFF.

Whitelisted as a narrow exception to the routine-mode destructive-action posture (per CLAUDE.md). The bounded reset is mechanically verified, not freeform.

### Skill + ops doc wiring

[`.claude/skills/routine-mode-lifecycle/SKILL.md`](../../.claude/skills/routine-mode-lifecycle/SKILL.md) gains steps 0a, 0b, the step-8 push-rejection branch, and the step-11 lock-release. [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) Layer 1 doc mirrors. CLAUDE.md adds the recovery-script + freshness-ff posture carve-out.

## Consequences

**Positive:**
- Eliminates the staleness vector that produced Issue #15. Future routine sessions cannot read stale `register_state.json` because boot mechanically fast-forwards before reading.
- Routine cadence can be tightened (e.g., quarter-hourly) without exposing a real concurrency race, because the lockfile catches it before either session commits.
- Future races leave no orphan branches/worktrees because the loser self-cleans via the bounded reset.
- Diverged HEAD is now a hard refusal at boot rather than silently proceeding against a corrupted state.

**Cost:**
- Three new tools (~280 lines total) plus three test files (~330 lines). Modest implementation cost; high-confidence tests against tmp-dir git fixtures and concurrent-acquire multiprocessing tests.
- Pre-existing orphan branches/worktrees from before this contract still need manual cleanup (the original `claude/mystifying-easley-3f3789` from Issue #15 is user-adjudicated).
- The lockfile mechanism is per-checkout — cross-machine concurrency (multiple developers' clones racing) is not addressed; that case still relies on first-push-wins.

**Out of scope:**
- Mechanizing the freshness gate for `/start-engine` interactive boot. Interactive sessions keep the informational-warning model — the AI is in the loop and the cost of acting on the warning is low. Could be a follow-up enhancement Issue if the same pattern appears interactively.
- Lock fairness / queueing. There is no retry loop; the loser exits cleanly and the next cadence fire claims fresh. Acceptable for the cadence frequency the project actually uses.
- Multi-commit-ahead recovery. If the loser has more than one commit ahead of origin/main, the shape doesn't match (substantive work was committed before the push); manual cleanup applies.

## Cross-references

- [Issue #15](https://github.com/StarshipSuperjam/paideia/issues/15) — the original report (corrected diagnosis at S-0055).
- [Issue #10](https://github.com/StarshipSuperjam/paideia/issues/10) — the S-0051 informational staleness check this ADR mechanizes.
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — routine-mode foundation; this ADR amends the "concurrent-session serialization" framing.
- [ADR 0045](0045-shared-state-integrity-discipline.md) — the same "shared state on disk doesn't match expected state-of-world" concern; this ADR adds another mechanical check in the same family.
- [`engine/operations/routine-mode-operations.md`](../operations/routine-mode-operations.md) — Layer 1 ops doc with the "Concurrency control" subsection.
- CLAUDE.md "Routine-mode posture (load-bearing)" — `routine_eager_claim_recovery.py` carve-out.
