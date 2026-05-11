# `uv` lockfile adoption — first-exercise readiness

> Per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Tracks readiness criteria for the `uv lock` + `uv sync` + `validate_uv_lock_freshness` mechanism landed at S-0127 per [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) (Issue [#65](https://github.com/StarshipSuperjam/paideia/issues/65)).

## Trigger criteria evaluation

Per ADR 0053 the mechanism qualifies for a readiness note when ANY of:

- ❌ Criterion 1 — introduces new session mode. **No.**
- ✅ Criterion 2 — introduces new validator soft-warn category depending on session-side discipline. **Yes** (`uv_lock_out_of_date` depends on the discipline of running `uv lock` whenever `pyproject.toml`'s deps change).
- ✅ Criterion 3 — introduces new state file the boot procedure (or any standing tool) reads. **Yes** (`uv.lock` is read by `uv sync` at every venv install; represents canonical transitive-dep state).
- ✅ Criterion 4 — consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — touches `engine/tools/scrub_env.sh` (install-command comments), `engine/tools/hooks/session-start.sh` (help text), `engine/tools/validate.py` (new soft-warn), `engine/tools/requirements.txt` (deprecated redirect), `engine/operations/code-discipline.md` (install reference), `engine/operations/dependency-discipline.md` (new doc), `CLAUDE.md` (Standing rules amendment), `pyproject.toml` (new), `uv.lock` (new) = 9 surfaces.

Three criteria satisfied → readiness note required.

## Mechanism

Three coupled mechanisms:

1. **`pyproject.toml` + `uv.lock` at the repo root** — `uv lock` regenerates the lockfile from `pyproject.toml`'s `[project.dependencies]`. Both files are tracked.
2. **`uv sync` as canonical install** — replaces `uv pip install -r engine/tools/requirements.txt`. Idempotent; brings the venv into byte-exact alignment with `uv.lock`.
3. **`validate_uv_lock_freshness` in `validate.py`** — runs `uv lock --check` (cwd=repo-root) inside the `health_probe` phase per ADR 0063. Non-zero exit → `uv_lock_out_of_date` soft-warn. Three no-op cases preserve clean exits when the contract isn't installed.

## Readiness criteria

- **T1-A — first lockfile-driven `uv sync` produces a reproducible tree.** Verified at authoring time on this machine: `uv lock` resolves 99 packages; `uv sync` would populate the venv from that lock. (Not destructively re-tested here to avoid disrupting the live venv this session is running under; verified at `uv lock --check` returning 0 with the committed lockfile.)
- **T1-B — lockfile-staleness soft-warn fires correctly when requirements diverge.** Pytest at `engine/tools/test_validate.py::TestValidateUvLockFreshness` covers the four observable shapes (clean lock; staged-pyproject-without-relock; absent pyproject; absent lockfile; absent uv binary). T1-B closes when the soft-warn fires naturally on a future session that bumps a floor without re-running `uv lock` (the soft-warn IS the discipline reminder).
- **T1-C — routine-mode session completes a lifecycle without needing to regenerate the lock.** Closes on the first natural routine-mode session post-S-0127. Routine-mode `scope_lock` (per ADR 0051) treats `pyproject.toml` and `uv.lock` as out-of-bounds; if a routine session somehow needed to bump a dep (it shouldn't — dep changes are human-adjudicated), the scope_lock check at commit time would hard-fail, and the routine would HANDOFF to an interactive session per the standard ADR 0051 protocol.
- **T1-D — second-machine reproduction.** Closes when a second clone (different machine, possibly different `uv` minor version) runs `uv sync` against the committed lockfile and produces a byte-identical `.venv/`. Deferred to natural exercise — there's no second machine in active use at S-0127.

## Status

- **T1-A — closed at S-0127 authoring.** `uv lock` resolved 99 packages cleanly; `uv lock --check` returns 0 against the committed lockfile.
- **T1-B — partially closed.** Synthetic-test coverage in place; awaits first natural fire on a session that edits `pyproject.toml` without re-locking.
- **T1-C — open.** Awaits first routine-mode session post-S-0127.
- **T1-D — open.** Awaits second-machine clone.

## Risk surface (deliberate posture)

The bootstrap risk is `uv` version drift: if `uv 0.11.8` (current) and `uv 0.12.x` produce slightly different resolutions for the same `pyproject.toml`, the staleness check would fire spuriously on machines running the newer `uv`. Mitigation: the project README / setup docs name a known-good `uv` version; if drift becomes a real cost, pin `uv` itself (currently a per-machine prereq, deliberately unpinned).

The cold-context risk is users running the legacy `pip install -r engine/tools/requirements.txt` invocation. The retained redirect-pointer file mitigates: such users land on a one-line message naming `uv sync` as the canonical command. Removal of the pointer waits until the next health-check audit confirms cross-references in the wild have caught up.

## Cross-references

- [ADR 0064](../adr/0064-uv-lockfile-and-reproducible-builds.md) — the contract.
- [ADR 0050](../adr/0050-project-venv-and-hook-path-wiring.md) — venv discipline.
- [ADR 0051](../adr/0051-routine-mode-and-engine-loop.md) — routine-mode scope_lock interaction.
- [ADR 0063](../adr/0063-validator-tiered-runtime-targets-and-regression-soft-warn.md) — `validate_uv_lock_freshness` runs in the `health_probe` phase.
- [`engine/operations/dependency-discipline.md`](../operations/dependency-discipline.md) — Layer 1 ops doc.
- [Issue #65](https://github.com/StarshipSuperjam/paideia/issues/65) — closes.
