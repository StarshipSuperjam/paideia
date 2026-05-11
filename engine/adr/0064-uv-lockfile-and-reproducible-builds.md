# ADR 0064 — `uv` lockfile + reproducible dependency builds

- **Status:** Accepted
- **Date:** 2026-05-11
- **Deciders:** S-0127

## Context

Pre-S-0127 dependency posture: `engine/tools/requirements.txt` carried 10 floor-pinned (`>=`) deps; no lockfile, no transitive-version pinning, no SBOM. `uv` was already the package manager per [ADR 0050](0050-project-venv-and-hook-path-wiring.md), used only for `uv venv` (interpreter management); installs went through `uv pip install -r engine/tools/requirements.txt`, which resolves transitives at install time. Two clones running the same install on different days (or with different `uv` releases) get different transitive graphs.

The pre-SWE-hardening audit at session-pre-S-0124 (plan file `~/.claude/plans/not-a-working-session-sequential-twilight.md`) classified `uv lock` adoption as Tier 1 keystone — five downstream Issues (#67 Dependabot, #68 CI mirror of `validate.py`, #69 PR template + branch protection, #70 `bandit` SAST, #71 `pytest-cov` coverage) are gated on it. CI mirroring requires a deterministic install; SAST + coverage benefit from byte-identical dep trees across local and CI; Dependabot needs a lockfile to bump.

## Decision

Five coupled changes mechanize the adoption.

### 1. Lockfile at repo root sourced from `pyproject.toml`

A new `pyproject.toml` at the repo root carries the dependency declarations under `[project.dependencies]`, mirroring the prior `engine/tools/requirements.txt` set with the same floor pins and inline comment justifications. `uv lock` (run from the repo root) generates `uv.lock` at the repo root from `pyproject.toml`'s declared deps. Both `pyproject.toml` and `uv.lock` are committed.

`pyproject.toml` declares the project as non-installable (`[tool.uv] package = false`) — Paideia ships scripts under `engine/tools/` rather than a packaged distribution at this stage; the lockfile workflow doesn't need the package-build step. If [Issue #82](https://github.com/StarshipSuperjam/paideia/issues/82) (release tagging) eventually packages tools, the flag flips at that time.

### 2. `uv sync` as the canonical install path

`uv sync` replaces `uv pip install -r engine/tools/requirements.txt` everywhere — setup scripts, hook help text, ops docs, code-discipline.md install instructions. `uv sync` reads `uv.lock` and brings the venv into byte-exact alignment.

The pre-S-0127 floor-pinned-only flow was internally inconsistent — `engine/tools/requirements.txt` declared floors; nobody pinned transitives. The new flow is consistent: `pyproject.toml` declares floors, `uv.lock` pins exact versions, `uv sync` installs from the lock. The two surfaces serve different consumers (humans read `pyproject.toml`; machines read `uv.lock`).

### 3. Staleness check as `validate.py` soft-warn

A new `validate_uv_lock_freshness()` function in `engine/tools/validate.py` runs `uv lock --check` as a subprocess (cwd = repo root). Non-zero exit produces the `uv_lock_out_of_date` soft-warn. The check is in the `health_probe` phase per [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) (subprocess invocation; ~150ms variable). Three no-op cases preserve clean exits for clones without the contract: missing `pyproject.toml`, missing `uv.lock`, missing `uv` binary.

The soft-warn fires at every commit when `pyproject.toml` is staged without a matching `uv.lock` regeneration — it's a structural reminder, not a hard-fail, because legitimate cases exist (`pyproject.toml` edits to comments, name, description don't always require a lock refresh; `uv lock --check` is the deterministic ground-truth, not a heuristic).

### 4. Refresh discipline: intentional-only

The lockfile is regenerated only when dependencies change — no drive-by refreshes mid-session. The procedure is documented in `engine/operations/dependency-discipline.md`:

1. Edit `pyproject.toml` `[project.dependencies]`.
2. Run `uv lock` (regenerates `uv.lock`).
3. Run `uv sync` (brings local venv into alignment).
4. Stage all three (`pyproject.toml`, `uv.lock`, any callsite changes) in the same commit.

Rationale: the lockfile is a tracked file. Spurious refreshes (e.g., from a different `uv` version that produces a slightly different resolution) produce noise commits and complicate `git blame` for dep history.

### 5. Routine-mode interaction: lockfile is read-only

