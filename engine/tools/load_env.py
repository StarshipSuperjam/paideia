"""Walk-up ``.env`` loader for engine tools.

Resolves the runtime gap surfaced by [Issue #8](https://github.com/StarshipSuperjam/paideia/issues/8):
worktrees do not have their own ``.env`` (the file is gitignored and
``git worktree add`` does not propagate it), and engine tools that read
``os.environ.get("SUPABASE_DB_URL")`` directly cannot see the value
unless a parent shell sourced it before launching the process.

Solution: walk up from the caller's CWD looking for the nearest
``.env``. From a worktree the chain is ``worktree-root → .claude/worktrees
→ .claude → main-repo-root``, where the main repo's ``.env`` lives —
found in three ancestor steps. From the main repo: found at the start.

Public API
----------

- :func:`find_dotenv` — locate the nearest ``.env`` walking up from a
  given start path (default ``Path.cwd()``).
- :func:`load_dotenv` — parse a ``.env`` file and apply its values to
  ``os.environ``. By default does NOT override pre-set keys, so an
  explicit ``SUPABASE_DB_URL=... python3 ...`` invocation still wins.
- :func:`load_dotenv_walk_up` — convenience wrapper. Calls
  :func:`find_dotenv` + :func:`load_dotenv`. Idempotent — re-running
  is safe.

Design choices
--------------

- **Hand-rolled parser**: reuses :func:`setup_env.parse_env` (~15 LOC).
  No new dependency on ``python-dotenv``.
- **Depth cap of 10 ancestors** prevents pathological loops if a caller
  starts inside a deeply-nested unrelated tree.
- **Filesystem-root halt**: walk stops when ``parent == self`` so we
  cannot escape onto a different mount or loop forever.
- **No file-system mutation**: the loader only reads.

Per Issue #8 (S-0049).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from setup_env import parse_env  # noqa: E402

DOTENV_BASENAME = ".env"
WALK_UP_DEPTH_CAP = 10


def find_dotenv(start: Path | None = None) -> Path | None:
    """Walk up from ``start`` (default ``Path.cwd()``) looking for ``.env``.

    Returns the first ``.env`` found on the way up, or ``None`` if no
    ``.env`` is reachable within :data:`WALK_UP_DEPTH_CAP` ancestor
    steps. Stops at filesystem root regardless of cap.
    """
    cur = (start or Path.cwd()).resolve()
    for _ in range(WALK_UP_DEPTH_CAP + 1):
        candidate = cur / DOTENV_BASENAME
        if candidate.is_file():
            return candidate
        parent = cur.parent
        if parent == cur:
            return None
        cur = parent
    return None


def load_dotenv(path: Path, *, override: bool = False) -> dict[str, str]:
    """Parse ``path`` and apply values to ``os.environ``.

    Parameters
    ----------
    path
        The ``.env`` file to read. Caller is responsible for existence
        (this raises :class:`FileNotFoundError` if absent — the
        :func:`load_dotenv_walk_up` wrapper handles the missing-file
        case gracefully).
    override
        When ``True``, overwrites any pre-existing value in
        ``os.environ`` for the same key. When ``False`` (default), keeps
        the pre-existing value — so an explicit ``KEY=value python3 ...``
        invocation still wins over the ``.env`` value.

    Returns
    -------
    dict[str, str]
        Map of keys actually applied to ``os.environ`` this call.
        Empty dict when every key was already set and ``override`` is
        ``False``.
    """
    parsed = parse_env(path.read_text())
    applied: dict[str, str] = {}
    for key, value in parsed.items():
        if not value:
            continue
        if not override and key in os.environ:
            continue
        os.environ[key] = value
        applied[key] = value
    return applied


def load_dotenv_walk_up(*, override: bool = False) -> dict[str, str]:
    """Locate the nearest ``.env`` and apply it to ``os.environ``.

    Idempotent. Returns an empty dict if no ``.env`` is reachable, or
    if every key it carries was already set in ``os.environ`` and
    ``override`` is ``False``.

    The intended call site is the top of an engine tool's ``main()``
    function, before any ``os.environ.get`` reads.
    """
    found = find_dotenv()
    if found is None:
        return {}
    return load_dotenv(found, override=override)


if __name__ == "__main__":
    # Diagnostic mode: report what would-load without committing the
    # mutation — useful for a fresh-clone sanity check.
    found = find_dotenv()
    if found is None:
        print("[load_env] no .env reachable from cwd")
        sys.exit(0)
    print(f"[load_env] found .env at: {found}")
    parsed = parse_env(found.read_text())
    populated = sorted(k for k, v in parsed.items() if v)
    print(f"[load_env] populated keys ({len(populated)}): {', '.join(populated)}")
