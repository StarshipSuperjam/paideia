# ADR 0101 — Subprocess isolation for graph_audit (Issue #151 structural fix)

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** S-0212

## Context

Issue #151 has accumulated four mitigations across S-0186 → S-0211. Each addressed the wedge symptom at a different layer; none escaped it. The S-0211 hypothesis-agnostic diagnostic capture ([`engine/tools/hang_diagnostic.py`](../tools/hang_diagnostic.py)) fired against a live wedge (PID 41424 dump at [`.engine_reports/hang-diagnostic-2026-05-19T183424.199794Z-41424.json`](../../.engine_reports/hang-diagnostic-2026-05-19T183424.199794Z-41424.json)) and produced one load-bearing empirical fact:

> **`conn.cancel()` itself wedged for 6+ minutes against the same poisoned socket.**

The 45s in-process watchdog (S-0187) fires PQcancel via the libpq protocol. PQcancel opens a *new* TCP connection to the same pooler endpoint to issue the cancel. When the pooler is the wedge source (the surviving live hypothesis after S-0211 falsified cross-process Python contamination), the cancel-channel hits the same wedge as the original query channel. The watchdog thread blocks on `conn.cancel()`; the main thread keeps blocking on `cur.execute()`; the process is a permanently stuck pair of threads holding GIL handoffs.

**No in-process defense escapes this.** TCP keepalive (S-0208) doesn't fire because the pgbouncer L4 traffic keeps the socket nominally alive; `statement_timeout` (S-0186) is stripped by transaction-pool mode; `connect_timeout` (S-0186) only bounds the initial handshake. The S-0211 lesson drawer `4e3c8296` captured this: *"capture-before-cancel ordering is load-bearing because conn.cancel() itself can wedge against the same poisoned socket."*

The escape requires a process boundary the parent controls. The OS can always SIGKILL a child; the kernel does not care whether the child's threads are wedged on libpq sockets, because SIGKILL is delivered to the kernel-side process table directly.

### Load-bearing premises

(per [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) extraction step. This ADR triggers criterion #4 — call-boundary changes from in-process to subprocess + IPC contract.)

1. **`conn.cancel()` can wedge indefinitely against a poisoned socket.** Empirically verified at S-0211 PID 41424 (6+ minute wedge in cancel against the same socket the original query wedged on). Falsifier: future wedge where `conn.cancel()` returns within seconds. Test status: passed; lesson drawer `4e3c8296` is the canonical record.

2. **`subprocess.run(..., timeout=N)` always delivers SIGKILL on timeout, regardless of the child's syscall state.** CPython's subprocess module implementation: on TimeoutExpired, the parent calls `Popen.kill()` (POSIX `kill(pid, SIGKILL)` — unblockable, undeflectable). The kernel terminates the process at the syscall boundary it's wedged on; libpq's `poll()` does not get a chance to handle anything because SIGKILL bypasses signal handlers. Falsifier: a Python implementation where `subprocess.run` timeout does NOT SIGKILL (CPython has this behavior; PyPy and Jython match per their stdlib mirroring). Test status: assumed; first-exercise will exercise a real subprocess kill on a real wedge.

3. **JSON serialization of the graph-read result is correct under the current schema.** Node rows carry `id` (uuid str), `label` (text), `domain` (text), `summary` (text), `teaching_notes` (text), `rigor_score_computed` (float), `confidence_level` (text), `status` (text). Edge rows carry `id` (uuid str), `source_id` (uuid str), `target_id` (uuid str), `edge_type` (text), `edge_layer` (text), `evidence` (text), `expert_confidence` (text), `counterexamples` (text array), `provenance` (jsonb-decoded dict). All are JSON-safe under Python's default `json.dumps` with `default=str` for any UUID stragglers. Falsifier: a future seed introducing binary bytea evidence or a custom psycopg type that doesn't serialize. Test status: passed via the existing 380-node × 533-edge corpus in production today; will be re-verified at first exercise.

4. **A 90s parent-side outer cap is sufficient under any non-pathological condition.** Inner: 45s in-process watchdog + 10s connect_timeout = 55s worst-case healthy run. Outer adds 35s for subprocess startup (Python interpreter cold start: ~200ms on the venv per ADR 0050; psycopg import: ~300ms; module load: ~100ms — total well under 1s) + JSON dump of ~1MB result (~50ms). The 35s margin is dominated by safety, not measured contribution. Falsifier: a healthy graph_audit run exceeding 90s on production data. Test status: passed for today's 380×533 corpus; recalibrate if Phase 6's full subdomain set pushes runtime past the 45s inner watchdog (at which point both caps need rethinking, not just this one).

5. **`SUPABASE_DB_URL` propagates through `scrubbed_env()` to the subprocess.** Per ADR 0045, `scrubbed_env()` strips only `GIT_*` prefixed variables. `SUPABASE_DB_URL` does not start with `GIT_` and is preserved by definition. Falsifier: a future scrub rule expanded to strip auth-bearing env vars. Test status: passed by `scrub_env.py`'s implementation contract (the `_GIT_ENV_PREFIX` constant is hard-coded and would require a deliberate ADR amendment to change); the new pytest in `test_validate.py` asserts the env round-trip explicitly.

### Why an architectural ADR and not an inline fix

Three things make this a contract-shape change, not a refactor:

- **The call boundary moves from in-process to subprocess.** `_read_graph_from_db` no longer runs in the validate.py process; it runs in a child the parent can kill. The IPC contract (JSON-over-stdout, exit codes) is a public surface other engine tools may need to consume.
- **The outer cap supersedes the inner watchdog as the load-bearing defense.** S-0187 made the watchdog load-bearing; S-0211 made it inadequate. This ADR demotes the watchdog to inner defense-in-depth and elevates the subprocess SIGKILL to the load-bearing boundary. That re-shape is the kind of decision that survives only if it's written down — otherwise the watchdog code reads as the primary defense to future readers.
- **`apply_migration.py` will face the same wedge class.** [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md)'s wrapper uses the same psycopg + transaction-pool + Supavisor pattern. If migration apply ever wedges (it hasn't yet, but the surface is structurally identical), the same subprocess pattern would generalize. Documenting the pattern here makes the future port straightforward.

