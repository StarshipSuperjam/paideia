# build_lifecycle_push.py — first-exercise readiness note

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) cross-cutting-mechanism gate. ADR 0076 criterion-4 evaluation (consequences span ≥3 ops docs OR ≥5 tooling files): satisfied via 2 tooling files (`build_lifecycle_push.py`, `test_build_lifecycle_push.py`) + 1 settings file + 2 procedural surfaces (build-lifecycle ops doc + shutdown ops doc) + 2 Skill files + 1 ADR + this readiness note = 9 surfaces total. Readiness note required.

## Tier 1 — close in-session (the session that introduces the mechanism)

Both Tier 1 criteria close at S-0138 (the session shipping ADR 0076):

- **T1-A — well-formed deliverable push succeeds against `main`.** S-0138's own deliverable commit (the commit that ships ADR 0076 + `build_lifecycle_push.py` + the allowlist revert + ops-doc updates) is the first natural exercise of `deliverable` mode. Invocation: `python3 engine/tools/build_lifecycle_push.py deliverable`. Expected: exit code 0, deliverable lands on origin/main, parent-side FF reports success. Recorded in the session's `outcome_summary` and updated here at close.
- **T1-B — well-formed close push succeeds against `main`.** S-0138's own close commit invokes `python3 engine/tools/build_lifecycle_push.py close`. Expected: exit code 0, close lands on origin/main, parent-side FF reports success.

S-0138's eager-claim push is NOT a first exercise because it landed BEFORE the wrapper existed (the wrapper is what the deliverable ships); the eager-claim used the still-effective S-0137 broad allowlist that this very deliverable removes. Eager-claim mode's first natural exercise is the next interactive `/start-engine` build session (S-0139 or later).

**Tier 1 closeout evidence (updated at S-0138 close):**

- T1-A status: _to be recorded at deliverable push_
- T1-B status: _to be recorded at close push_
- If either fails: HANDOFF entry per wrapper exit-code contract; investigate before retry; do NOT amend the commit.

## Tier 2 — close in next natural occasions

- **Eager-claim mode first exercise.** The next interactive `/start-engine` session (S-0139+) invokes `build_lifecycle_push.py eager-claim`. Record outcome in that session's `outcome_summary` AND update this note's "Empirical record" subsection.
- **First refusal exercise.** Any session that authors a malformed lifecycle commit (wrong subject pattern, dirty working tree, etc.) and gets refused by the wrapper. Record the refusal reason and the recovery path the AI took.
- **First push-rejection exercise (exit code 3).** A peer push to main between the wrapper's verification and its push, OR a future harness update that closes the subprocess-bypass loophole. The wrapper's exit-3 path with the "investigate before retry" guidance should fire cleanly.

## Tier 3 — defer indefinitely (recorded for future audit)

- **Performance budget.** The wrapper adds ~0.3-0.5s to each lifecycle push (3 subprocess git calls per verification + 1 for push + 1 for parent FF). Negligible relative to the lifecycle's overall cadence (3 pushes per session ≈ ~1.5s total). Re-audit if the wrapper grows additional verification predicates.
- **Refactor to single `lifecycle_push.py`.** Sibling composition (per ADR 0076 decision 1) is the right shape for now. A future health-check audit may recommend collapsing the two wrappers if drift between them becomes observable. Trigger: 3+ instances of "fixed in one wrapper, missed in the other."
- **Validator soft-warn for raw-push attempts in build sessions.** Could mechanize "the AI invoked `git push origin main` in a build session despite the allowlist revert." Deferred — the allowlist revert plus the harness classifier together make raw push impossible from sanctioned paths.
- **Subprocess-bypass hypothesis robustness.** Both `routine_lifecycle_push.py` and `build_lifecycle_push.py` depend on the harness inspecting Bash command surface but not subprocess-spawned git from permitted python. If a future harness update closes this loophole, both wrappers break together. The exit-code-3 path documents this scenario; no proactive defense.

## Empirical record (Tier 1 will be appended at S-0138 close; Tier 2 by future sessions)

_Empty — populated as exercises occur._
