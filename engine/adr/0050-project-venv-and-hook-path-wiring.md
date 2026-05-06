# ADR 0050 — Project venv (uv-managed) at main repo root with hook PATH wiring

- **Status:** Accepted
- **Date:** 2026-05-04
- **Deciders:** S-0043

## Context

The engine has accumulated seven third-party Python dependencies (`ruff`, `mypy`, `pytest`, `psycopg[binary]`, `beautifulsoup4`, plus `chromadb` carried implicitly as a `probe_palace.py` import, plus `mempalace` carried out-of-band as a user-scope tool) but no isolation around them. Three failure modes have surfaced or are imminent:

**Failure mode A — implicit system-Python coupling.** Eight current Python invocation sites — pre-commit hook (4 calls), `session-start.sh` (2), `mempalace-hook-wrapper.sh` (1), and `validate.py`'s four subprocess gates for `python3 -m {ruff,mypy,pytest}` — all use bare `python3` and rely on system-level package resolution. The user runs system Python 3.9.6 at `/usr/bin/python3`, with user-scope packages at `/Users/shanekidd/Library/Python/3.9/bin/`. A breaking upgrade to system Python or any of the seven libs (chromadb being the most version-sensitive — see ADR 0045's mention of repair-mode and version-coupling concerns) silently propagates into engine behavior. The user reported recurring Python version issues with mempalace specifically.

**Failure mode B — silent missing dependency.** `chromadb` is imported by [`engine/tools/probe_palace.py`](../tools/probe_palace.py) but was never declared in [`engine/tools/requirements.txt`](../tools/requirements.txt). The probe worked because chromadb was incidentally installed in user-scope Python (transitively by mempalace). The first machine to run engine code without that incidental install would fail probe-palace silently. Surfaced when the venv dep resolution showed only 5 packages declared vs. 6+ imported.

**Failure mode C — no reproducibility surface.** Two machines, two snapshots in time, two different dep resolutions. The cost compounds as the project grows. tiktoken is the immediate exemplar: [`scan_context_telemetry.py`](../tools/scan_context_telemetry.py) per ADR 0049 has tiktoken/fallback branching — accurate `tiktoken-o200k_base` counts when the package is present, coarse `chars-div-4-fallback` otherwise. Without explicit pinning, telemetry quality is whatever the system happened to install.

The user surfaced the venv question before committing to "heavy dev work" (Phase 5 epistemology seed-authoring). The cost of paying isolation/reproducibility debt now is small; paying it after the heavy work has accumulated is much larger.

## Decision

The project mechanizes a single project-local Python venv, managed by `uv`, living at `<main_repo_root>/.venv/`. Hook scripts resolve `python3` and other tool entry points to the venv via a sourcing-time PATH prepend in [`engine/tools/scrub_env.sh`](../tools/scrub_env.sh).

### Tool: uv (not plain venv, not pyproject.toml)

`uv` is chosen over `python -m venv` for three reasons: (a) it bundles its own pip, eliminating the system-pip "old version" warning at root; (b) ~10x faster install for chromadb (the heaviest dep); (c) it manages Python interpreter installation natively (`uv venv --python 3.12` downloads and installs CPython 3.12 if the system lacks it). `uv.lock` generation is deferred to a future ADR — the lockfile discipline (when to regenerate, how to handle resolution conflicts) is a separate concern from venv adoption itself.

A migration to `pyproject.toml` is also deferred. The current `requirements.txt` remains the source of truth for project dependencies; `pyproject.toml` would add `[project]` metadata that buys nothing for an internal toolchain that doesn't expose a packaged surface.

### Venv location: main repo root, worktree-local override

The venv lives at `<main_repo_root>/.venv/` — a single install shared across all git worktrees. The hook resolves the location via `git rev-parse --git-common-dir` (which returns `<main_repo>/.git` from any worktree, normalized via `realpath` to handle the relative-path return case). A worktree may opt into its own venv by creating `<worktree_root>/.venv/`; the PATH-prepend logic prefers the worktree-local path when present, falls back to the main repo's path otherwise, and silently no-ops when neither exists or when the script is sourced outside a git repo.

