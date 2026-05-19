#!/usr/bin/env python3
"""Hypothesis-agnostic hang-diagnostic capture for validate.py's 45s watchdog.

Module contract.

Purpose
-------
Issue #151 (priority:urgent, bug): pre-commit invocations of
:mod:`engine.tools.validate`'s ``graph_audit`` phase hang intermittently
with an ESTABLISHED TCP socket to the Supabase pooler. The S-0208
mitigation (TCP keepalives on every ``psycopg.connect``) was empirically
falsified ~30 min after landing — the next wedge slipped past both the
45s wall-clock watchdog AND the ~60s keepalive detection window. Two
competing root-cause hypotheses are live and unresolved:

- **pgbouncer/Supavisor L4-traffic** (lesson drawer ``c8f90de5``).
  Transaction-pool mode keeps the socket L4-busy, so the kernel never
  marks it idle and TCP keepalive never fires.
- **Cross-process Python contamination** (user hypothesis, S-0211
  STATE.md row 54). Non-project Python tools leak state into the project
  venv's interpreter.

Every wedge to date has been reconstructed cold from ``ps`` evidence;
no ``strace`` / ``lsof`` / call-stack data has been captured at the
moment of hang. This module closes that gap. When the existing watchdog
in :func:`engine.tools.validate._read_graph_from_db` fires (queries
exceeded the wall-clock cap), it calls :func:`capture_hang_diagnostic`
BEFORE ``conn.cancel()``. The capture writes a structured JSON snapshot
to ``.engine_reports/hang-diagnostic-<iso-ts>-<pid>.json`` containing
the data each hypothesis predicts (sibling Python processes, open file
descriptors / sockets, thread call stacks, sample of ``sys.modules``,
psycopg version, env vars, macOS ``sample`` output). At the next
recurrence the snapshot pins which hypothesis is right.

Module invariants
-----------------
- **Best-effort.** Every subprocess call is wrapped in ``try/except``
  with a bounded timeout (≤5s). Missing fields drop to ``None`` rather
  than failing the dump. The watchdog's primary job (calling
  ``conn.cancel()``) must not be blocked by a capture failure.
- **Bounded.** Total capture time is bounded by the sum of per-call
  timeouts (~30s worst case). On a healthy system the capture completes
  in <2s. The macOS ``sample`` call uses ``-mayDie`` so it cannot block
  on a dead target.
- **Secret-scrubbing.** ``os.environ`` is included with keys matching
  ``KEY|SECRET|TOKEN|PASSWORD|URL`` redacted (case-insensitive). The
  ``SUPABASE_DB_URL`` env var carries credentials and must never land
  in a diagnostic file (gitignored or not).
- **No new dependencies.** Stdlib only. The module is imported on the
  pre-commit hot path; import cost must stay negligible.
- **Lazy directory creation.** ``.engine_reports/`` is created at first
  dump (already gitignored per ADR 0100). The module does not create
  the directory at import time.

Cross-references
----------------
- :mod:`engine.tools.validate` — caller; see ``_watchdog()`` at the
  ``_read_graph_from_db`` site for the integration point.
- ``.engine_reports/`` directory convention — established by S-0210
  (ADR 0100) for the hook-bypass audit trail. Same directory hosts
  hang diagnostics.
- ADR 0045 — subprocess environment scrubbing. The diagnostic capture
  does NOT scrub ``GIT_*`` env vars from its own subprocesses (it runs
  ``ps`` / ``lsof`` / ``netstat`` / ``pgrep`` / ``sample`` — none of
  which consult git context). Subprocess outputs land in the snapshot,
  not in git state.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from typing import Any

import timestamps

# Per-subprocess timeout. Five seconds is more than enough for ps,
# lsof, netstat, pgrep on a healthy macOS or Linux system; on a wedged
# system the cap prevents the diagnostic itself from extending the
# hang.
_SUBPROCESS_TIMEOUT_S = 5.0

# Sampling window for the macOS ``sample`` call-stack profiler. The
# tool needs at least 1s to produce a useful stack; 2s gives a clearer
# picture without significantly extending the capture. ``-mayDie``
# lets ``sample`` give up if the target dies during sampling.
_SAMPLE_DURATION_S = 2

# Secret-key substring patterns. ``os.environ`` keys containing any of
# these (case-insensitive) are redacted in ``env_scrubbed``. The
# project's ``SUPABASE_DB_URL`` env var carries credentials and is the
# load-bearing case; KEY/SECRET/TOKEN/PASSWORD are general-defense.
_SECRET_KEY_PATTERNS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "URL")

# Cap on ``sys.modules`` keys recorded. Sorted ASCII order; truncated
# to the first N. A full ``sys.modules`` dump can run to thousands of
# entries on a fully-loaded interpreter; the first 200 sorted is enough
# to spot a non-stdlib non-venv contaminant by alphabetic adjacency.
_SYS_MODULES_SAMPLE_CAP = 200

# Output directory. Lazily created. Already gitignored per S-0210
# (ADR 0100) — the .engine_reports/ entry was added at S-0210 for the
# hook-bypass audit trail; hang diagnostics live alongside.
_OUTPUT_DIR = Path(".engine_reports")


def _run_command(argv: list[str]) -> str | None:
    """Run ``argv`` with a bounded timeout; return stdout or ``None``.

    Returns ``None`` for any of: command-not-found (``FileNotFoundError``),
    nonzero exit (``CalledProcessError``-equivalent — but we use
    ``check=False`` and only return ``None`` when stdout is empty AND
    stderr indicates a real failure), timeout, or generic OS error.

    Captures stderr to the same buffer so a useful error message lands
    in the dump even when stdout is empty.
    """
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=_SUBPROCESS_TIMEOUT_S,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    except Exception:  # noqa: BLE001  # best-effort capture
        return None
    if proc.stdout:
        return proc.stdout
    # Some tools (netstat, pgrep) print zero output for empty result
    # sets without setting a nonzero exit. Treat empty-output + exit 0
    # as a valid empty result. Nonzero exit with stderr is a real
    # failure — record the stderr so the dump is still useful.
    if proc.returncode == 0:
        return ""
    return proc.stderr or None


def _scrub_env(env: dict[str, str]) -> dict[str, str]:
    """Return a copy of ``env`` with secret-bearing keys redacted.

    A key is considered secret-bearing if any of the patterns in
    :data:`_SECRET_KEY_PATTERNS` appear in the key name (case-
    insensitive). Redacted values become ``"<redacted>"``; the key
    itself remains visible so the absence-vs-presence-of-the-key
    signal is preserved (load-bearing for the cross-process
    contamination hypothesis — a leaked ``PYTHONPATH`` is informative
    even when its value happens to contain a secret-pattern token).
    """
    scrubbed: dict[str, str] = {}
    for key, value in env.items():
        upper = key.upper()
        if any(pattern in upper for pattern in _SECRET_KEY_PATTERNS):
            scrubbed[key] = "<redacted>"
        else:
            scrubbed[key] = value
    return scrubbed


def _thread_stacks() -> dict[str, list[str]]:
    """Return a snapshot of every live thread's call stack.

    Functional equivalent of ``strace`` for the hang case: pinpoints
    which Python frame each thread is parked in. The watchdog target
    (the main thread calling ``cur.execute()`` / ``cur.fetchall()``)
    will show its current frame in ``poll()`` or the psycopg C extension
    when the hang is the suspected idle-socket-poll(); a stack rooted
    in a non-project module would surface contamination at the
    interpreter level.
    """
    frames = sys._current_frames()
    out: dict[str, list[str]] = {}
    name_by_ident = {t.ident: t.name for t in threading.enumerate()}
    for ident, frame in frames.items():
        name = name_by_ident.get(ident, f"unknown-{ident}")
        # ``format_stack`` returns a list of formatted source lines;
        # rstrip each so the JSON dump stays readable.
        out[f"{name}-{ident}"] = [
            line.rstrip() for line in traceback.format_stack(frame)
        ]
    return out


def _psycopg_version() -> str | None:
    """Return the loaded psycopg version, or ``None`` if not loaded.

    Imported lazily and defensively — the project's validate.py keeps
    psycopg as an optional dependency, and the diagnostic must run
    even when psycopg is absent (e.g., reproducing the snapshot in an
    isolated-env probe).
    """
    try:
        import psycopg  # type: ignore[import-not-found,unused-ignore]
    except ImportError:
        return None
    except Exception:  # noqa: BLE001
        return None
    return getattr(psycopg, "__version__", None)


def capture_hang_diagnostic(label: str, pid: int | None = None) -> Path | None:
    """Capture a best-effort hang-diagnostic snapshot.

    Called from inside a watchdog when an external blocking call has
    exceeded its wall-clock cap. Writes a JSON file to
    ``.engine_reports/hang-diagnostic-<iso-ts>-<pid>.json`` and returns
    the path. Returns ``None`` if the capture itself fails catastrophically
    (e.g., the output directory cannot be created); the caller must
    treat ``None`` as "best-effort failed, proceed with whatever
    recovery action you were about to take anyway."

    Parameters
    ----------
    label
        Caller-supplied tag (e.g., ``"graph_audit_watchdog"``). Lands
        in the JSON's ``label`` field and identifies which call site
        produced this dump. Free-form; the diagnostic-reader uses it
        to filter when multiple dumps accumulate.
    pid
        Process ID to inspect. Defaults to the current process. The
        ``ps`` / ``lsof`` / ``sample`` calls target this pid; thread
        stacks always belong to the current process (cross-process
        stack capture requires gdb/lldb attach which is out of scope).
    """
    target_pid = pid if pid is not None else os.getpid()

    # Build the snapshot payload. Every field is optional in the sense
    # that a None value records "this probe failed or produced no
    # data"; the reader is expected to handle nulls.
    snapshot: dict[str, Any] = {
        "timestamp_utc": timestamps.emit_micros(),
        "label": label,
        "pid": target_pid,
        "ppid": os.getppid(),
        "platform": platform.system(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "psycopg_version": _psycopg_version(),
        "proc_self": _run_command(
            ["ps", "-p", str(target_pid), "-o", "pid,ppid,etime,stat,comm"]
        ),
        "python_procs": _run_command(["pgrep", "-fl", "python"]),
        "lsof_self": _run_command(["lsof", "-p", str(target_pid)]),
        "netstat_supabase": None,  # filled below; needs platform branch
        "python_modules_sample": sorted(sys.modules.keys())[:_SYS_MODULES_SAMPLE_CAP],
        "thread_stacks": _thread_stacks(),
        "env_scrubbed": _scrub_env(dict(os.environ)),
        "sample_stack": None,  # filled below; macOS-only
    }

    # netstat: on macOS the BSD netstat lacks the GNU -E regex flag,
    # so do the grep client-side. macOS netstat -an renders addresses
    # in dot-separated form (``192.168.1.5.51480``) while Linux netstat
    # uses colon (``192.168.1.5:51480``); accept both. Empirically
    # confirmed at S-0211 first-exercise (PID 41424 wedge dump) — the
    # initial colon-only grep produced empty output despite an
    # established TCP to ``ec2-...:postgresql`` per lsof.
    raw_netstat = _run_command(["netstat", "-an"])
    if raw_netstat is not None:
        snapshot["netstat_supabase"] = "\n".join(
            line
            for line in raw_netstat.splitlines()
            if any(token in line for token in (":5432", ":6543", ".5432", ".6543"))
        )

    # sample: macOS-only. Runs a 2s call-stack sample with -mayDie so
    # we don't wedge if the target dies during sampling. Equivalent
    # role to strace on Linux — the actual strace would require
    # special permissions and root on macOS, so sample is the
    # available equivalent. On Linux this field stays None and the
    # thread_stacks field carries the analogous data.
    if platform.system() == "Darwin":
        snapshot["sample_stack"] = _run_command(
            ["sample", str(target_pid), str(_SAMPLE_DURATION_S), "-mayDie"]
        )

    # Write to .engine_reports/. Lazy directory creation; absent
    # directory does not block other functionality. Any failure here
    # is unrecoverable for this capture — return None to signal best-
    # effort failure to the caller.
    try:
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        return None

    # Filename: ISO timestamp + pid. Colons in ISO timestamps are valid
    # on macOS but cause grief on Windows-shared filesystems; replace
    # to be portable. Pid suffix discriminates concurrent captures from
    # different processes hitting the watchdog simultaneously.
    safe_ts = snapshot["timestamp_utc"].replace(":", "")
    out_path = _OUTPUT_DIR / f"hang-diagnostic-{safe_ts}-{target_pid}.json"
    try:
        out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    except OSError:
        return None
    return out_path


if __name__ == "__main__":
    # CLI smoke-test entry: capture the current process's state to
    # .engine_reports/. Useful for verifying the capture works in a
    # given environment without triggering a real hang. Not intended
    # to be invoked from the pre-commit hook or any production path.
    result = capture_hang_diagnostic(label="cli_smoke_test")
    if result is None:
        print("capture_hang_diagnostic: capture failed", file=sys.stderr)
        sys.exit(2)
    print(f"capture_hang_diagnostic: wrote {result}")
