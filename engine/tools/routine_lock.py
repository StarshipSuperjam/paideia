"""Atomic-write lockfile for routine-mode session serialization.

Layer 1 contract per ADR 0082 (Issue #15 belt-and-suspenders).

Purpose
-------
Defense-in-depth for true concurrent routine fires. The primary fix
for Issue #15 is the boot-freshness gate
(:mod:`routine_boot_freshness`) — that addresses the actual S-0054
failure mode (boot-time staleness, not concurrency). The lockfile
prevents the *hypothetical* concurrent case: two cadence fires
happen close enough together that both pass freshness, both read
the same ``register_state.json``, both attempt to claim the same
slot, and the second push gets rejected.

Per the user's S-0055 in-session direction, the cost of the
loser-cleanup overhead (orphan branch + worktree) is non-trivial
enough to warrant the defense even though no concurrent fire has
actually been observed.

Mechanism
---------
At routine boot (``.claude/skills/routine-mode-lifecycle/SKILL.md``
step 0b), call ``routine_lock.py acquire``. Exit 0 means the lock
was acquired; the routine proceeds and releases at shutdown
(``routine_lock.py release`` — last action). Exit 1 means another
routine session is already in progress; the current session exits
cleanly without claiming.

The lock is an ``O_EXCL`` atomic write of a JSON blob containing
``{pid, started_at_iso}``. Stale-after timeout (default 1 hour,
covers worst-case session length) auto-evicts crashed-session
locks: if the lockfile exists and its mtime is older than the
threshold, ``acquire`` removes it and re-acquires (logging the
eviction to stderr).

Lock path defaults to ``.claude/routine.lock`` at the repo root
(must be gitignored — runtime artifact, never tracked).

CLI
---
- ``routine_lock.py acquire`` — acquire the lock. Exit 0 on success,
  exit 1 if held by another fresh process.
- ``routine_lock.py release`` — release the lock. Exit 0 always
  (idempotent; missing lockfile is fine).
- ``routine_lock.py check`` — inspection only. Exit 0 if held-fresh,
  exit 1 if not held, exit 2 if held-stale (would be evicted on
  next acquire).
- ``--lock-path PATH`` — override the lockfile location (test
  fixtures).
- ``--stale-after SECONDS`` — override the staleness threshold
  (default 3600 = 1 hour).

Out of scope
------------
- Cross-machine serialization. This is per-checkout lock state,
  not a distributed lock. Routine sessions all run in the same
  machine's worktree set; cross-machine concurrency would need
  the eager-claim "first push wins" property as the residual.
- Lock fairness. There is no queue. If two sessions race to
  acquire, exactly one wins; the other exits cleanly. No retry
  loop. The next cadence fire claims the lock fresh.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import emit  # noqa: E402  # ADR 0058

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK_PATH = REPO_ROOT / ".claude" / "routine.lock"
DEFAULT_STALE_AFTER = 3600  # 1 hour


def is_stale(lock_path: Path, stale_after: int) -> bool:
    """Return True if the lockfile exists and is older than stale_after seconds."""
    if not lock_path.exists():
        return False
    age = time.time() - lock_path.stat().st_mtime
    return age >= stale_after


def acquire(lock_path: Path, stale_after: int = DEFAULT_STALE_AFTER) -> bool:
    """Atomically acquire the lock. Returns True on success, False if held-fresh.

    If the lock exists but is stale, it is evicted (with a stderr note) and
    acquired fresh.
    """
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if is_stale(lock_path, stale_after):
        try:
            stale_age = int(time.time() - lock_path.stat().st_mtime)
            lock_path.unlink()
            print(
                f"[routine-lock] evicted stale lock at {lock_path} "
                f"(age {stale_age}s ≥ {stale_after}s threshold).",
                file=sys.stderr,
            )
        except FileNotFoundError:
            pass

    payload = json.dumps(
        {
            "pid": os.getpid(),
            "started_at": emit(),  # ADR 0058 canonical
        }
    )

    try:
        # O_EXCL: fail if file exists. Atomic create-or-fail.
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError:
        return False

    try:
        with os.fdopen(fd, "w") as f:
            f.write(payload)
    except Exception:
        # If write fails, clean up the partial lock so the next acquire can try
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        raise

    return True


def release(lock_path: Path) -> None:
    """Release the lock. Idempotent — no-op if the lockfile is missing."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def check(lock_path: Path, stale_after: int = DEFAULT_STALE_AFTER) -> int:
    """Inspect lock state. Returns: 0=held-fresh, 1=not-held, 2=held-stale."""
    if not lock_path.exists():
        return 1
    if is_stale(lock_path, stale_after):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry. See module docstring for exit-code semantics per command."""
    parser = argparse.ArgumentParser(
        description=(
            "Atomic-write lockfile for routine-mode session serialization. "
            "Defense-in-depth per ADR 0082."
        ),
    )
    parser.add_argument(
        "command", choices=["acquire", "release", "check"], help="Action to perform."
    )
    parser.add_argument(
        "--lock-path",
        type=Path,
        default=DEFAULT_LOCK_PATH,
        help=f"Lockfile location (default: {DEFAULT_LOCK_PATH}).",
    )
    parser.add_argument(
        "--stale-after",
        type=int,
        default=DEFAULT_STALE_AFTER,
        help=f"Stale-after threshold in seconds (default: {DEFAULT_STALE_AFTER}).",
    )
    args = parser.parse_args(argv)

    lock_path: Path = args.lock_path
    stale_after: int = args.stale_after

    if args.command == "acquire":
        if acquire(lock_path, stale_after):
            print(f"[routine-lock] acquired {lock_path}")
            return 0
        print(
            f"[routine-lock] {lock_path} is held by another fresh process; "
            "exiting cleanly without claiming.",
            file=sys.stderr,
        )
        return 1

    if args.command == "release":
        release(lock_path)
        print(f"[routine-lock] released {lock_path}")
        return 0

    # check
    state = check(lock_path, stale_after)
    if state == 0:
        print(f"[routine-lock] {lock_path} is held (fresh).")
    elif state == 1:
        print(f"[routine-lock] {lock_path} is not held.")
    else:
        print(
            f"[routine-lock] {lock_path} is held but STALE (would be "
            "evicted on next acquire)."
        )
    return state


if __name__ == "__main__":
    sys.exit(main())
