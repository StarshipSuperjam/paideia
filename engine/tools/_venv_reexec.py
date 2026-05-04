"""Re-exec the current script under the project venv when needed.

Per Issue #14 (S-0055): routine sessions and bare ``python3 engine/tools/x.py``
invocations were resolving to system Python, which lacks ``psycopg``. The
DB-touching tools (:mod:`check_target`, :mod:`validate`, :mod:`setup_env`)
emitted misleading ``[FAIL] migration_applied — psycopg not available`` output
even when the migration was genuinely applied. The pre-commit hook scripts
already source :file:`scrub_env.sh` which prepends the venv to ``PATH``, but
direct invocations skip that hook.

This module's :func:`ensure_venv_python` runs at the top of each affected
tool. If the required module (default ``psycopg``) is not importable under
the current interpreter, it walks up from the script's directory to find a
``.venv/bin/python3`` (worktree-local first, then ascends to the main repo —
same precedence as :file:`scrub_env.sh`), and ``os.execv``'s the venv
interpreter. The tool transparently re-runs under the correct Python.

The module uses only stdlib so it can run under system Python before the
re-exec. It is intentionally minimal — no logging, no fancy heuristics, no
subprocess calls. The walk-up terminates at the filesystem root.

Idempotency: the venv-Python child won't re-exec a second time because
:data:`sys.executable` will match the resolved venv path on the next entry.
Best-effort: if no ``.venv/bin/python3`` is found anywhere on the walk-up,
the function returns silently and the caller's ``import psycopg`` fails with
the original :class:`ImportError`. That preserves the prior behavior for
genuinely-broken environments instead of masking the failure.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def ensure_venv_python(required_module: str = "psycopg") -> None:
    """Re-exec under the project venv if ``required_module`` isn't importable.

    No-op when:
      - ``required_module`` is already importable under the current interpreter
        (find_spec returns a non-None spec), OR
      - no ``.venv/bin/python3`` exists on the walk-up from this file's
        directory to the filesystem root.

    Otherwise replaces the current process with the venv interpreter via
    :func:`os.execv`. Does not return on a successful re-exec.
    """
    if importlib.util.find_spec(required_module) is not None:
        return
    here = Path(__file__).resolve().parent
    for candidate in (here, *here.parents):
        venv_python = candidate / ".venv" / "bin" / "python3"
        # is_file() follows symlinks, so a symlinked venv interpreter still matches.
        if venv_python.is_file():
            # Pass the symlink path as argv[0]: Python uses argv[0] to detect
            # the surrounding venv (looks for pyvenv.cfg in the parent dir).
            # Using the resolved interpreter path bypasses venv bootstrap and
            # site-packages would not be loaded.
            venv_python_str = str(venv_python)
            if sys.executable != venv_python_str:
                os.execv(venv_python_str, [venv_python_str, *sys.argv])
            return
