# `parent_ff()` identical-content auto-recovery — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. The S-0150 amendment to [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) introduces a bounded auto-recovery extension to the canonical `parent_ff()` in [`engine/tools/routine_lifecycle_push.py`](../tools/routine_lifecycle_push.py); the change propagates to [`engine/tools/build_lifecycle_push.py`](../tools/build_lifecycle_push.py) via the existing import (line 120 of the build wrapper).
>
> Criterion-4 evaluation (consequences span ≥3 ops docs OR ≥5 tooling files): satisfied via 6 tooling files (`routine_lifecycle_push.py`, `test_routine_lifecycle_push.py`, `update_settings.py`, `test_update_settings.py`, `build_lifecycle_push.py` import surface, `check_settings_sync.py` companion) + 2 ADR amendments (0054 + 0076 cross-reference) + 1 ops doc (`session-build-lifecycle.md` Recovery subsection) + this readiness note = 10 surfaces total. Readiness note required.

## What this mechanism does

On a parent-side `git merge --ff-only origin/<target>` refusal matching the *"Your local changes to the following files would be overwritten by merge"* signature, `parent_ff()` parses the affected file list, compares each working-tree copy to its `origin/<target>` version via `git diff --quiet`, and:

- **All identical:** runs `git checkout -- <files>` + retries the FF. Provably idempotent — discarded content equals incoming content. Reason string names *"auto-recovered from identical-content overwrite refusal on N file(s)"*.
- **Any diverged:** bails with *"working-tree diverges from origin/<target> on <files>; manual recovery required"* WITHOUT mutating state. The wrapper's destructive-action refusal posture remains in force.
- **Non-overwrite refusal class:** falls through to the pre-existing *"refused: <stderr first line>"* path unchanged (regression guard — non-FF, parent on wrong branch, etc., behave as before).

## Tier 1 — close in-session (S-0150)

- **T1-A — identical-content happy path: auto-recovery succeeds end-to-end.** REQUIRES all files in the parent's working tree to be byte-identical to their `origin/<target>` versions. **Cannot close at S-0150** because the parent repo carries a pre-existing residual uncommitted modification to `pyproject.toml` (a 4-line *"Floors bumped at S-0147"* comment block present in parent's working tree but absent from `origin/main`) that diverges from `origin/main`. Until that residual is resolved, every parent-FF refusal in this session hits the diverged-content bail path, not the auto-recovery success path. **Closes in next build session whose parent repo is clean** (or by a deliberate edit of `.claude/settings.json` + `update_settings.py` in a session where `pyproject.toml` is no longer the residual blocker).
- **T1-B — diverged-content bail: returns "working-tree diverges..." without state mutation.** **CLOSES IN-SESSION at S-0150** via the parent's pre-existing `pyproject.toml` residual. Every parent-FF invocation after commit `4fffd31` (the parent_ff extension landing) exercises this path naturally: the wrapper's stderr reports *"working-tree diverges from origin/main on ['pyproject.toml']; manual recovery required"* and parent HEAD is NOT advanced. The wrapper's overall exit code remains 0 (the push itself succeeded; parent-FF failure is non-fatal per ADR 0054 decision 2). Empirical evidence captured at session close in the Empirical record subsection below.

## Tier 2 — close in next natural occasions

