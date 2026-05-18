---
session_id: S-0205
session_type: build
closed_at: "2026-05-18T17:35:00Z"
material_change_class: tool
module: engine/tools
summary: Fix Issue #150 — pin HISTORY_FILE to canonical main-repo path so ADR 0063 regression check sees a consolidated time-series across all worktrees + main repo.
---

# S-0205 — Fix Issue #150 (HISTORY_FILE per-clone resolution) — 2026-05-18

Closes [Issue #150](https://github.com/StarshipSuperjam/paideia/issues/150) (S-0204 audit Finding B: `validator_runtime_phase_regression` structurally inoperative across the entire S-0184 → S-0203 audit window). Issue #115 deferred per user decision in plan-mode pushback — STATE.md trigger-gate honored.

## Changed

- **[`engine/tools/validate.py`](../../tools/validate.py)** — new `_resolve_canonical_history_path(cwd=None)` helper at lines 187-238 runs `git rev-parse --path-format=absolute --git-common-dir` (returns `<main-repo>/.git` from any worktree or the main repo itself), pins `HISTORY_FILE` to `<main-repo>/engine/tools/validate-history.jsonl`. Falls back to per-clone path on subprocess failure. `REPO_ROOT` unchanged (still active-clone path; correct for repo-internal path resolution).
- **[`engine/adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md`](../../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md)** — Consequences amendment "S-0205 (Issue #150) — HISTORY_FILE pinned to canonical main-repo location". Also adds Issue #150 cross-reference.
- **[`engine/operations/tools-validate-interpretation.md`](../../operations/tools-validate-interpretation.md)** — `validator_runtime_phase_regression` entry gains "HISTORY_FILE resolution" paragraph; Telemetry section's per-invocation-forensics line updates the (gitignored, per-clone) parenthetical.

## Added

- **[`engine/tools/test_validate_history_resolution.py`](../../tools/test_validate_history_resolution.py)** — 3 pytest cases against tmp main-repo + linked-worktree fixtures: worktree-side resolution / main-repo-side resolution / outside-git-repo fallback. All 3 pass.

## Verification

End-to-end this session. Pre-fix snapshot (S-0205 eager-claim at `5ee5c23` ran default-mode pre-commit from worktree): per-phase fields wrote to `<worktree>/engine/tools/validate-history.jsonl` (2 entries); main-repo file unchanged at 90 entries (latest `S-0190`, 2026-05-16, retired-substrate mempalace shape). Post-fix snapshot (`validate.py --health-probe-only` from same worktree): new entry landed in `<main-repo>/engine/tools/validate-history.jsonl` (90 → 91 entries); worktree file unchanged at 2 entries. Synthetic 3-entry breach test against `validate_runtime_phase_regression()` fires the soft-warn (median 800ms vs 750ms threshold) as designed.

**Live first-fire at session close.** The close `validate.py --final-check` reported `validator_runtime_phase_regression` for the first time ever: median `duration_structural_ms` 909.6ms across last 3 runs against 500ms target (750ms threshold). Pre-S-0205 the check fired 0 times across 90 history entries. The structural-phase regression itself is real signal newly visible; recommended for S-0206 investigation per the Next-session work item in STATE.md.

## Engine_memory

3 drawers + diary. Decision `359cab0b` (ADR 0063 amendment + commit SHAs). Lesson `0c8863ca` (per-clone-file-resolution gotcha — `Path(__file__).resolve()` in worktree-heavy project resolves to active clone, not canonical clone). Pushback `93d76b20` (self-pushback against the user's "fix #115 if possible now" hedge; trigger-gate problem surfaced; user accepted deferral via AskUserQuestion). Diary entry `b7e7f288`.
