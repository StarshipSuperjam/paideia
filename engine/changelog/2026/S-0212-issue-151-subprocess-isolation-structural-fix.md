---
session_id: S-0212
session_type: build
closed_at: 2026-05-19T19:50:00Z
material_change_class: mixed
module: multi
summary: Issue #151 structural fix landed via subprocess isolation per ADR 0101; new gate verified end-to-end against a live wedge in-session; Issue #151 closed
---

### Added

- [`engine/adr/0101-subprocess-isolation-for-graph-audit.md`](../../adr/0101-subprocess-isolation-for-graph-audit.md) — engine ADR for the structural fix to Issue #151. Five load-bearing premises per ADR 0084 extraction step (criterion #4 fires: call-boundary changes from in-process to subprocess + IPC contract). Moves `_read_graph_from_db` across a process boundary the parent SIGKILLs on a 90s wall-clock cap; existing in-process defenses retained as defense-in-depth inside the worker.
- [`engine/tools/graph_audit_worker.py`](../../tools/graph_audit_worker.py) — new runnable-as-`-m` worker module. Reads `SUPABASE_DB_URL` from env, calls `validate._read_graph_from_db`, emits compact JSON on stdout. Exit codes 0/2/3/4/5 for success/env-missing/psycopg-import/db-error/serialize-error.
- [`engine/tools/test_graph_audit_worker.py`](../../tools/test_graph_audit_worker.py) — 7 tests covering every exit-code path of `worker.main()` plus the compact-JSON-separators contract.
- New `TestGraphAuditSubprocess` class in [`engine/tools/test_validate.py`](../../tools/test_validate.py) — 11 tests covering the wrapper's exit-code dispatch (ImportError on exit 3; RuntimeError with named categories on 2/4/5/unexpected; protocol_error on bad JSON/missing keys) + env propagation (SUPABASE_DB_URL set, GIT_* stripped) + end-to-end TimeoutExpired routing.
- [`engine/build_readiness/graph_audit_subprocess_first_exercise.md`](../../build_readiness/graph_audit_subprocess_first_exercise.md) — first-exercise readiness note per ADR 0053 (criterion #4 fires; 6 surfaces span). All Tier 1 findings (T1-A through T1-D) closed in-session against the live PID 56709 wedge that fired during the implementation commit itself.
- engine_memory `decisions` drawer `9e33ea6d` paired with ADR 0101 — captures the user-adjudicated Option A/B/C alternatives consideration, five load-bearing premises, and consequences.
- engine_memory `pushback` drawer `8fdd0c44` — the symptom-vs-cause framing pushback at session start (when user says "fix X" with multiple root-cause hypotheses alive, surface whether the candidates address the symptom (operationally invisible) or the cause (hypothesis-conditional root-elimination); the symptom-bound option often dominates).
- engine_memory `lesson` drawer `85fb02e9` — `subprocess.run(timeout=N)` SIGKILL escapes libpq `poll()` wedges that no in-process cancellation primitive can; generalizable wedge-class pattern (any Python program holding a long-lived socket where the service can wedge the socket against in-process cancel needs a subprocess kill-switch boundary).
- engine_memory diary `0c78b351` (S-0212 first-person session reflection).

### Changed

- [`engine/tools/validate.py`](../../tools/validate.py) — `validate_graph()` now routes through new `_run_graph_audit_subprocess` wrapper that spawns the worker via `subprocess.run([sys.executable, "-m", "engine.tools.graph_audit_worker"], capture_output=True, timeout=90.0, env=scrubbed_env() with SUPABASE_DB_URL, cwd=REPO_ROOT, text=True)`. New `subprocess.TimeoutExpired` except branch in `validate_graph()` records `graph_audit_subprocess_timeout` as the hard-fail message. Module-level `_GRAPH_AUDIT_SUBPROCESS_TIMEOUT_S = 90.0` constant. Existing `_read_graph_from_db` unchanged; runs inside the worker with all its S-0186/S-0187/S-0208/S-0211 inner defenses preserved.
- [`engine/tools/test_validate.py`](../../tools/test_validate.py) — six existing test monkey-patches migrated from `_read_graph_from_db` → `_run_graph_audit_subprocess` (validate_graph routes through the wrapper now). `TestMain` cases also patch the wrapper to skip cleanly under synthetic_repo (REPO_ROOT is monkey-patched to tmp_path which has no `engine.tools.graph_audit_worker` package).
- [`engine/adr/README.md`](../../adr/README.md) — index updated: ADR 0101 row added.
- [`engine/STATE.md`](../../STATE.md) — "Current phase" row ADR count 100 → 101; "Last session" → S-0212; prior-session rows shifted; "Next session work item" reauthored for S-0213 (Cluster 4 — four-way carry-forward; Issue #151 no longer pending).
- [Issue #151](https://github.com/StarshipSuperjam/paideia/issues/151) — closed with the structural-fix update comment ([comment link](https://github.com/StarshipSuperjam/paideia/issues/151#issuecomment-4491412959)); acceptance criterion #4 retired as obsolete.

### First-exercise empirical findings

The new subprocess gate fired against a live #151 wedge during the very commit that introduced it (`66b346c`). Diagnostic file: [`.engine_reports/hang-diagnostic-2026-05-19T193154.887479Z-56709.json`](../../../.engine_reports/) (PID 56709, gitignored). Behavior:

1. Inner watchdog fired at +45s as designed.
2. `capture_hang_diagnostic()` ran (capture-before-cancel ordering held).
3. Main thread captured wedged in `psycopg.connection.wait()`; netstat captured 2 ESTABLISHED TCP rows to the Supabase pooler.
4. `conn.cancel()` did not return within the next 45s.
5. Parent's 90s outer cap fired and SIGKILLed PID 56709.
6. Parent's control flow returned cleanly; pre-commit recorded `graph_audit_subprocess_timeout` hard-fail.

Premise 2 of ADR 0101 (subprocess.run timeout always delivers SIGKILL regardless of child syscall state) closes verified in production. The implementation commit then landed via `SKIP_ENGINE_HOOKS=1` (audited bypass per ADR 0100) so the fix could reach `origin/main`.

### Cross-references

- [`engine/session/archive/S-0212.json`](../../session/archive/S-0212.json) — canonical structured record.
- [Issue #151](https://github.com/StarshipSuperjam/paideia/issues/151) — closed.
- [ADR 0101](../../adr/0101-subprocess-isolation-for-graph-audit.md) — authoring decision.
- [ADR 0100](../../adr/0100-engine-inspired-hook-installation-and-close-friction-mitigations.md) — `SKIP_ENGINE_HOOKS=1` audited bypass (used once this session for the first-exercise wedge bootstrap; S-0212 = sample 2 of ADR 0100's revised observation window).
- [ADR 0053](../../adr/0053-mechanism-first-exercise-gate.md) — first-exercise gate procedure.
- [ADR 0084](../../adr/0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — extraction step (criterion #4 fires for ADR 0101).
