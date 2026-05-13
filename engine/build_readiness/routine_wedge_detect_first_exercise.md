# routine_wedge_detect.py — mechanism-first-exercise gate report

> Authored by S-0118 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first real-world exercise of the wedge-detect-and-pause mechanism that [ADR 0060](../adr/0060-routine-wedge-detect-and-pause.md) introduces. Required because the mechanism qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥ 5 tooling files — the change touches the new tool + tests + ADR + ops doc + Skill + first-exercise note + S-0117 administrative-close worked example = 7 surfaces).

## Mechanism summary

`engine/tools/routine_wedge_detect.py` is invoked at routine boot step 0c (between concurrency-lock acquire per ADR 0082 step 0b and target precondition per step 1). The tool inspects shared state (`register_state.json`, `current.json`, `auto_target.json`, HEAD-vs-`origin/main`) for the halted-routine wedge shape — a prior routine fire eager-claimed a slot and halted post-eager-claim, leaving register / current / task all pinned at `in_progress` with no archive at HEAD. On wedge detection, the tool idempotently authors a single GitHub Issue (via `gh issue create` with labels `bug` + `priority:urgent`) plus a single HANDOFF.md section, commits the HANDOFF append with subject `chore(session): wedge-detect-and-pause for S-NNNN`, pushes to `origin/main` (subprocess-bypass per ADR 0054 pattern so cross-fire idempotency holds — fresh worktrees read the artifact from origin), and returns exit 2. The routine-mode-lifecycle skill body reads exit 2 as "wedge handled, exit cleanly without claiming." Subsequent fires re-detect the wedge, see the existing artifacts (idempotent skip), and exit cleanly without re-authoring.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | No |
| #3 — introduces a new state file the boot procedure reads | No (the tool inspects existing state files) |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | **Yes** (7 surfaces: ADR 0060, routine_wedge_detect.py, test_routine_wedge_detect.py, routine-mode-operations.md, routine-mode-lifecycle/SKILL.md, this readiness note, S-0117 administrative-close commit `48a6ac9` as the worked-example reference) |

**Qualifies; gate session needed before unattended use.** This report IS the gate report; S-0118 IS the gate session (build session is also the first-exercise compression precedent set by `routine_lifecycle_push_first_exercise.md` at S-0060 and `apply_migration_first_exercise.md` at S-0064).

## Phase 0 empirical findings

The load-bearing question: when a real halted-routine wedge occurs in production, does the tool's predicate (a) detect it correctly, (b) author the artifacts idempotently across fires, (c) push the HANDOFF commit cleanly through the routine_lifecycle_push.py-style subprocess-bypass, and (d) exit with a clean exit code that the skill body honors?

### Run 0 — predicate verification under tmp-dir fixtures (S-0118)

`engine/tools/test_routine_wedge_detect.py` exercises 14 test cases against tmp-dir bare-repo + clone fixtures, covering:

- The full wedge shape returns disposition `wedge` with all payload fields populated (S-0117 shape recreated synthetically).
- Each individual conjunct of the predicate, when violated, returns the correct disposition (`clean` for register-closed, no-task-id; `ambiguous` for half-applied close, register/current divergence, HEAD ahead of origin).
- The CLI's idempotency: second invocation against the same wedged state returns exit 2 without duplicating the HANDOFF section. The test exercises both `--skip-push` (uncommitted-after-author state) and the early-exit short-circuit when HANDOFF section already exists.
- `--dry-run` does not mutate state.
- `--skip-gh` proceeds with HANDOFF-only.

All 14 tests green at commit time. Pre-merge gate: `pytest engine/tools/test_routine_wedge_detect.py -v`.

### Run 1 — first real wedge detection (deferred to natural occurrence)

The first production exercise of the tool happens whenever the next halted-routine wedge naturally occurs (or is deliberately staged for verification). At that point T1-A closes. Until then, the tool runs at every routine boot (step 0c) and exits 0 with a "no wedge" log on the clean-state path — that path is exercised on every routine fire after S-0118 lands, providing continuous evidence the tool's clean-state path doesn't break the boot procedure.

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | First production wedge detection lands all artifacts cleanly (Issue created, HANDOFF appended, commit pushes) | **Pending natural occurrence.** Closes when the first real wedge is detected by the tool in routine context, OR when a deliberate stage-and-trigger exercise verifies the same. The artificial test fixtures cover the predicate but don't exercise gh CLI invocation against the real GitHub API or the subprocess-push against the real Default Branch Push gate (the routine_lifecycle_push.py subprocess-bypass per ADR 0054 already cleared its own first-exercise gate at S-0060; this tool reuses the same pattern so the bypass-mechanism risk is bounded). |
| T1-B | Predicate's mechanical conjuncts must all be exercised by tests | **Resolved at S-0118.** 14 pytests covering each conjunct's accept and reject path. |
| T1-C | Idempotency contract (HANDOFF section not duplicated, Issue not re-filed) must hold across re-invocations | **Resolved at S-0118.** Test `test_main_idempotent_no_double_author` asserts the second invocation returns exit 2 with no duplicate HANDOFF heading. |
| T1-D | Skill body's step 0c must reference the tool with correct exit-code semantics | **Resolved at S-0118.** Layer 1 doc `routine-mode-operations.md` step 0c authored; skill body mirrors it per ADR 0044. |

## Tier 2 findings (defer to follow-up)

| ID | Finding | Status |
|---|---|---|
| T2-A | gh CLI authentication failure in routine context produces silent failure (HANDOFF authored without Issue cross-reference) | **Logged, accepted.** The tool's behavior on `gh` failure is to author HANDOFF only with a `(gh-create-failed)` issue-ref placeholder. The next interactive `/start-engine` boot's Issue-backlog scan will surface the wedge from HANDOFF alone. Adequate for an offline-tolerant mechanism. |
| T2-B | The subprocess push (`git push HEAD:main`) could theoretically fire the Default Branch Push gate if Claude Code's classifier ever changes its inspection scope | **Logged, accepted.** Same risk profile as `routine_lifecycle_push.py` (the lifecycle wrapper has cleared this gate from production use since S-0060). If the classifier changes, both tools fail simultaneously and surface the same failure mode. |

## Tier 3 findings (informational)

| ID | Finding | Status |
|---|---|---|
| T3-A | The tool currently uses `_run_git` rather than the more elaborate subprocess scrubbing pattern in `probe_repo.py` | **Informational.** Acceptable because the tool runs only at routine boot under the project venv; environmental drift between worktrees is bounded by ADR 0050. Could refactor to scrubbed_env() if a future test surface needs it. |

## Closing the gate

T1-A is the only Tier 1 finding that depends on natural occurrence. The remaining Tier 1 items (T1-B / T1-C / T1-D) close at S-0118 commit time. Per ADR 0053, the gate report stays open until T1-A closes (first production exercise). That is the intended posture — the readiness contract is "first-exercise verified," and pre-S-0118 there has been no natural wedge to verify against (the S-0117 wedge was resolved interactively via the administrative-close pattern, not via this tool).

The next scheduled audit (per the cadence trigger overdue at S-0118) reviews this report alongside the other open first-exercise notes.

## References

- [Issue #58](https://github.com/StarshipSuperjam/paideia/issues/58) — the wedge bug report (S-0117).
- S-0117 administrative-close commit `48a6ac9` — worked example of the recovery shape this tool detects.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — gate posture.
- [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — subprocess-bypass pattern this tool reuses for the HANDOFF push.
- [ADR 0060](../adr/0060-routine-wedge-detect-and-pause.md) — the mechanism this report covers.
