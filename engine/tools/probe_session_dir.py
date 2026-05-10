"""Probe the parent repo's engine/session/ directory for stray files.

Layer 1 contract per Issue #57.

Exit codes
----------
0
    Healthy. No stray files in ``engine/session/``.
1
    Soft-warn. One or more files matching the macOS Finder duplicate
    pattern (``^current [0-9]+\\.json$``) found. Recovery move is the
    user's call (typically ``mv "<path>" /tmp/<name>``); the file
    blocks ``routine_lifecycle_push.py eager-claim`` because the
    wrapper hard-checks for a clean working tree.
2
    Reserved. Currently no level-2 conditions; left for future
    catastrophic-corruption scenarios that warrant a hard-broken
    surface.

Per ADR 0045 (engine; shared-state integrity discipline). Run from
the SessionStart hook (boot probe) via ``validate.py
--health-probe-only`` alongside ``probe_palace.py`` and
``probe_repo.py``.

Motivating failure: S-0116 boot discovered ``engine/session/current
2.json`` — orphaned from S-0108 routine session — in the parent repo
working tree. The naming pattern (``current.json`` plus ``current
2.json`` with a literal leading space) is the canonical macOS Finder
/ iCloud-sync conflict pattern: when iCloud detects a conflict on a
file, Finder appends ``space + integer`` to the new copy. The stray
file blocked ``routine_lifecycle_push.py eager-claim`` (clean-tree
check); recovery was a manual ``mv`` to ``/tmp``. Without boot-time
detection, every recurrence requires the same manual triage.

Why scan the parent and not the worktree
----------------------------------------
The iCloud/Finder conflict appears in the parent repo (where iCloud
sync watches), not the linked worktree (which is a checkout pointer
with no separate ``.json`` files). The probe resolves the parent via
``git rev-parse --git-common-dir`` — the same pattern
``session-start.sh`` uses for the parent ``.env`` fallback per Issue
#50 / S-0099.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Local import — scrub_env lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scrub_env import scrubbed_env  # noqa: E402

# Canonical macOS Finder / iCloud-sync duplicate pattern: original name
# + literal space + integer + extension. The integer is typically 2 but
# can be any digit run if multiple conflicts accumulate.
STRAY_PATTERN = re.compile(r"^current \d+\.json$")


def _git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=scrubbed_env(),
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _emit(stream: str, line: str) -> None:
    target = sys.stderr if stream == "err" else sys.stdout
    print(line, file=target, flush=True)


def resolve_parent_session_dir(cwd: Path) -> Path | None:
    """Resolve the parent repo's ``engine/session/`` directory.

    Worktree-aware. From inside a linked worktree, ``git rev-parse
    --git-common-dir`` returns ``<parent>/.git``; the parent repo
    root is its parent directory. From a non-worktree session, the
    common-dir is ``<repo>/.git`` so the parent is ``<repo>`` —
    same path, no behavior change.

    Returns the resolved ``engine/session/`` path, or ``None`` if
    git fails, the layout is unexpected, or the directory is absent.
    """
    rc, common_dir_str, _err = _git(["rev-parse", "--git-common-dir"], cwd)
    if rc != 0 or not common_dir_str:
        return None
    common_dir = Path(common_dir_str)
    if not common_dir.is_absolute():
        common_dir = (cwd / common_dir).resolve()
    if common_dir.name != ".git":
        return None
    parent_repo = common_dir.parent
    session_dir = parent_repo / "engine" / "session"
    if not session_dir.is_dir():
        return None
    return session_dir


def find_stray_files(session_dir: Path) -> list[Path]:
    """Return paths of stray files matching ``STRAY_PATTERN``.

    Non-recursive — only direct children of ``session_dir``. The
    archive subdirectory is intentionally NOT scanned; the iCloud
    conflict pattern targets the live ``current.json`` slot, not
    archived files. The probe lists results in a deterministic order
    (sorted by name).
    """
    if not session_dir.is_dir():
        return []
    out: list[Path] = []
    for entry in session_dir.iterdir():
        if entry.is_file() and STRAY_PATTERN.match(entry.name):
            out.append(entry)
    out.sort(key=lambda p: p.name)
    return out


def main() -> int:
    cwd = Path.cwd()
    session_dir = resolve_parent_session_dir(cwd)
    if session_dir is None:
        # Best-effort: if we can't locate the parent's session dir
        # (not a git repo, common-dir resolution failed, dir absent),
        # treat as healthy. The session-start hook surface already
        # warns about repo-level health on its own.
        _emit("out", "[probe-session-dir] healthy: no parent session dir to scan")
        return 0

    strays = find_stray_files(session_dir)
    if not strays:
        _emit("out", f"[probe-session-dir] healthy: {session_dir} clean")
        return 0

    lines = ["[probe-session-dir] soft-warn: stray file(s) in engine/session/"]
    for path in strays:
        lines.append(f"  - {path}")
    lines.append(
        "  Likely macOS Finder / iCloud-sync duplicate pattern. "
        "These block routine_lifecycle_push.py eager-claim (clean-tree "
        "check). Recover with:"
    )
    for path in strays:
        # Quote the path for shell safety since the filename contains
        # a literal space.
        lines.append(f'  mv "{path}" /tmp/')
    lines.append("  See Issue #57 for context (engine/session/ pollution patterns).")
    _emit("err", "\n".join(lines))
    return 1


if __name__ == "__main__":
    sys.exit(main())
