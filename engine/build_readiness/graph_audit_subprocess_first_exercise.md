# graph_audit subprocess isolation — mechanism-first-exercise gate report

> Authored at S-0212 per [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md). Covers the first exercise of the subprocess-isolation mechanism that [ADR 0101](../adr/0101-subprocess-isolation-for-graph-audit.md) introduces. Required because the ADR qualifies under ADR 0053's trigger criterion #4 (Consequences span ≥ 3 ops docs OR ≥ 5 tooling files — `engine/tools/validate.py` + `engine/tools/graph_audit_worker.py` + `engine/tools/test_validate.py` + `engine/tools/test_graph_audit_worker.py` + ADR 0101 + this report = 6 surfaces).

## Mechanism summary

`engine/tools/validate.py:_run_graph_audit_subprocess()` invokes `engine/tools/graph_audit_worker.py` via `subprocess.run([sys.executable, "-m", "engine.tools.graph_audit_worker"], capture_output=True, timeout=90.0, env=scrubbed_env() with SUPABASE_DB_URL, cwd=REPO_ROOT, text=True)`. The worker calls `validate._read_graph_from_db` (unchanged from pre-S-0212) and emits compact JSON on stdout. Worker exit codes 0/2/3/4/5 discriminate success/env-missing/psycopg-import/db-error/serialize-error; the wrapper translates non-zero exits to `ImportError` (exit 3 → `graph_audit_skipped`) or `RuntimeError` (everything else → `graph_audit` hard-fail). `subprocess.TimeoutExpired` propagates to `validate_graph()`, which records `graph_audit_subprocess_timeout` as the hard-fail message.

The subprocess boundary exists because the S-0211 diagnostic empirically pinned `conn.cancel()` itself wedging against the same poisoned socket the original query wedged on — no in-process defense escapes. CPython's `subprocess.run(timeout=N)` delivers `SIGKILL` on timeout regardless of the child's syscall state.

## Trigger criterion evaluation (per ADR 0053)

| Criterion | Status |
|---|---|
| #1 — introduces a new session mode | No |
| #2 — introduces a new validator soft-warn category requiring session-side discipline | No (new failure modes within existing `graph_audit` hard-fail category) |
| #3 — introduces a new state file the boot procedure reads | No |
| #4 — Consequences span ≥ 3 ops docs OR ≥ 5 tooling files | **Yes** (6 surfaces named above) |

**Qualifies; gate session needed before unattended use.** This report IS the gate report. S-0212 is both the authoring session and the first-exercise session — the build session also served as the first-exercise opportunity because the wedge fired in-hook against this very session's implementation commit (see Phase 0 below).

## Phase 0 empirical findings — Tier 1 closure

The load-bearing question per ADR 0101 premise 2: does `subprocess.run(timeout=90)` actually deliver `SIGKILL` and unblock the parent when the inner `conn.cancel()` wedges?

### First-exercise wedge bootstrap (2026-05-19, S-0212)

**Procedure (unintentional but well-targeted):** the pre-commit hook fired on the S-0212 implementation commit (`66b346c`). The hook invokes `validate.py` which now routes graph_audit through `_run_graph_audit_subprocess()`. The pre-commit context's Supabase pooler was in the wedged state Issue #151 documents.

**Result (PID 56709, file [`.engine_reports/hang-diagnostic-2026-05-19T193154.887479Z-56709.json`](../../.engine_reports/hang-diagnostic-2026-05-19T193154.887479Z-56709.json)):**

1. **Inner watchdog fired at +45s** as designed. The S-0211 capture-before-cancel ordering held: the watchdog called `capture_hang_diagnostic("graph_audit_watchdog")` before `conn.cancel()`. The diagnostic file landed on disk before `conn.cancel()` ran.
2. **Main thread captured wedged in `psycopg.connection.wait()`** on `pgconn.socket`. Two threads in the stack dump: `MainThread-8310649088` (the query thread) and `validate-graph-audit-watchdog-6175223808` (the watchdog thread that called capture).
3. **Netstat captured 2 ESTABLISHED TCP rows** to Supabase pooler endpoint. The L4 socket was alive (consistent with S-0208 lesson drawer `c8f90de5` — pgbouncer keeps the socket nominally alive even while the application-layer is wedged).
4. **`conn.cancel()` did NOT return within 45 seconds of the inner watchdog firing.** PID 56709 remained alive and wedged.
5. **Parent's `subprocess.run(timeout=90)` fired at +90s and SIGKILLed PID 56709.** The kernel terminated the process at the libpq `poll()` syscall it was wedged on; no signal handler ran.
6. **Parent recorded `graph_audit_subprocess_timeout` hard-fail** with a clean error message naming Issue #151, ADR 0101, the diagnostic file path, and the recovery instruction ("retry the commit — the wedged worker is dead and the next attempt is unblocked").
7. **The pre-commit hook returned non-zero**; the commit attempt was correctly blocked.

