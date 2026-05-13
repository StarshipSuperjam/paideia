# Dependency discipline

> Layer 1 source-of-truth for Python dependency management per [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md). The shape: `pyproject.toml` carries the floor-pinned dependency declarations; `uv.lock` carries the exact transitive resolution; `uv sync` installs from the lock; `validate.py` gates lockfile freshness.

## The shape

| File | Role | Source-of-truth for |
|---|---|---|
| `pyproject.toml` (repo root) | Declares floor-pinned dependencies | What versions a fresh dep install accepts |
| `uv.lock` (repo root) | Records exact resolved transitive graph | What every clone's venv contains, byte-for-byte |
| `engine/tools/requirements.txt` | Retained as a **deprecated redirect pointer** for cold-context discoverability | Nothing — content moved to `pyproject.toml` |
| `.python-version` (repo root) | Pins the Python interpreter | What `uv venv` installs, what hooks run under (per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md)) |

`pyproject.toml` is read by humans (and by `uv lock` when resolving). `uv.lock` is read by `uv sync` when installing. The lockfile is the contract between machines: any two clones running `uv sync` against the same lock get the same packages.

## Install procedure

Fresh setup (or rebuilding after a Python version change):

```sh
cd <repo-root>
uv sync
```

Re-installing after pulling a lockfile change:

```sh
uv sync
```

`uv sync` is idempotent — it brings the venv into exact alignment with the lockfile. No `pip install -r ...` flow remains; the prior `pip install -r engine/tools/requirements.txt` invocation in setup help text is updated to `uv sync`.

## Refresh procedure (when dependencies change)

When you intentionally bump a floor pin in `pyproject.toml`:

```sh
cd <repo-root>
uv lock              # regenerates uv.lock against the new floor
uv sync              # bring local venv into alignment
git add pyproject.toml uv.lock
git commit -m "..."  # MUST stage both files in the same commit
```

The pre-commit hook's `validate_uv_lock_freshness` check fires the `uv_lock_out_of_date` soft-warn if `pyproject.toml` is staged without a matching `uv.lock` regeneration. Soft-warn — not hard-fail — because legitimate cases exist (e.g., editing comments or non-dep metadata in `pyproject.toml` doesn't require a lock refresh, though `uv lock --check` still compares the resolution surface and is deterministic).

## Refresh discipline

**Lockfile is regenerated only when dependencies change.** No drive-by refreshes mid-session. Specifically:

- A session that touches `pyproject.toml`'s `[project.dependencies]` runs `uv lock` in the same commit.
- A session that does NOT touch dependencies must NOT run `uv lock`. The lockfile is a tracked file; spurious refreshes produce noise commits.
- A session that wants a security-driven dep bump (CVE in a transitive) edits the floor pin in `pyproject.toml` to bump above the bad version, then runs `uv lock`.
- Routine-mode sessions (per [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md)) treat `uv.lock` as read-only — the routine-mode scope_lock catches it via the standard predicate (the lockfile is not in any task's `allowed_paths`).

## Adding a new dependency

1. Edit `pyproject.toml`'s `[project.dependencies]` to add a floor-pinned line.
2. Add an inline comment naming what the dep is for and which Phase / ADR it serves (the existing comments in `pyproject.toml` are the pattern).
3. Run `uv lock` to refresh the resolution.
4. Run `uv sync` to install locally.
5. Stage `pyproject.toml` AND `uv.lock` in the same commit.

The contract: every dep in `pyproject.toml` is justified by an inline comment naming its purpose. New deps without justification slip in silently and accumulate.

## Removing a dependency

1. Remove the line from `pyproject.toml`'s `[project.dependencies]`.
2. Run `uv lock` (the resolution may shrink as transitive-only deps drop out).
3. Run `uv sync` (the venv gets the removal).
4. Confirm no remaining import-site references the removed package — `rg "^(import|from) <pkgname>"` from the repo root should return zero results in tracked files.
5. Stage all three (`pyproject.toml`, `uv.lock`, and any callsite removals) in the same commit.

## Security-update workflow

Per [ADR 0069](../adr/0069-dependabot-pip-and-actions-ecosystems.md) (S-0133), [`.github/dependabot.yml`](../../.github/dependabot.yml) runs Dependabot weekly on Mondays against `pip` (repo-root `pyproject.toml`) and `github-actions` (`.github/workflows/`). Dependabot's PRs:

1. Bump the floor pin in `pyproject.toml` to a minor/patch release (or above a CVE'd version).
2. Open a PR with the `pyproject.toml` diff (grouped per ecosystem per ADR 0069 decision 3 — one PR per week per ecosystem for minor/patch; major-version bumps land separately).

**Dependabot does NOT regenerate `uv.lock`.** The `pip` ecosystem reads `pyproject.toml` floors and bumps them; lockfile regen is the reviewer's responsibility. The standard refresh procedure applies (above): pull the Dependabot branch, run `uv lock && uv sync`, amend the PR with the regenerated `uv.lock`, push. The PR template's lockfile-regen reminder line surfaces the step at human-review time. CI hard-fails on `uv lock --check` per [ADR 0083 (engine)](../adr/0083-validate-py-mirror-to-ci.md) decision 3, so a Dependabot PR with stale `uv.lock` cannot merge until regenerated.

The reviewer accepts the PR. **No auto-merge** per ADR 0069 — user merges; CI green is necessary but not sufficient.

**Dependabot PRs are not routine-mode commits** per [ADR 0069](../adr/0069-dependabot-pip-and-actions-ecosystems.md). They originate from GitHub's external apparatus, not from an `auto_target.json` task; routine-mode `scope_lock` does not apply (the routine apparatus never sees the PR).

**Major-version bumps** are deliberately NOT grouped — each opens its own PR for individual review. A major bump in a tool cited by an ADR (psycopg, bandit, mempalace, chromadb, pdfplumber, pypdfium2, reportlab) may require an ADR amendment if upstream contract changes affect the citing decision; see ADR 0069 "Major-version bumps require ADR or amendment."

Out-of-cadence CVE response: a session that wants to apply a CVE fix mid-week (before Dependabot's next Monday run) follows the "Adding a new dependency" procedure with the floor bumped above the bad version. Dependabot is the *batched* refresh procedure, not the only one.

## Validator soft-warn

`validate_uv_lock_freshness` (in `engine/tools/validate.py`, in the `health_probe` phase per ADR 0063 four-phase model) emits the `uv_lock_out_of_date` soft-warn when `uv lock --check` exits non-zero. Three no-op cases:

- `pyproject.toml` absent (project hasn't adopted the lockfile contract).
- `uv.lock` absent (same case).
- `uv` binary not on PATH (clone hasn't installed prerequisites per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md); the missing-prereq surface is `engine/STATE.md`'s "Infrastructure pointers" section, not this gate).

Per [`tools-validate-interpretation.md`](tools-validate-interpretation.md) "Persistent-warn annotation": this soft-warn should NOT persist across sessions — every fire indicates a missing `uv lock` step that the session author should address inline. If it persists across 10 sessions per `soft-warn-lifecycle.md`, escalate as either: (a) the dep change was wrong and should be reverted; (b) a CI regeneration job should be added so the lockfile updates automatically on dep changes.

## Stale Dependabot PR handling

Per [ADR 0080](../adr/0080-boot-time-dependency-version-visibility.md) (S-0147), every session boot surfaces open Dependabot PRs via [`engine/tools/scan_dependabot_prs.py`](../tools/scan_dependabot_prs.py). The surface has three modes:

- **Quiet** (0 open PRs) — no line at boot.
- **FYI** (1–4 open PRs, all <7 days old) — single line: `[session-start] Dependabot PRs: N open (oldest M day(s); review at convenience).`
- **LOUD** (≥5 open PRs OR any PR ≥7 days old) — multi-line block listing each PR with age + mergeable status + a one-line next-action hint.

Threshold: **7 days = one full Dependabot weekly cadence.** A PR open across one Monday refresh is stale by definition.

Defense-in-depth: `validate_dependabot_pr_stale` in [`validate.py`](../tools/validate.py) emits one soft-warn per stale PR. The soft-warn lands in `outcome_summary_soft_warns` so the persistent-warn 3-of-5 surface per [ADR 0042](../adr/0042-soft-warn-lifecycle-archive-canon.md) fires at the next boot if stale PRs accumulate across sessions.

**Valid responses on encountering a stale Dependabot PR:**

1. **Process the PR** (default). Per the "Security-update workflow" section above: pull the branch, run `uv lock && uv sync`, push the regen, wait for CI green, merge.

2. **Close-with-justification** when the dep should not bump (the bump introduces an incompatible contract change without an offsetting safety improvement; the dep is being intentionally pinned at an older version for a documented reason). Close via `gh pr close --comment "<justification>"`; the AI-or-human reviewer records the reason in the comment.

3. **File a follow-up Issue and defer** when a single session genuinely cannot triage the backlog (≥10 stale PRs each requiring per-major-bump review per [ADR 0069](../adr/0069-dependabot-pip-and-actions-ecosystems.md)). Open one tracking Issue labeled `cleanup` referencing the backlog; the next session sees it in the boot surface alongside the stale PRs themselves.

**Anti-pattern:** suppressing the soft-warn by hand-editing `outcome_summary_soft_warns` without addressing the PRs themselves. The persistent-warn surface exists specifically to make this lapse visible across sessions.

## Boot-time version telemetry

Per [ADR 0080](../adr/0080-boot-time-dependency-version-visibility.md), every session boot also surfaces the active venv's Python + chromadb + mempalace versions via [`engine/tools/probe_versions.py`](../tools/probe_versions.py):

```
[session-start] Versions: python=3.12.13 chromadb=1.5.9 mempalace=3.3.5 venv=<path> (worktree-local|main-repo|MISCONFIGURED)
```

The `(worktree-local|main-repo|MISCONFIGURED)` label verifies that [`scrub_env.sh`](../tools/scrub_env.sh)'s PATH-prepend (per [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md)) actually won — when `sys.prefix` matches neither the worktree-local `.venv/` nor the main-repo `.venv/`, the surface emits a LOUD `MISCONFIGURED` marker indicating system Python silently resolved.

**On MISCONFIGURED:** stop substantive work, verify `<repo>/.venv/` exists (run `uv sync` if not), confirm `scrub_env.sh` is sourcing (the wiring is idempotent — re-sourcing won't break anything), and verify the next boot's surface reads `worktree-local` or `main-repo`.

**On version drift between sessions** (chromadb or mempalace version changes without an accompanying ADR amendment or commit referenced in the citing ADR's empirical record): investigate before assuming behavior. A version that changed silently is a clue to a `uv sync` that happened without a `pyproject.toml` commit — likely a Dependabot PR that's been merged or an out-of-band `uv lock` invocation.

## Interaction with other ADRs

- [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md) — the venv exists at `<repo-root>/.venv/` (Python 3.12 pinned via `.python-version`). `uv sync` populates it from the lockfile. `scrub_env.sh` prepends `.venv/bin/` to PATH so all subprocess invocations resolve to the venv-installed binaries.
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — routine sessions treat `uv.lock` as read-only; the scope_lock check enforces.
- [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — `validate_uv_lock_freshness` runs in the `health_probe` phase (subprocess to `uv`).
- [ADR 0069](../adr/0069-dependabot-pip-and-actions-ecosystems.md) — Dependabot adoption (S-0133) automates the security-update half of the refresh procedure via weekly batched PRs on `pip` + `github-actions` ecosystems. Closes [Issue #67](https://github.com/StarshipSuperjam/paideia/issues/67).
- [Issue #83](https://github.com/StarshipSuperjam/paideia/issues/83) — SBOM generation (trigger-gated on deployable artifact) reads `uv.lock` as the canonical transitive-graph source.

## External tool prerequisites

Some gates depend on tools outside the Python venv — non-Python binaries that the venv cannot install. These are project prerequisites; the pre-commit hook hard-fails with installation guidance when one is missing.

| Tool | Pinned version | Installation (Darwin/macOS) | Required by | Contract |
|---|---|---|---|---|
| `gitleaks` | `8.30.1` | `brew install gitleaks` | `engine/tools/hooks/pre-commit` gitleaks step | [ADR 0067](../adr/0067-gitleaks-pre-commit-secret-scanning.md) |
| `gh` | (any recent) | `brew install gh` | `engine/tools/hooks/session-start.sh` CI-red surface; routine_lifecycle_push.py admin-bypass; validate.py `issue_collision` | [ADR 0054](../adr/0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) + [ADR 0083 (engine)](../adr/0083-validate-py-mirror-to-ci.md) |
| `uv` | (any recent) | `brew install uv` | every Python invocation (venv resolution + dep install) | [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) |

**Version-pin discipline.** External tools pinned to a major version. Substantive version drift (major-version bump) requires an ADR amendment because the tool's config schema may change. Forensic minor-version drift is recorded in the consuming ADR's empirical record, not enforced.

**Gate-fail-on-missing.** Every consuming pre-commit step checks `command -v <tool>` and emits actionable stderr (`brew install <tool>` line + ADR pointer) on absence. Failure is loud, not silent.

**Update procedure.** Verify with `<tool> version` (or `<tool> --version`); compare against the table above. Major-version bumps go through an ADR amendment; minor-version drift is forensic-only (recorded in the next session's ENGINE_LOG entry if it changes operational behavior).

## Migration notes (S-0127)

The repo migrated from `engine/tools/requirements.txt` to `pyproject.toml` + `uv.lock` at S-0127. `engine/tools/requirements.txt` is retained as a one-line redirect pointer so cold-context users land on a discoverable surface; the deprecation is final at the next health-check audit. Pre-S-0127 clones running `pip install -r engine/tools/requirements.txt` will still resolve the floor-pinned set (the file content is `# Source-of-truth moved to pyproject.toml ... run \`uv sync\``); the migration is non-breaking for legacy invocations.

## Cross-references

- [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) — the contract.
- [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md) — venv discipline.
- [`engine/tools/scrub_env.sh`](../tools/scrub_env.sh) — PATH wiring (no functional change at S-0127; install command in inline comments updated).
- [`engine/operations/code-discipline.md`](code-discipline.md) — install command in setup section updated to reference this doc.
- [`engine/build_readiness/uv_lockfile_first_exercise.md`](../build_readiness/uv_lockfile_first_exercise.md) — first-exercise readiness note per ADR 0053.