- **First multi-file identical-content auto-recovery.** A future session that triggers an overwrite refusal across 2+ files (e.g., simultaneous `.claude/settings.json` and `engine/operations/*.md` edits with the cp+stage flow applied to each). The reason string should report *"on N file(s)"* with N ≥ 2.
- **First second-failure-after-checkout path.** A future session where the auto-recovery's first checkout succeeds but the retry FF still fails (e.g., due to a concurrent merge conflict from a different file not in the original refusal list). The wrapper should report *"refused after auto-recovery attempt: <new stderr>"* with no state mutation beyond the initial checkout. Diagnostic: investigate the new failure cause; the auto-recovery did its job by handling the original overwrite-refusal, but a separate issue intervened.
- **First mixed-divergence bail (some identical, some diverged).** A future session where the overwrite refusal lists multiple files and at least one is identical while at least one diverges. The bail must name only the diverged files in the reason string and must NOT checkout any of the identical ones (atomic — no partial recovery). Empirical signature: reason includes the diverged-files list; non-diverged files are NOT mentioned; parent working tree is unchanged (verify via `git -C <parent> diff` post-bail).
- **First exercise from a routine-mode push.** The mechanism lives in `routine_lifecycle_push.py:parent_ff` — used by both build AND routine modes. Routine-mode sessions don't typically edit `.claude/settings.json`, but a routine session whose deliverable touches a parent-mirrored file (e.g., a future ADR 0080 boot-time-version-surface migration that updates `pyproject.toml`) would exercise the auto-recovery from the unattended side. Record the exit-code path observed; verify `mempalace_activity` captures the auto-recovery reason string.

## Tier 3 — defer indefinitely (recorded for future audit)

- **Performance budget.** The auto-recovery path adds at most one `git diff --quiet` per affected file + one `git checkout` + one retry `git merge --ff-only`. Worst case (single file): ~50ms total. Multi-file: linear in file count. Negligible relative to the lifecycle's overall cadence. Re-audit if the wrapper grows additional pre-flight predicates or if overwrite refusals routinely involve 10+ files.
- **Extending the auto-recovery to other refusal classes.** Considered and rejected at S-0150. The identical-content overwrite case is provably idempotent; other refusal classes (non-FF, divergent histories, merge conflicts) require human judgment about what to discard. Mechanizing those would invite silent data loss. Leave as manual recovery; the wrapper's existing destructive-action refusal posture is the right shape.
- **Per-mode disablement.** Could expose a `--no-auto-recovery` flag for sessions that want strict pre-S-0150 behavior. No use case identified; the auto-recovery is always safe when its preconditions hold. Defer unless a regression surfaces.
- **Validator soft-warn on auto-recovery firing.** Could mechanize "auto-recovery fired N times in the last K sessions" as a drift signal. Premature; the mechanism is too new to know what frequency is normal. Re-audit when the soft-warn surface has 30+ sessions of empirical baseline.

## Empirical record

### S-0150 (the session that authored the auto-recovery) — 2026-05-13

**T1-B closeout — diverged-content bail (parent pyproject.toml residual):**

The session's eager-claim push at 2026-05-13T20:20Z (commit `6f67b9b`) triggered the pre-existing parent-FF refusal behavior (the auto-recovery code landed AFTER eager-claim, at commit `4fffd31`). For all subsequent in-session pushes (the auto-recovery code's own deliverable commit, the `update_settings.py` deliverable, the docs deliverable, and the close commit), the new auto-recovery code IS deployed. Each push exercises the parent-FF surface against parent's residual `pyproject.toml` divergence.

Expected wrapper stderr per push: *"parent FF best-effort failed: working-tree diverges from origin/main on ['pyproject.toml']; manual recovery required"*. Wrapper exit code remains 0 (push succeeded; parent-FF failure is non-fatal). Parent HEAD does NOT advance.

*[Closeout evidence: see the close-push wrapper output captured in S-0150's `outcome_summary` field at session close.]*

**T1-A status: NOT closed in-session.** Reason: the parent's `pyproject.toml` residual divergence prevents the all-identical precondition from holding for any push during S-0150. The user adjudicates the pyproject.toml residual outside this session (the residual is a pre-S-0150 working-tree modification — investigation flagged at session close). Next session whose parent repo is clean (and which edits `.claude/settings.json` + invokes `update_settings.py`) closes T1-A naturally.

### Pattern note for future sessions

The S-0150 first-natural-exercise window illustrates a real-world property of the auto-recovery: the auto-recovery only fires when its preconditions hold. A session with multiple unrelated residuals in the parent repo (e.g., one identical, one diverged) sees the diverged-content bail path even when other files would have been auto-recoverable in isolation. The atomic all-or-nothing behavior is by design — partial recovery would invite silent data loss on the diverged files. Sessions that want to maximize auto-recovery success should clean parent residuals before invoking the wrapper.
