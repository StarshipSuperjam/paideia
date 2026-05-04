"""Tests for routine_lock.py — Issue #15 (S-0055)."""

from __future__ import annotations

import multiprocessing
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from routine_lock import acquire, check, main, release  # noqa: E402


def test_acquire_clean_succeeds(tmp_path: Path) -> None:
    """No prior lock → acquire succeeds, lockfile exists."""
    lock_path = tmp_path / "routine.lock"
    assert acquire(lock_path) is True
    assert lock_path.exists()


def test_acquire_when_fresh_lock_held_fails(tmp_path: Path) -> None:
    """Fresh lock present → second acquire returns False, file unchanged."""
    lock_path = tmp_path / "routine.lock"
    assert acquire(lock_path) is True
    mtime_before = lock_path.stat().st_mtime
    assert acquire(lock_path) is False
    assert lock_path.stat().st_mtime == mtime_before


def test_acquire_evicts_stale_and_succeeds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Stale lock present → second acquire evicts and succeeds."""
    lock_path = tmp_path / "routine.lock"
    assert acquire(lock_path) is True

    # Backdate the lockfile mtime to simulate a stale (>1h) lock
    old_time = time.time() - 7200  # 2 hours ago
    os.utime(lock_path, (old_time, old_time))

    assert acquire(lock_path, stale_after=3600) is True
    err = capsys.readouterr().err
    assert "evicted stale lock" in err


def test_release_idempotent(tmp_path: Path) -> None:
    """Release works on existing lock; second release no-ops."""
    lock_path = tmp_path / "routine.lock"
    assert acquire(lock_path) is True
    release(lock_path)
    assert not lock_path.exists()
    release(lock_path)  # idempotent — should not raise
    assert not lock_path.exists()


def test_check_states(tmp_path: Path) -> None:
    """check() returns 1 when not held, 0 when fresh, 2 when stale."""
    lock_path = tmp_path / "routine.lock"
    assert check(lock_path) == 1  # not held
    assert acquire(lock_path) is True
    assert check(lock_path) == 0  # held fresh
    old_time = time.time() - 7200
    os.utime(lock_path, (old_time, old_time))
    assert check(lock_path, stale_after=3600) == 2  # held stale


def _try_acquire_in_subprocess(lock_path_str: str, result_queue: object) -> None:
    """Helper: acquire in a subprocess and report success."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from routine_lock import acquire as sub_acquire

    success = sub_acquire(Path(lock_path_str))
    result_queue.put(success)  # type: ignore[attr-defined]


def test_concurrent_acquire_only_one_wins(tmp_path: Path) -> None:
    """Two concurrent acquire calls — exactly one succeeds."""
    lock_path = tmp_path / "routine.lock"

    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    p1 = ctx.Process(target=_try_acquire_in_subprocess, args=(str(lock_path), queue))
    p2 = ctx.Process(target=_try_acquire_in_subprocess, args=(str(lock_path), queue))
    p1.start()
    p2.start()
    p1.join(timeout=10)
    p2.join(timeout=10)

    results = [queue.get(timeout=1), queue.get(timeout=1)]
    assert sorted(results) == [False, True]


def test_main_acquire_returns_0_on_success(tmp_path: Path) -> None:
    """CLI: acquire returns 0 when successful."""
    lock_path = tmp_path / "routine.lock"
    rc = main(["acquire", "--lock-path", str(lock_path)])
    assert rc == 0
    assert lock_path.exists()


def test_main_acquire_returns_1_when_held(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI: acquire returns 1 when fresh lock held."""
    lock_path = tmp_path / "routine.lock"
    main(["acquire", "--lock-path", str(lock_path)])
    capsys.readouterr()  # clear
    rc = main(["acquire", "--lock-path", str(lock_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "held by another fresh process" in err


def test_main_release_always_returns_0(tmp_path: Path) -> None:
    """CLI: release returns 0 even when no lock exists."""
    lock_path = tmp_path / "routine.lock"
    rc = main(["release", "--lock-path", str(lock_path)])
    assert rc == 0