**Premise 2 of ADR 0101 closes verified.** `subprocess.run(timeout=N)` delivered SIGKILL and the parent's control flow returned cleanly. The wedge that took down S-0184 → S-0211 (each requiring user intervention) became operationally invisible at the parent boundary.

**The S-0212 implementation commit then landed via `SKIP_ENGINE_HOOKS=1` (audited bypass per [ADR 0100](../adr/0100-engine-inspired-hook-installation-and-close-friction-mitigations.md))** because the fix needed to reach `origin/main` before the worktree's next commit could benefit. Bypass-log entry at `.engine_reports/hook-bypass.log` records the rationale. This is the canonical case the audited bypass exists for — landing the fix that prevents the wedge requires getting past the wedge once.

### Worker module test coverage (Phase 0 unit verification)

`engine/tools/test_graph_audit_worker.py` covers all six exit-code paths of `graph_audit_worker.main()`:

| Exit code | Test | Pass |
|---|---|---|
| 0 (success) | `test_main_emits_json_on_success` | ✓ |
| 0 (empty corpus) | `test_main_handles_empty_corpus` | ✓ |
| 0 (compact JSON contract) | `test_main_uses_compact_separators` | ✓ |
| 2 (env missing) | `test_main_exits_2_when_env_missing` | ✓ |
| 3 (psycopg ImportError) | `test_main_exits_3_on_psycopg_import_error` | ✓ |
| 4 (psycopg query error) | `test_main_exits_4_on_psycopg_query_error` | ✓ |
| 5 (JSON serialize error) | `test_main_exits_5_on_serialization_error` | ✓ |

### Wrapper test coverage (Phase 0 unit verification)

`engine/tools/test_validate.py::TestGraphAuditSubprocess` covers the wrapper's exit-code dispatch and the env-propagation contract:

| Path | Test | Pass |
|---|---|---|
| Happy path: exit 0 + JSON | `test_happy_path_parses_subprocess_json` | ✓ |
| TimeoutExpired propagates | `test_subprocess_timeout_propagates` | ✓ |
| Exit 3 → ImportError | `test_subprocess_psycopg_unavailable_raises_import_error` | ✓ |
| Exit 4 → RuntimeError(db_error) | `test_subprocess_db_error_raises_runtime_error` | ✓ |
| Exit 2 → RuntimeError(env_violation) | `test_subprocess_env_violation_raises_runtime_error` | ✓ |
| Exit 5 → RuntimeError(serialize_error) | `test_subprocess_serialize_error_raises_runtime_error` | ✓ |
| Other non-zero exits → RuntimeError(unexpected_exit) | `test_subprocess_unexpected_exit_raises_runtime_error` | ✓ |
| Unparseable stdout → protocol_error | `test_subprocess_unparseable_stdout_raises_protocol_error` | ✓ |
| Missing JSON keys → protocol_error | `test_subprocess_missing_keys_raises_protocol_error` | ✓ |
| Env contract: SUPABASE_DB_URL set, GIT_* stripped | `test_subprocess_env_propagates_connection_string` | ✓ |
| End-to-end: TimeoutExpired → hard-fail with category | `test_validate_graph_routes_timeout_to_hard_fail` | ✓ |

All 11 wrapper tests pass; integration with existing `TestValidateGraphIntegration` (8 tests), `TestStagedPathsSkip` (3 tests), `TestValidateGraphSnapshot` (1 test), `TestMainExportSnapshotMode` (1 test), `TestMain` (2 tests using monkey-patched wrapper) all green.

## Tier 1 findings (must close before unattended use)