## Decision

`_read_graph_from_db()` is invoked from `validate.py`'s `validate_graph()` orchestrator via a subprocess (`engine/tools/graph_audit_worker.py`), with a parent-side hard wall-clock timeout. The subprocess does the psycopg work and emits a JSON result on stdout; the parent enforces the outer cap and parses or fails.

Five coupled choices mechanize the adoption.

### 1. New module `engine/tools/graph_audit_worker.py`

A standalone, runnable-as-`-m` module with one `main()` entry point. Reads `SUPABASE_DB_URL` from env (mandatory — caller is the parent's `validate.py`, which has already verified the env is set; absence is a contract violation, exit 2). Calls `engine.tools.validate._read_graph_from_db(SUPABASE_DB_URL)`. Serializes the result as a single line of JSON on stdout: `{"nodes": [...], "edges": [...]}`. Exit codes:

- **0** — success; nodes+edges on stdout.
- **2** — `SUPABASE_DB_URL` env missing (contract violation; parent must have set it).
- **3** — psycopg `ImportError`. Caller's `audit_skipped` path should have caught this; if it didn't, exit-3 routes through the parent's `except` and lands as `graph_audit_skipped`.
- **4** — psycopg connect or query error (the same `Exception` class S-0211's `_read_graph_from_db` already raises). Stderr carries the exception type + message; parent surfaces as `graph_audit` hard-fail.
- **5** — JSON serialization failure on the result (defense-in-depth; premise 3 says this can't happen with today's schema, but if a future row carries an unserializable type, exit-5 is the discrimination point).

The worker imports `validate` lazily inside `main()` so test fixtures can monkey-patch the function before import.

### 2. Parent-side wrapper in `validate.py`

`validate_graph()` invokes the worker via `subprocess.run([sys.executable, "-m", "engine.tools.graph_audit_worker"], capture_output=True, timeout=_GRAPH_AUDIT_SUBPROCESS_TIMEOUT_S, env=scrubbed_env(), text=True)`. Default timeout: `90.0` seconds. Dispatch on result:

- **`returncode == 0` + parseable stdout** — extract `nodes`, `edges`; continue into the existing soft-warn / hard-fail loops in `validate_graph()`.
- **`subprocess.TimeoutExpired`** — `subprocess.run` has already SIGKILLed the child; record a `graph_audit` hard-fail with category `graph_audit_subprocess_timeout` (new failure mode within the existing category, not a new category). Parent control returns immediately. The pre-commit hook fails fast; subsequent commits are not blocked by a wedged child.
- **`returncode == 2`** (env contract violation) — re-raise as `RuntimeError`; this is a parent bug, not a runtime condition.
- **`returncode == 3`** — `graph_audit_skipped`.
- **`returncode == 4`** — `graph_audit` hard-fail carrying the worker's stderr.
- **`returncode == 5`** — `graph_audit` hard-fail with category `graph_audit_subprocess_protocol_error`.
- **Unparseable stdout on `returncode == 0`** — `graph_audit_subprocess_protocol_error`.

The subprocess timeout constant `_GRAPH_AUDIT_SUBPROCESS_TIMEOUT_S` lives next to the existing `_GRAPH_AUDIT_WALL_CLOCK_TIMEOUT_S` so future tuning is localized.

### 3. Inner defenses retained as defense-in-depth

`connect_timeout=10` (S-0186), `_KEEPALIVE_KWARGS` (S-0208), in-process watchdog with `conn.cancel()` (S-0187), `capture_hang_diagnostic` invocation in the watchdog (S-0211) — all preserved unchanged. They run inside the subprocess. The diagnostic capture runs inside the subprocess too, so the file lands at `.engine_reports/hang-diagnostic-*.json` even when the subprocess is later SIGKILLed (Python flushes on `print()` to stdout/stderr but the diagnostic writes via `Path.write_text` and the underlying `write()` syscall is line-buffered; the file is on-disk by the time the watchdog returns). The capture-before-cancel ordering remains load-bearing inside the child.

The reason for the layered defense:

- Healthy queries: inner watchdog never fires; subprocess returns in milliseconds; outer timeout never fires.
- Server-side query stall (statement_timeout territory if it worked): inner watchdog fires, `conn.cancel()` returns cleanly, subprocess raises QueryCanceled, exits 4; outer timeout never fires.
- Pooler wedge with cancel still functional: inner watchdog fires, `conn.cancel()` returns (slow), subprocess raises QueryCanceled, exits 4; outer timeout might fire if cancel was slow, in which case the subprocess is SIGKILLed cleanly.
- **Pooler wedge with `conn.cancel()` itself wedged (the S-0211 case)**: inner watchdog issues `conn.cancel()` which blocks; subprocess never exits; outer timeout fires; parent SIGKILLs. **This is the failure mode the ADR exists for; no other layer escapes it.**

### 4. Tests cover all four return-code paths plus the timeout path

New pytests in `test_validate.py::TestGraphAuditSubprocess`:

- `test_happy_path_parses_subprocess_json` — stub `subprocess.run` to return `CompletedProcess(returncode=0, stdout='{"nodes":[],"edges":[]}', stderr='')`; assert `validate_graph()` returns a clean `ValidationResult` with `graph_audit` in checks_run.
- `test_subprocess_timeout_records_hard_fail` — stub `subprocess.run` to raise `TimeoutExpired`; assert `graph_audit_subprocess_timeout` hard-fail surfaces.
- `test_subprocess_db_error_records_hard_fail` — stub returns exit 4 with stderr; assert hard-fail body carries stderr content.
- `test_subprocess_psycopg_unavailable_records_skip` — stub returns exit 3; assert `graph_audit_skipped` in checks_run.
- `test_subprocess_protocol_error_on_unparseable_stdout` — stub returns exit 0 with junk stdout; assert `graph_audit_subprocess_protocol_error` hard-fail.
- `test_subprocess_env_propagates_supabase_db_url` — capture the `env=` arg passed to `subprocess.run`; assert `SUPABASE_DB_URL` is present and `GIT_*` keys are absent.

Worker tests in new `test_graph_audit_worker.py`:

- `test_worker_main_emits_json_on_success` — monkey-patch `validate._read_graph_from_db` to return a known list pair; capture stdout; assert it round-trips through `json.loads`.
- `test_worker_main_exits_2_when_env_missing`.
- `test_worker_main_exits_3_on_psycopg_import_error`.
- `test_worker_main_exits_4_on_psycopg_query_error`.

The existing `TestReadGraphFromDbTimeouts` class remains unchanged — it tests the inner function directly with stubs, and `_read_graph_from_db` still runs in-process under those tests. The new outer wrapper is tested separately.

### 5. First-exercise readiness note per ADR 0053

Cross-cutting mechanism. Trigger evaluation:

- ❌ Criterion 1 — new session mode. No.
- ❌ Criterion 2 — new validator soft-warn category. No (new failure modes within existing `graph_audit` hard-fail category).
- ❌ Criterion 3 — new state the boot procedure reads. No.
- ✅ Criterion 4 — Consequences span ≥3 ops docs OR ≥5 tooling files. **Yes** — `engine/tools/validate.py` (modified), `engine/tools/graph_audit_worker.py` (new), `engine/tools/test_validate.py` (extended), `engine/tools/test_graph_audit_worker.py` (new), this ADR, plus the first-exercise readiness note = 6 surfaces.

One criterion satisfied. First-exercise readiness note authored at [`engine/build_readiness/graph_audit_subprocess_first_exercise.md`](../build_readiness/graph_audit_subprocess_first_exercise.md). T1-A closes when a real wedge occurs in production and the parent SIGKILL-on-timeout path is empirically exercised; the bug is intermittent so closure may take ≥1 session. Until T1-A closes, the path is documented and tested but not field-validated.

## Consequences

### Positive

- **Issue #151 closes structurally.** Recurrences become operationally invisible: a wedge inside the worker fires the outer timeout, the worker is killed, the parent records a hard-fail, the pre-commit run exits non-zero, the user re-tries (or the underlying pooler issue resolves and the next try succeeds). No more 5-15 minute hangs; no more Supabase restart as recovery; subsequent commits in the same session are unblocked.
- **Acceptance criterion #4 retired as obsolete.** "5 consecutive build sessions without a hang recurrence" measured the *bug*. The bug may persist; the *blocker* it produced will not. The new closure criterion: subprocess gate verified in production once.
- **The `conn.cancel()` failure mode is bounded by the OS.** No further engineering effort needs to be spent on libpq-internal escape hatches.
- **The pattern generalizes to `apply_migration.py`.** If migration apply ever wedges in the same shape, the subprocess pattern is now a known answer.

### Negative / cost

- **Process startup cost on every graph_audit run.** ~500ms cold-start (interpreter + psycopg import + module load) on the venv per ADR 0050. Acceptable: graph_audit fires on commits that touch graph paths (per Issue #142 path-aware skip), not on every commit.
- **JSON-over-stdout has size limits in practice.** Python's `subprocess.run(capture_output=True)` reads the full stdout into memory. Current corpus serializes to ~700KB; comfortably within memory. Phase 6 will grow this; a future seed past ~50MB would need streaming, but that's a Phase-6-far-out concern, not a today concern.
- **A test architecture split.** Inner-function tests stay where they are; outer-wrapper tests live in a new class. Some readers will need to follow two test paths to understand the full coverage.
- **The in-process watchdog is now inner defense, not load-bearing primary defense.** S-0187's documentation comment in `_read_graph_from_db` will keep describing it as "client-side wall-clock cap" — accurate but mode-shifted. The accurate framing is in this ADR; the function's docstring should reference back here.

### Out-of-scope (deliberately not changing)

- **Supavisor session mode (Option B from the user-adjudication menu).** Switching `SUPABASE_DB_URL` from transaction-pool to session-mode pooler is a deployment-side config change that may or may not address the underlying pgbouncer L4-traffic hypothesis (lesson drawer `c8f90de5`). It remains available as a follow-up if the wedge's *frequency* rather than *blocking nature* becomes the operational concern. The subprocess gate makes Option B optional; not adopting today.
- **Direct DB port 5432 (Option A).** Same reasoning — it requires Supabase IPv6 or paid IPv4 add-on, and the operational pressure for it disappears once the wedge is non-blocking.
- **Migration of `apply_migration.py` to the same subprocess pattern.** Migrations have never wedged in the wild. Authoring the pattern speculatively before evidence of need would violate the no-pilot-wait-and-see discipline; the pattern is documented in this ADR and trivially portable when a real wedge surfaces.
- **Removing the inner watchdog.** Defense-in-depth is cheap (~40 LOC) and means healthy-but-slow queries get a clean QueryCanceled exception instead of a SIGKILL. Removal would lose that signal-quality distinction.

## Alternatives Considered

(Per [ADR 0077](0077-adr-template-alternatives-considered-section.md).)

**Alternative 1 — Supavisor session mode (URL switch, no code).** Lower complexity, fixes the suspected root cause directly. Rejected because: it addresses one hypothesis (the L4-traffic behavior of transaction-pool mode); the wedge may have other causes; the subprocess gate is hypothesis-agnostic. If wedge frequency becomes a separate concern from blocking severity, Supavisor switch becomes the natural follow-up. Adopted neither today.

**Alternative 2 — Direct DB port 5432.** Bypasses the pooler entirely. Rejected because: Supabase direct port requires IPv6 (or paid IPv4 add-on); adds environment-fragility to the validator gate; tries to avoid the pooler rather than survive it; the subprocess pattern survives any future pooler issue.

**Alternative 3 — Async psycopg with `asyncio.wait_for` outer timeout.** Same outer-cap idea but in-process. Rejected because: `asyncio.wait_for` cancels the awaitable's coroutine, not the underlying OS-level libpq syscall — the wedged socket survives the cancel just like `conn.cancel()` does. No real escape; same S-0211 failure mode at a different syntax.

**Alternative 4 — `multiprocessing` instead of `subprocess`.** Same process-boundary, more Python-native API. Rejected because: `multiprocessing` shares the parent's import graph at spawn time (cost), uses pickle for IPC (more failure modes than JSON-over-stdout), and the parent's `Process.kill()` plus `join(timeout=)` is more error-prone than `subprocess.run(..., timeout=)`. `subprocess` is the leaner primitive for this case.

**Alternative 5 — In-process watchdog calls `os._exit()` after `conn.cancel()` to force-exit the parent.** Considered briefly. Rejected because: it leaves the parent's caller (pre-commit hook) in a confused state with no return code semantics; the subprocess pattern preserves clean parent control flow.

## See also

- [Issue #151](https://github.com/StarshipSuperjam/paideia/issues/151) — the recurring wedge this ADR closes structurally.
- [ADR 0084](0084-pushback-rule-extraction-step-for-high-stakes-decisions.md) — extraction step (criterion #4 fires).
- [ADR 0053](0053-mechanism-first-exercise-gate.md) — first-exercise readiness gate (criterion #4 fires).
- [ADR 0045](0045-shared-state-integrity-discipline.md) — `scrubbed_env()` (the subprocess inherits a scrubbed env).
- [ADR 0050](0050-project-venv-and-hook-path-wiring.md) — venv discipline (subprocess inherits PATH-prepended venv tools via the parent's scrub-time helper).
- [ADR 0054](0054-lifecycle-push-wrapping-against-default-branch-push-gate.md) — sibling subprocess-wrapping pattern (for git pushes, not psycopg).
- [ADR 0055](0055-apply-migration-wrapping-against-production-reads-gate.md) — sibling wrapper pattern that may adopt this approach if migration-apply ever wedges similarly.
- engine_memory pushback drawer `94e4ea6e` (S-0211) — hypothesis-agnostic-data-collection-beats-committed-hypothesis-testing.
- engine_memory lesson drawer `4e3c8296` (S-0211) — capture-before-cancel ordering; the empirical pin that establishes premise 1.
- engine_memory lesson drawer `c8f90de5` (S-0208) — TCP keepalive necessary-but-not-sufficient; pgbouncer L4-traffic hypothesis.
- `.engine_reports/hang-diagnostic-2026-05-19T183424.199794Z-41424.json` — the S-0211 PID 41424 dump that supplies the empirical evidence for premise 1.
