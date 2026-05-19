---
session_id: S-0211
session_type: build
closed_at: 2026-05-19T18:58:56Z
material_change_class: tool
module: engine/tools/validate.py
summary: Issue #151 hypothesis-agnostic diagnostic capture in validate.py's 45s watchdog; first-exercise empirically falsifies cross-process contamination hypothesis
---

### Added

- `engine/tools/hang_diagnostic.py` — new best-effort capture module. `capture_hang_diagnostic(label, pid=None) -> Path | None` dumps a structured JSON snapshot to `.engine_reports/hang-diagnostic-<iso-ts>-<pid>.json` containing data each #151 root-cause hypothesis predicts: `proc_self` / `lsof_self` / `netstat_supabase` (socket-state evidence for pgbouncer L4-traffic hypothesis); `python_procs` / `python_modules_sample` / `env_scrubbed` / `python_executable` / `psycopg_version` (sibling-Python evidence for cross-process contamination hypothesis); `thread_stacks` (via `sys._current_frames` + `traceback.format_stack`) and `sample_stack` (macOS `sample` 2s) (syscall-level "what is poll() blocked on" data). Module invariants: best-effort (subprocess failures degrade to null fields), bounded (per-call 5s timeout), secret-scrubbing (KEY/SECRET/TOKEN/PASSWORD/URL keys redacted in env_scrubbed), stdlib + engine.tools.timestamps per ADR 0058, lazy `.engine_reports/` directory creation per ADR 0100.
- `engine/tools/test_hang_diagnostic.py` — 12 pytests covering the four invariants: output-key set, lazy directory, pid override, filename portability (no colons), subprocess failure modes (FileNotFoundError / TimeoutExpired / nonzero-exit-with-stderr), secret-pattern matching case-insensitive, non-secret passthrough, thread-stack inclusion, mkdir OSError → None.

### Changed

- `engine/tools/validate.py:_watchdog()` — when the 45s `wall_clock_timeout_s` cap fires, the watchdog now calls `capture_hang_diagnostic("graph_audit_watchdog")` BEFORE `conn.cancel()`. Both wrapped in separate `try/except` blocks so capture failure does not block cancellation and cancellation failure does not block exit. Comment block above `psycopg.connect(...)` expands from "four caps" to "four caps plus one diagnostic-capture layer" (S-0211), cross-referencing lesson drawer `c8f90de5` (pgbouncer L4-traffic hypothesis) and STATE.md row 54 (user cross-process Python contamination hypothesis).
- `engine/tools/test_validate.py:TestReadGraphFromDbTimeouts` — one new pytest `test_watchdog_invokes_capture_before_cancel` verifying the capture-before-cancel ordering via call-order tracking. Existing three tests unchanged.

### Empirical (first-exercise findings — PID 41424 wedge dump)

The capture fired against a live #151 wedge during the very commit that introduced it. File: `.engine_reports/hang-diagnostic-2026-05-19T183424.199794Z-41424.json`. (1) Main thread wedged in `psycopg.connection.wait()` on `pgconn.socket` — predicted poll() hang confirmed at the kernel layer. (2) ESTABLISHED TCP to ec2-18-214-78-123:5432 at moment of capture — keepalive did NOT fire (consistent with the pgbouncer L4-traffic hypothesis). (3) `conn.cancel()` ITSELF wedged for 6+ minutes against the same socket — empirically pins the S-0208 falsification shape and validates the deliberate capture-before-cancel ordering choice. (4) No suspect non-project Python processes at wedge time (only 4× `engine.memory.mcp_server`, project-internal, SQLite per ADR 0091, not Supabase) — **the user-hypothesized cross-process Python contamination vector is NOT supported by the captured evidence.** Surviving live hypothesis: structural to the pooler.

### Fixed (same-session, fix-in-context)

- `engine/tools/hang_diagnostic.py:netstat_supabase` grep accepts both `:5432/:6543` (Linux) and `.5432/.6543` (macOS) separators — discovered via the wedge dump's empty netstat field despite a live ESTABLISHED TCP per `lsof`. macOS BSD netstat -an renders addresses with dot separator; Linux uses colon.

### Bypass log

Two commits landed via SKIP_ENGINE_HOOKS=1 audited bypass per ADR 0100 — the live #151 wedge blocks the in-hook graph_audit phase, and the fix is the diagnostic capture we're trying to land. User explicitly authorized each bypass at the AskUserQuestion prompt. Audit trail at `.engine_reports/hook-bypass.log`.

### Cross-references

- Issue #151 — diagnostic-mechanism update + first-exercise findings posted via [comment](https://github.com/StarshipSuperjam/paideia/issues/151#issuecomment-4490997861); observation-window guidance revised to "measures from the first session AFTER a structural fix lands."
- lesson drawer `4e3c8296` — capture-before-cancel ordering load-bearing per the S-0211 empirical pinning of conn.cancel-wedge against poisoned socket.
- pushback drawer `94e4ea6e` — hypothesis-agnostic data collection over committed hypothesis testing when bug is intermittent.
- ADR 0091 (engine_memory substrate) — citations populated by `scan_engine_memory_citations.py` at step 12.
- ADR 0100 (close-friction mitigations) — SKIP_ENGINE_HOOKS=1 audited bypass used twice; entries logged.