Routine sessions per [ADR 0051](0051-routine-mode-and-engine-loop.md) operate within a `scope_lock` that names the active task's `allowed_paths`. `pyproject.toml` and `uv.lock` are never in any task's `allowed_paths` (dep changes are inherently human-adjudicated decisions; routine sessions execute existing deps, they don't bump). The standard scope_lock check at commit time hard-fails any routine commit touching either file. Master-plan revisions to add a dep change to a task go through HANDOFF.md per the standard ADR 0051 protocol.

## Consequences

- **Positive — reproducibility.** Any two clones running `uv sync` against the same lockfile get the same packages. CI runs match local runs. Cross-machine debugging is no longer "did you have a different transitive?".
- **Positive — Dependabot readiness.** [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67) (Dependabot for pip + GitHub Actions) becomes feasible. Dependabot's PRs bump `pyproject.toml` floors and regenerate `uv.lock`; the standard refresh discipline captures the work.
- **Positive — CI gate compatibility.** [Issue #68](https://github.com/StarshipSuperjam/paideia/issues/68) (mirror `validate.py` to CI) can install with `uv sync` rather than `uv pip install`. Cache layer keys off `uv.lock` hash for fast cache restores.
- **Positive — transitive-dep visibility.** `uv.lock` lists the entire 99-package resolved graph (vs the 10 explicit declarations). Security review can audit the actual install surface, not just the floors.
- **Cost — lockfile churn.** `uv.lock` is ~440KB. Dep changes produce ~50–500-line diffs (transitive cascades). Tracked but understandable; `git log -- uv.lock` shows the dep-change history.
- **Cost — pre-commit gate latency.** The new `uv_lock_out_of_date` soft-warn adds ~150ms (subprocess to `uv lock --check`) to every commit's validator run. Lands in the `health_probe` phase per ADR 0063; total budget ~5s with current usage ~3.5s, so absorbs cleanly.
- **Cost — dual maintenance during deprecation window.** `engine/tools/requirements.txt` retained as a redirect pointer so cold-context users (and any unaware automation) land on a discoverable surface. The redirect is removed at the next health-check audit (cadence ~20 sessions per current `register_state.json`) once cross-references in the wild have caught up.
- **Out-of-scope.** SBOM generation is [Issue #83](https://github.com/StarshipSuperjam/paideia/issues/83), trigger-gated on a deployable artifact. The lockfile is the input to a future SBOM step but doesn't itself produce one.
- **Out-of-scope.** Splitting deps into prod/dev groups via PEP 735 dependency-groups is a deferred refinement — `reportlab` is currently test-only but kept in the main set; if the surface grows, split.
- **Out-of-scope.** Pinning `uv` itself to a version. The user prereq stays `brew install uv`. If `uv lock`'s output starts varying meaningfully across `uv` versions, pin in `pyproject.toml` `[tool.uv]` at that point.
- **Persistent-warn lifecycle.** The `uv_lock_out_of_date` soft-warn is intentionally per-session-resolvable — every fire indicates a missing `uv lock` step. Per `soft-warn-lifecycle.md`, persistence across 10 sessions hits the escalation criterion as either: (a) the dep change should be reverted; (b) the lockfile-regeneration step should be CI-automated.

## See also

- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv discipline (the venv is what `uv sync` populates).
- [ADR 0051](0051-routine-mode-and-engine-loop.md) — routine-mode scope_lock (lockfile as read-only target).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate (this adoption qualifies under criteria 2, 3, 4 — see readiness note).
- [ADR 0063](0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — validator phase model (`validate_uv_lock_freshness` in `health_probe`).
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — Layer 1 ops doc.
- [`engine/build_readiness/uv_lockfile_first_exercise.md`](../build_readiness/uv_lockfile_first_exercise.md) — first-exercise readiness note.
- [Issue #65](https://github.com/StarshipSuperjam/paideia/issues/65) — closes.
- [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67), [#68](https://github.com/StarshipSuperjam/paideia/issues/68), [#69](https://github.com/StarshipSuperjam/paideia/issues/69), [#70](https://github.com/StarshipSuperjam/paideia/issues/70), [#71](https://github.com/StarshipSuperjam/paideia/issues/71) — downstream SWE-hardening Issues unblocked by this lockfile adoption.
- [Issue #83](https://github.com/StarshipSuperjam/paideia/issues/83) — SBOM (consumes `uv.lock` when triggered).