Reasoning: paying the chromadb install cost once across N worktrees beats per-worktree isolation for the typical workflow (a worktree is usually a short-lived experiment that should inherit the project's stable dep set). The override path preserves isolation when actually needed — e.g., testing a chromadb upgrade in a branch without affecting other worktrees.

### Python version: 3.12, pinned via `.python-version`

A new tracked file `.python-version` at the main repo root pins the Python version to `3.12`. uv reads this file when creating venvs. CPython 3.12 is well-supported by all eight project dependencies (verified during S-0043 install) and gives access to `tomllib` in stdlib (mempalace currently requires the `tomli` backport; future versions may drop it).

### Wiring: idempotent PATH prepend at `scrub_env.sh` source time

[`engine/tools/scrub_env.sh`](../tools/scrub_env.sh) gains a sourcing-time side effect: it resolves the worktree and main roots, prefers the worktree-local `.venv/bin/`, falls back to the main repo's `.venv/bin/`, and prepends to `PATH` if either exists. The prepend is idempotent — re-sourcing the file does not duplicate PATH entries, guarded by a `case ":$PATH:"` substring check.

This is the single intervention point. Because [`engine/tools/scrub_env.py`](../tools/scrub_env.py) preserves `PATH` across `scrubbed_env()` subprocess hops (per ADR 0045 — only `GIT_*` is stripped), the prepend propagates through every nested invocation. **Zero changes to `validate.py` and zero changes to any hook script.**

The sourcing-time side effect is intentional: every hook in this project that sources `scrub_env.sh` wants venv tools. Opting out would be the exception, not the rule. The header comment in `scrub_env.sh` documents the behavior so a future cold-context reader does not mistake it for a foot-gun.

### Dependencies: explicit pinning of previously implicit packages

Three additions to [`engine/tools/requirements.txt`](../tools/requirements.txt):

- **`chromadb>=0.5.0`** — was implicit (used by `probe_palace.py`, only worked because of incidental user-scope install via mempalace). Now explicit so probe_palace's expected version is independent of mempalace's pin.
- **`tiktoken>=0.7.0`** — *retired at S-0083 per the ADR 0049 amendment.* Originally activated the accurate-tokenizer branch in `scan_context_telemetry.py` (ADR 0049). The tool and pin were retired together when the cross-session Session-load trend telemetry was retired (zero behavioral signal across three audits per Issue [#32](https://github.com/StarshipSuperjam/paideia/issues/32)). chromadb and mempalace pins remain.
- **`mempalace`** — migrates mempalace from user-scope system Python 3.9 into the project venv. Resolves the user's recurring Python-version issues with the tool. Provides `mempalace` and `mempalace-mcp` binaries; the MCP server config in `.mcp.json` (gitignored) is updated locally to point at `<main_repo>/.venv/bin/mempalace-mcp`. The hook wrapper at [`engine/tools/hooks/mempalace-hook-wrapper.sh`](../tools/hooks/mempalace-hook-wrapper.sh) already calls `mempalace` via PATH lookup, so the scrub_env.sh prepend handles the CLI side automatically. The version floor lives in [`engine/tools/requirements.txt`](../tools/requirements.txt) (single source of truth for the supported version; prose in this ADR and elsewhere does not pin the version inline so the docs don't rot when upstream releases).

## Consequences

**Direct.**

- Every machine that runs engine code now needs `uv` installed (single command: `brew install uv` or the curl installer). Documented as a one-time machine prereq.
- Per-worktree disk cost: zero by default (shared venv at main); ~250MB if a worktree opts into its own override venv (chromadb dominates).
- The four `validate.py` subprocess gates (ruff, mypy, pytest, plus repository SQL checks) execute against pinned versions across machines and across sessions. Variance in lint/type/test results becomes a consequence of code changes, not environment drift.
- *(Retired at S-0083.)* Pre-S-0083: `scan_context_telemetry.py` archives carry accurate `tiktoken-o200k_base` token counts. The Session-load trend section consumed those counts. Both the tool and the section retired at S-0083 per the ADR 0049 amendment; tiktoken pin removed from requirements.txt in the same commit.

**Mempalace migration: bug status verified at S-0043.**

The two upstream bugs documented as Issues [#1](https://github.com/StarshipSuperjam/paideia/issues/1) and [#2](https://github.com/StarshipSuperjam/paideia/issues/2) were verified against the venv-managed mempalace at S-0043:

- **Issue #1 (wing-filtered search "Internal error: Error finding id"):** reproduces verbatim. Same exact error string, same error path. Workaround unchanged: unfiltered `mempalace_search` continues to be the project's standing query pattern.
- **Issue #2 (per-worktree wing names):** behavior changed but bug is not fixed. `mempalace/hooks_cli.py:_wing_from_transcript_path()` now does `encoded.rsplit("-", 1)[-1]` and returns `wing_<last-token>`. For Paideia: main sessions derive `wing_paideia` (closer to expected); worktree sessions derive `wing_<random-hash>` (e.g., `wing_a5d511`) — still per-worktree because each worktree's path-suffix is unique. Additionally, the new `wing_paideia` wing is distinct from the documented bare `paideia` wing (488 drawers, manually curated), so the auto-capture and curated wings remain separate.

[`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) "Known issues" section reflects current behavior. The Issues themselves remain OPEN; the user can decide whether to update them externally.

**Posture preservation.**

- `scrub_env.sh`'s sourcing-time side effect adds visible behavior to a previously pure function-definition file. Documented prominently in the file header. A future session that wants to add another sourcing-time side effect should add it adjacent to the existing block, not as a separate file.
- The override-hatch logic in `scrub_env.sh` (worktree-local preferred over main) is retained even though it's not currently exercised — removing it would force every worktree to share main's venv state, eliminating the test-an-upgrade-in-isolation use case.

**Future work surfaced (not deferred).**

- `uv.lock` adoption — when a concrete reproducibility incident motivates it.
- `pyproject.toml` migration — if Paideia ever publishes a Python package surface.
- Mempalace upstream bug reconciliation — if 3.3.5+ ships fixes for Issues #1 and #2, the venv pin makes upgrade trivial; the ops-doc and Issues should be re-verified at that point.

## See also

- [ADR 0045](0045-shared-state-integrity-discipline.md) — subprocess environment scrubbing; same `scrub_env.sh` file, related concern (PATH preservation across `scrubbed_env()` subprocess hops is what makes this ADR's PATH prepend propagate).
- [ADR 0049](0049-scope-lock-at-boot-and-descope-reorder-audit-at-shutdown.md) — pre-S-0083 the venv enabled tiktoken for that ADR's context-telemetry decision; that decision retired at S-0083 (this ADR's `tiktoken>=0.7.0` pin retired in the same commit). The other two pins this ADR added (chromadb, mempalace) remain.
- [`engine/operations/mempalace-operations.md`](../operations/mempalace-operations.md) — Known issues section, reflects current upstream behavior.
- [Issue #1](https://github.com/StarshipSuperjam/paideia/issues/1), [Issue #2](https://github.com/StarshipSuperjam/paideia/issues/2) — mempalace upstream bugs, verification noted internally.
- [`engine/tools/scrub_env.sh`](../tools/scrub_env.sh), [`engine/tools/scrub_env.py`](../tools/scrub_env.py), [`engine/tools/conftest.py`](../tools/conftest.py) — the three-layer scrub mirror (bash, python, pytest fixture).
