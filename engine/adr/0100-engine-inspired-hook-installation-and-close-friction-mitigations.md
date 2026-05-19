# ADR 0100 — Engine-inspired hook installation and close-friction mitigations

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** S-0210

## Context

[ADR 0099](0099-session-close-friction-mitigations.md) landed Fixes A+C+D+E for [Issue #153](https://github.com/StarshipSuperjam/paideia/issues/153) at S-0209 with an open observation window (acceptance criterion 4: three consecutive clean closes). Mid-S-0209 surfaced [Issue #154](https://github.com/StarshipSuperjam/paideia/issues/154) — `check_settings_sync.py`'s bidirectional-assumption bug — *during the very session intended to eliminate close friction*. The diary entry for that close (drawer `c2dfb077`, lesson drawer `1e3071aa`, pushback drawer `fcd3e824`) names the recurring shape: the apparatus we built to prevent close-friction is itself a source of close-friction. The user's reframe — *"Wasn't this whole session to prevent things just like this?"* — names the identity of the problem class rather than yet another distinct symptom.

The genealogy of one-off fixes against this class is long. S-0033 (HANDOFF audit), S-0036 (HANDOFF disposition contract), S-0041 (explicit pushback/lesson capture), S-0048 (`check_settings_sync.py` authorship), S-0055 (archive structured-fields audit), S-0078 (diary-write enforcement), S-0118 (`git-mv` close-shape fix), S-0209 (ADR 0099 fix package). Each addresses a specific failure mode; the underlying structural property — a burst of mechanical commits at close time, sequential gates compounding, recovery paths classifier-blocked — keeps producing new symptoms. The one-off-fix loop has not converged.

A sibling project at `/Users/shanekidd/Documents/Claude_Files/Engine` runs the same kind of session apparatus (eager-claim ritual, validator suite, lifecycle-push wrapper) and is reported to have zero close-friction. The architectural delta surfaces four transferable patterns:

1. **Hook discovery via `core.hooksPath`-equivalent (vs symlink).** Engine installs `.git/hooks/pre-commit` as a direct script via `.engine/tools/setup/install_git_hooks.sh`; the installed hook resolves `REPO_ROOT="$(git rev-parse --show-toplevel)"` at runtime per-worktree. Paideia uses a relative symlink `<main>/.git/hooks/pre-commit → ../../engine/tools/hooks/pre-commit` whose target resolves through main's working tree — so worktree commits run main's bash-content version of the hook. The S-0209 lesson (drawer `1e3071aa`) is exactly this: a hook-content edit in a worktree (Fix C's `ruff format` auto-apply) didn't take effect on the worktree's own next commit because main's working tree hadn't FF'd yet. Paideia's pre-commit *already* does `REPO_ROOT="$(git rev-parse --show-toplevel)"; cd "$REPO_ROOT"` at line 32, so subsequent `python3 engine/tools/validate.py` invocations DO hit the worktree's own validate.py — only the BASH content of the hook itself is symlink-staleness-vulnerable.
2. **Auditable bypass via `SKIP_ENGINE_HOOKS=1`.** Engine's hook supports `SKIP_ENGINE_HOOKS=1 git commit -m "..."` as an alternative to `--no-verify`; every bypass logs to `.engine/reports/hook-bypass.log` with timestamp, branch, user, and commit subject. Paideia's S-0207 + S-0208 + S-0209 each used `--no-verify` (or in S-0208's case, classifier-blocked recovery operations) to land close commits; none of those bypasses left an audit trail.
3. **Partial-close recovery tooling.** Engine ships `recover_partial_close.py` with 4-state diagnosis (archive-active-no-commit / active-only / archive-only / neither) and three recovery flags (`--remove-active`, `--land-close`, `--rollback-archive`); each verifies the state shape mechanically before mutating. Paideia has no equivalent — when close goes wrong, recovery is bespoke and classifier-friction-bound.
4. **Bidirectional-aware sync checks.** Issue #154's surface — `check_settings_sync.py` assuming main is always canonical — is a Paideia-specific bug, not directly mirrored in Engine (which has no centralized settings-sync gate). The fix is independent of Engine's pattern but lands alongside as it's the same problem class (gate-mechanism produces close-friction).

### Load-bearing premises

*(Extraction step per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md): this ADR qualifies under criterion #1 — cross-cutting mechanism authoring per [ADR 0053](0053-mechanism-first-exercise-gate.md) trigger #4 (Consequences span ≥5 tooling files: see Trigger-criterion evaluation below).)*

1. **Git 2.50 resolves relative `core.hooksPath` worktree-root-relative.** Required for the hook-discovery migration to work without ambiguity from worktree subdirectories. *Falsifier:* Git resolves the path relative to CWD instead, causing the hook to be missed (or worse, a wrong file to be invoked) when commits are made from a subdirectory. *Mitigation:* in-session verification by setting `git -c core.hooksPath=engine/tools/hooks_test_path` and committing from both worktree root AND a subdirectory (`engine/session/`), with a test hook that prints its own path. *Test ran:* both invocations resolved to `engine/tools/hooks_test_path/pre-commit` (worktree-root-relative). **Premise verified empirically against Git 2.50 (Apple Git-155).**
2. **`SKIP_ENGINE_HOOKS=1` audited-bypass adoption is structurally safer than `--no-verify`.** *Falsifier:* the bypass becomes the path of least resistance and accumulates use beyond the rare-case intent, producing audit-log volume without any session ever reading it. *Mitigation:* `session-start.sh` reads `.engine_reports/hook-bypass.log` at every boot and surfaces new-since-last-session entries as a LOUD attention surface — every bypass is visible to a subsequent session even if the using session never named it; the same persistent-warn-style 3-of-5 escalation per [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) applies if frequency rises. *Test status:* unverifiable until the mechanism is exercised across enough sessions to measure frequency. **Premise accepted with the named risk + named surveillance mechanism.**
3. **Partial-close recovery's 4-state model covers the close-failure shapes actually encountered.** *Falsifier:* a fifth state shape exists that the tool refuses on AND that is reachable in practice. *Mitigation:* the tool refuses unrecognized shapes rather than guessing — a fifth shape surfaces as an explicit "shape not recognized: please file an Issue with shape signature" message, surfacing the gap rather than silently mishandling. *Test status:* in-session pytest fixtures cover all four named states + at least two "shape not recognized" cases; live-fire first exercise will be the next post-S-0210 close that goes wrong. **Premise accepted with explicit failure mode.**
4. **`check_settings_sync.py` direction detection via mtime + content hash discriminates worktree-newer from main-newer reliably.** *Falsifier:* mtime can be manipulated (e.g., `touch -d`) producing a false signal; multiple worktrees can write to their copies near-simultaneously producing genuine concurrent edits. *Mitigation:* the tool prefers content-hash equality as the primary signal (if hashes match, no divergence regardless of mtime); when hashes differ, mtime is the discriminator but a genuine bidirectional-edit case (both newer than common ancestor) halts and surfaces both diffs for user adjudication rather than guessing. *Test status:* in-session pytest fixtures cover (a) worktree-newer (mtime-distinguishable), (b) main-newer (the original case the tool handled), (c) hash-equal (no-op), (d) bidirectional conflict (halt-and-confirm). **Premise verified by test fixtures.**
5. **ADR 0099's observation window confound is an acceptable cost.** ADR 0099 acceptance criterion 4 requires three consecutive clean closes to close Issue #153. This ADR alters the apparatus mid-window. If S-0210 closes cleanly we cannot attribute the cleanliness to ADR 0099's fix package alone vs the additional core.hooksPath + SKIP_ENGINE_HOOKS + check_settings_sync + recover_partial_close additions. *Falsifier:* the confound prevents convergence (we never learn which intervention worked, and a future failure of the combined apparatus can't be attributed to a specific item). *Mitigation:* this ADR explicitly redefines the acceptance criterion to "3 clean closes against the combined apparatus" — Issue #153 closes when the combined set works, not when ADR 0099 alone works. If close-friction recurs, the next session triages which surface fired (the failure mode itself names the responsible item: a hook-content-staleness issue → core.hooksPath broke; a settings-sync mis-fire → Issue #154 fix is incomplete; etc.). The attribution clarity comes from FAILURE pattern matching, not from layered-deployment isolation. **Premise accepted; risk acknowledged.**

## Decision

Land four mechanically distinct Engine-inspired mitigations as one package:

**Item 1 — Migrate hook discovery from filesystem symlink to `core.hooksPath`.**

- Set `git config --local core.hooksPath engine/tools/hooks` on the main repo's `.git/config`. Worktrees share main's `.git/config`, so the setting propagates automatically.
- Remove `<main>/.git/hooks/pre-commit` (the relative symlink to `../../engine/tools/hooks/pre-commit`).
- After the migration, every commit (from main or any worktree) resolves the pre-commit script from `<worktree-root>/engine/tools/hooks/pre-commit` — the worktree's OWN working tree at HEAD. Hook-content edits authored in a worktree take effect on the SAME worktree's next commit, no longer dependent on main repo's working tree being FF'd first. Cures the S-0209 symlink lesson at the root.
- **Per-clone setup:** new clones must run `git config --local core.hooksPath engine/tools/hooks` once. Documented at [`engine/operations/clone-setup.md`](../operations/clone-setup.md) (new) + cross-referenced from the project README.

**Item 2 — Fix `check_settings_sync.py` bidirectional-assumption bug (closes [Issue #154](https://github.com/StarshipSuperjam/paideia/issues/154)).**

- Modify [`engine/tools/check_settings_sync.py`](../tools/check_settings_sync.py) to compute SHA-256 content hashes for both copies. If hashes match, exit 0 (no divergence; no guidance). If hashes differ, compare mtimes:
  - If worktree's copy is newer → emit guidance to copy `worktree → main`.
  - If main's copy is newer → emit guidance to copy `main → worktree` (existing behavior).
  - If mtimes are within a 1-second tolerance (genuinely-concurrent edit) → halt-and-confirm: emit both diffs to stderr, exit non-zero, name the file paths, name the conflict-resolution choice the user must make.
- Hard-fail exit code 1 on guidance produced (existing behavior preserved).

**Item 3 — Add `SKIP_ENGINE_HOOKS=1` audited bypass to pre-commit (Engine pattern).**

- Insert bypass block at head of [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit) (after `REPO_ROOT` resolution, before `scrub_env.sh` sourcing). The block: if `$SKIP_ENGINE_HOOKS = "1"`, log to `.engine_reports/hook-bypass.log` (timestamp + branch + user email + commit subject from `.git/COMMIT_EDITMSG`), emit a stderr notice, exit 0.
- Add `.engine_reports/` to `.gitignore`.
- The bypass is auditable (every use leaves a trace), project-aware (uses git config for user identity), and explicit (intent named in the env var, vs `--no-verify` which is universally available). **Routine-mode sessions still refuse this path** per [routine-mode-operations.md](../operations/routine-mode-operations.md) — every routine bypass is a HANDOFF entry + halt, not a silent escape hatch.
- Document at [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) close-failure-handling: when fix-in-context isn't possible mid-close (e.g., the close-shape verifier refuses a path the AI cannot route through a separate commit because step 14 has already started), `SKIP_ENGINE_HOOKS=1 git commit` is the preferred path over `--no-verify`.

**Item 4 — Port `recover_partial_close.py` for partial-close recovery.**

- New tool at [`engine/tools/recover_partial_close.py`](../tools/recover_partial_close.py). Four-state diagnosis (per Paideia archive layout — paths adapted from Engine's `.engine/sessions/` to `engine/session/`):
  - **State A** — `engine/session/current.json` exists AND `engine/session/archive/S-NNNN.json` exists for the same N. (Archive landed but `current.json` was not deleted in the close commit; the commit is in a malformed state.)
  - **State B** — `current.json` exists, no matching archive. (Normal in-progress; no recovery needed; tool reports and exits 0.)
  - **State C** — No `current.json`, archive exists for last claimed N, `register_state.json` still says `current_status: in_progress`. (Archive + current.json removal landed but register flip didn't commit, or commit landed but push didn't.)
  - **State D** — No `current.json`, no archive for last claimed N, register says `closed`. (Clean closed state; no recovery needed; tool reports and exits 0.)
- Three recovery flags:
  - `--remove-active` — delete the duplicate `current.json` when in State A. Verifies State A shape (both files exist, contents match the same session ID); refuses if shape differs.
  - `--land-close` — author + commit the pending register flip when in State C. Verifies State C shape; refuses otherwise.
  - `--rollback-archive` — move archive back to `current.json` + restore register `current_status: in_progress` when an erroneous close needs undoing. Verifies the rollback target shape; refuses otherwise.
- Each flag emits a structured pre-flight report (paths touched, register state before/after, refuse reason if applicable) before mutating. **No raw `git reset`** — recovery uses normal staged-commit operations through the existing build-mode lifecycle apparatus.
- Per ADR 0048 disposition discipline, `--land-close` writes a HANDOFF disposition entry referencing the recovered close.

**Item 5 — Update operations docs + Skill parity.**

- [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md): add "Close-commit-failed recovery" subsection covering `recover_partial_close.py`'s four states + the `SKIP_ENGINE_HOOKS=1` bypass guidance.
- [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md): parity update per [ADR 0089](0089-skill-layer1-parity-validator-check.md). The recovery subsection lives outside the numbered step procedure (it's a recovery path, not a step), so no step-set change. Parity-check stays clean.
- [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh): LOUD reminder block when `.engine_reports/hook-bypass.log` has entries newer than the last session's `started_at`. Mirrors the existing pattern for ADR-index inconsistency surfacing.

## Trigger-criterion evaluation (per ADR 0053)

`engine-inspired-hook-installation-and-close-friction-mitigations` is evaluated against [ADR 0053](0053-mechanism-first-exercise-gate.md)'s four disjunctive trigger criteria:

- **#1 (new session mode):** does not fire.
- **#2 (new validator soft-warn that depends on session-side discipline):** does not fire. No new `validate.py` category; the existing surfaces already cover the apparatus.
- **#3 (new state file the boot procedure reads):** marginal. `.engine_reports/hook-bypass.log` is read by `session-start.sh` as a LOUD reminder surface, but it's observer-only (no load-bearing state encoded in it; bypass-or-not is decided at SKIP_ENGINE_HOOKS-set time, not at boot-read time). Does not fire under a strict reading.
- **#4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files):** **fires** — Consequences below touch [`engine/tools/hooks/pre-commit`](../tools/hooks/pre-commit), [`engine/tools/check_settings_sync.py`](../tools/check_settings_sync.py), new [`engine/tools/recover_partial_close.py`](../tools/recover_partial_close.py), [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh), `.gitignore`, `<main>/.git/config` (the `core.hooksPath` setting), plus [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) and [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) (8 surfaces).

Criterion #4 fires, so the mechanism qualifies as cross-cutting. **No first-exercise readiness note is authored**, for the same reason as [ADR 0089](0089-skill-layer1-parity-validator-check.md) and [ADR 0099](0099-session-close-friction-mitigations.md): the gate exists to catch mechanism bugs before unattended exercise where they cannot be observed; each of these four mitigations is dogfooded in this authoring session itself. Item 1 is exercised by every commit AFTER the migration lands (the eager-claim commit ran the OLD symlink; this and all subsequent commits run the new `core.hooksPath`). Item 2 is exercised by pytest fixtures + a real divergence simulation in-session. Item 3 is exercised by a direct hook invocation that writes the audit log + a real `SKIP_ENGINE_HOOKS=1` use to verify the trace. Item 4 is exercised by pytest fixtures for each named state + a dry-run against the current closed-session state.

## Alternatives Considered

### Suite dispatch via `validate.py --suite pre-commit/pre-close` (deferred)

- **What:** replace Paideia's dynamic phase detection (mode determined by parsing `current.json` + staged `register_state.json` in bash) with Engine's declarative model — `--suite pre-commit | pre-close | ci | audit-prep` flags + YAML suite definitions + an explicit dispatcher.
- **Pros:** matches Engine's pattern; eliminates state-sniffing in bash; suite membership becomes an auditable contract (a check is or isn't in the suite, declared in YAML).
- **Cons:** large refactor (new phase model in `validate.py`, new YAML schema, dispatcher logic, migration of every existing check to suite-tagged registration); confounds the [ADR 0099](0099-session-close-friction-mitigations.md) observation window further than the current ADR already does.
- **Deferred because:** the per-user adjudication at plan-mode review chose "targeted Engine ports, not full architectural alignment." Suite dispatch is the natural escalation if the combined apparatus fails the redefined observation window — equivalent to [ADR 0099](0099-session-close-friction-mitigations.md)'s Fix B at architectural depth.

### Thin pre-commit hook (225 → 20 LOC bash, Engine pattern) (deferred)

- **What:** move all inline pre-commit hook logic (mode detection, `ruff format` auto-apply per ADR 0099 Fix C, `check_routine_scope.py` invocation, code-gates + sql-gates per [ADR 0050](0050-project-venv-and-hook-path-wiring.md)) into `validate.py`'s phase-aware entry points; reduce the bash hook to a wrapper that resolves `REPO_ROOT` and invokes `python3 engine/tools/validate.py --hook pre-commit`.
- **Pros:** reduces bash surface from ~225 lines to ~20; eliminates entire classes of bash-quoting / shell-globbing / regex-corner-case failures; future hook updates become Python (with type-checking, pytest coverage); aligns with Engine's hook architecture.
- **Cons:** same scope as suite dispatch above; bigger refactor than the user's targeted-ports scope; needs careful coverage of the existing soft-warn surfaces.
- **Deferred because:** same as suite dispatch — escalation path if the targeted ports don't generalize.

### Engine's `install_git_hooks.sh` pattern (vs `core.hooksPath`) (rejected for this session)

- **What:** instead of `git config core.hooksPath engine/tools/hooks`, port Engine's setup script that writes a thin wrapper into `.git/hooks/pre-commit` directly. The wrapper resolves `REPO_ROOT` at runtime and invokes `validate.py`.
- **Pros:** Engine's empirically-tested pattern; explicit setup step is more discoverable (the user runs `bash install_git_hooks.sh` once, and the hook is in place).
- **Cons:** the hook script lives in `.git/hooks/` which is NOT version-controlled — hook updates require re-running the install script after every pull that touches hook source. `core.hooksPath` resolves to the tracked tree directly, so `git pull` auto-propagates hook updates without any install step. Net result: `core.hooksPath` is structurally simpler for the same problem.
- **Rejected because:** `core.hooksPath` gives the same per-worktree resolution benefit with strictly less machinery. Engine's install pattern remains a fallback if `core.hooksPath` proves brittle in unforeseen edge cases; revisitable.

### Status-quo + Issue #154 patch only (rejected)

- **What:** patch `check_settings_sync.py`'s bidirectional bug; leave hook installation, bypass mechanism, recovery tooling unchanged.
- **Pros:** smallest possible intervention; doesn't confound [ADR 0099](0099-session-close-friction-mitigations.md)'s observation window.
- **Cons:** does not address the structural class. Issue #154 is symptomatic of the same pattern that produced Issues #153, the S-0207 wedge, the S-0208 close-shape refusal sequence. Patching only the latest surface keeps the one-off-fix loop unconverged.
- **Rejected because:** the user explicitly chose targeted Engine ports (not status-quo patches) at plan-mode review. The architectural diagnosis is what blocked the one-off-fix loop from converging.

## Consequences

### Structural

- **`<main>/.git/config` carries `core.hooksPath = engine/tools/hooks`.** This is per-clone state (not tracked). Every new clone (developer onboarding, fresh worktree setup if `.git` is re-initialized for some reason, CI checkouts) must set this. Documented at [`engine/operations/clone-setup.md`](../operations/clone-setup.md) (new) + cross-referenced from the project README. If the setting is missing, Git falls back to `.git/hooks/` which is now empty for pre-commit (the symlink was removed) — commits would proceed UNGATED. *Surface to monitor:* a future session that finds itself in an ungated state should suspect missing `core.hooksPath` first, before suspecting a hook bug.
- **`<main>/.git/hooks/pre-commit` symlink removed.** Any tool or script that inspects `.git/hooks/` expecting the symlink will see absence. None currently do — searched the tree for `\.git/hooks/pre-commit` references at session boot; only the recovery-procedure subsection in [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) "Pre-commit hook symlink" recovery path references it. That subsection updates as part of this ADR.
- **`engine/tools/hooks/pre-commit` carries a `SKIP_ENGINE_HOOKS=1` bypass block at head.** Audited via `.engine_reports/hook-bypass.log` (per-clone, gitignored). `--no-verify` continues to work (git-native) but is no longer the preferred path; `SKIP_ENGINE_HOOKS=1` is auditable.
- **`engine/tools/check_settings_sync.py` returns direction-aware guidance** + halts-and-confirms on bidirectional concurrent edits. Closes [Issue #154](https://github.com/StarshipSuperjam/paideia/issues/154).
- **New tool `engine/tools/recover_partial_close.py`** provides 4-state diagnosis + 3 recovery flags. Test coverage via pytest fixtures.
- **`engine/tools/hooks/session-start.sh`** emits a LOUD reminder when `.engine_reports/hook-bypass.log` has new entries since last session.
- **`engine/operations/session-shutdown-sequence.md`** gains a "Close-commit-failed recovery" subsection.

### Observation-window confound

[ADR 0099](0099-session-close-friction-mitigations.md) acceptance criterion 4 required three consecutive clean closes (no `--no-verify`, no classifier-blocked recovery) to close [Issue #153](https://github.com/StarshipSuperjam/paideia/issues/153). This ADR's apparatus confounds that signal — if S-0210 closes cleanly, we cannot isolate whether ADR 0099's Fix A+C+D+E alone would have produced the clean close, or whether one of this ADR's four additional mitigations is load-bearing.

**Acceptance criterion (revised):** three consecutive clean closes against the combined ADR 0099 + ADR 0100 apparatus close Issue #153. S-0210 = sample 1.

If close-friction recurs during the window, the failure pattern names the responsible item:
- Bash-content-staleness symptom (a hook edit not taking effect for the authoring worktree's next commit) → Item 1's `core.hooksPath` migration is broken or was reverted.
- `--no-verify` invoked instead of `SKIP_ENGINE_HOOKS=1` → AI discipline gap, not Item 3's mechanism (which is available).
- Settings-sync mis-fire (wrong direction guidance, or false-positive on identical content) → Item 2's direction-fix is incomplete.
- Close-failure recovery still requires user adjudication → Item 4's `recover_partial_close.py` is missing a state shape that this case exhibits.

Per-failure attribution comes from pattern-matching the symptom against the items, not from layered deployment.

### Deferred (named, tracked)

- **Suite dispatch** (Alternatives Considered above) and **thin pre-commit hook** (same) remain available as escalation paths if the targeted ports don't generalize. No Issue is filed pre-emptively; if the observation window fails and the failure pattern implicates fat-bash or dynamic-phase-detection, file then.

### Cross-references

- Supersedes nothing.
- Cited by: [`engine/operations/session-shutdown-sequence.md`](../operations/session-shutdown-sequence.md) (new close-failure-recovery subsection), [`.claude/skills/session-shutdown-sequence/SKILL.md`](../../.claude/skills/session-shutdown-sequence/SKILL.md) (parity mirror), [`engine/tools/hooks/session-start.sh`](../tools/hooks/session-start.sh) (bypass-log surveillance block), [`engine/operations/session-build-lifecycle.md`](../operations/session-build-lifecycle.md) (pre-commit symlink recovery subsection updates to reflect `core.hooksPath`).
- Cites: [ADR 0042](0042-soft-warn-lifecycle-archive-canon.md) (persistent-warn 3-of-5 escalation; bypass-log surveillance pattern), [ADR 0043](0043-hook-architecture.md) (hook posture: soft-warn reminders, non-blocking), [ADR 0048](0048-handoff-narrowing-and-github-issues-for-cross-session-deferrals.md) (HANDOFF disposition tokens; `--land-close` recovery flag writes one), [ADR 0050](0050-project-venv-and-hook-path-wiring.md) (venv PATH wiring in pre-commit; bypass block runs BEFORE the venv source — bypass needs no Python), [ADR 0053](0053-mechanism-first-exercise-gate.md) (trigger-criterion evaluation; no readiness note rationale), [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) and [ADR 0076](0076-build-mode-lifecycle-push-wrapping.md) (existing close-shape verification patterns reused by `recover_partial_close.py`), [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) (extraction-step section above), [ADR 0089](0089-skill-layer1-parity-validator-check.md) (Skill parity discipline), [ADR 0091](0091-engine-memory-substrate-sqlite-fts5.md) (engine_memory decisions-room drawer for this ADR), [ADR 0099](0099-session-close-friction-mitigations.md) (observation-window predecessor).