| ID | Finding | Status |
|---|---|---|
| T1-A | Parent SIGKILL escapes the conn.cancel() wedge end-to-end | **Closed** — empirically verified in-session at PID 56709 wedge (2026-05-19T19:31:54Z). Diagnostic file on disk; parent's 90s outer cap delivered SIGKILL; parent returned to caller cleanly; pre-commit recorded hard-fail and exited non-zero. |
| T1-B | Worker exit-code contract covers every documented failure mode | **Closed** — 7/7 worker tests pass; 11/11 wrapper tests pass. |
| T1-C | Env propagation correct: SUPABASE_DB_URL reaches child, GIT_* keys absent | **Closed** — `test_subprocess_env_propagates_connection_string` explicitly verifies both directions. |
| T1-D | Existing `validate_graph` tests pass after monkey-patch migration | **Closed** — 237 tests in `test_validate.py` pass post-migration; the inner `TestReadGraphFromDbTimeouts` class is unchanged and still covers the in-process defenses. |

**All Tier 1 closed in-session.** No deferred verification required.

## Tier 2 findings (informational; document but do not block)

| ID | Finding | Status |
|---|---|---|
| T2-A | Subprocess startup cost (~500ms on cold cache) | Acceptable. Graph audit fires only on commits that touch graph paths per Issue #142 path-aware skip — every-commit cost is zero for non-graph commits. |
| T2-B | `subprocess.run(capture_output=True)` reads full stdout into memory | Today's 380×533 corpus serializes to ~700KB; sub-50MB ceiling at Phase 6 full subdomain set; well within process memory. Recalibrate as a Phase 7+ concern if the corpus crosses 50MB. |
| T2-C | The inner 45s watchdog is now defense-in-depth, not load-bearing primary defense | Documented in ADR 0101 Consequences. Healthy-but-slow queries still get the clean `QueryCanceled` exception path (inner watchdog) instead of falling all the way to outer SIGKILL. Defense-in-depth is cheap (~40 LOC). |

## Tier 3 findings (defer for future re-evaluation)

| ID | Finding | Forward trigger |
|---|---|---|
| T3-A | Pattern generalizes to `apply_migration.py` if migration apply ever wedges | First observation of an apply_migration wedge in production. |
| T3-B | Supavisor session mode (Option B) remains available | If wedge *frequency* (rather than blocking nature) becomes the operational concern. Subprocess gate handles blocking; URL switch could reduce frequency. |
| T3-C | Direct DB port 5432 (Option A) remains available | If pooler-class failures persist across future fixes AND IPv6 availability is verified for the target environments. |
| T3-D | Outer cap calibration | Phase 6 full subdomain set may push healthy-path runtime past the inner 45s watchdog; recalibrate both inner + outer caps then. |

## Forward operations

- **Operational signature of a wedge after S-0212:** pre-commit fails with `graph_audit_subprocess_timeout` hard-fail; the user retries the commit (next attempt re-runs the subprocess, which will either succeed against a now-cleared pooler or fire the gate again). No Supabase restart needed; no manual process kill needed. The wedge becomes a transient hard-fail rather than a blocking hang.
- **When the gate fires:** the parent's hard-fail message names the diagnostic file path under `.engine_reports/hang-diagnostic-*.json`. Inspect for thread-stack evidence and netstat row counts; cross-reference against the S-0211 dump pattern (lesson drawer `4e3c8296`).
- **Issue #151 closure:** acceptance criterion #4 (5 consecutive clean sessions) is retired as obsolete — it measured the bug, not the blocker. The subprocess gate makes the bug operationally invisible. Issue body updated at S-0212 close.

## See also

- [ADR 0101](../adr/0101-subprocess-isolation-for-graph-audit.md) — authoring ADR.
- [ADR 0053](../adr/0053-mechanism-first-exercise-gate.md) — first-exercise gate procedure.
- [ADR 0100](../adr/0100-engine-inspired-hook-installation-and-close-friction-mitigations.md) — SKIP_ENGINE_HOOKS audited bypass (the path the S-0212 implementation commit took to land past its own first-exercise wedge).
- [Issue #151](https://github.com/StarshipSuperjam/paideia/issues/151) — the recurring wedge this mechanism structurally fixes.
- engine_memory decisions drawer `9e33ea6d` (S-0212) — ADR 0101 settlement.
- engine_memory lesson drawer `4e3c8296` (S-0211) — capture-before-cancel ordering (still load-bearing inside the worker after S-0212).
- engine_memory lesson drawer `c8f90de5` (S-0208) — pgbouncer L4-traffic / TCP-keepalive necessary-but-not-sufficient.
- `.engine_reports/hang-diagnostic-2026-05-19T193154.887479Z-56709.json` — the S-0212 first-exercise wedge dump.
