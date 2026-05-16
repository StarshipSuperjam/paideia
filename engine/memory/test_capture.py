"""Tests for ``engine/memory/capture.py`` — entrypoint dispatch."""

from __future__ import annotations

from typing import Any

import pytest

from engine.memory import capture as capture_mod
from engine.memory import transcript_capture


def test_main_dispatches_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def _fake_capture(hook_kind: str) -> int:
        seen["kind"] = hook_kind
        return 0

    monkeypatch.setattr(transcript_capture, "capture", _fake_capture)
    rc = capture_mod.main(["capture.py", "stop"])
    assert rc == 0
    assert seen["kind"] == "stop"


def test_main_dispatches_precompact(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def _fake_capture(hook_kind: str) -> int:
        seen["kind"] = hook_kind
        return 0

    monkeypatch.setattr(transcript_capture, "capture", _fake_capture)
    rc = capture_mod.main(["capture.py", "precompact"])
    assert rc == 0
    assert seen["kind"] == "precompact"


def test_main_defaults_to_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    """No argv[1] → default to 'stop'."""
    seen: dict[str, Any] = {}

    def _fake_capture(hook_kind: str) -> int:
        seen["kind"] = hook_kind
        return 0

    monkeypatch.setattr(transcript_capture, "capture", _fake_capture)
    rc = capture_mod.main(["capture.py"])
    assert rc == 0
    assert seen["kind"] == "stop"


def test_main_unknown_kind_no_ops(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unknown hook kind → exit 0 without calling capture()."""
    called = False

    def _fake_capture(hook_kind: str) -> int:
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr(transcript_capture, "capture", _fake_capture)
    rc = capture_mod.main(["capture.py", "bogus"])
    assert rc == 0
    assert not called


def test_main_uses_sys_argv_when_none(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, Any] = {}

    def _fake_capture(hook_kind: str) -> int:
        seen["kind"] = hook_kind
        return 0

    monkeypatch.setattr(transcript_capture, "capture", _fake_capture)
    monkeypatch.setattr("sys.argv", ["capture.py", "precompact"])
    rc = capture_mod.main()
    assert rc == 0
    assert seen["kind"] == "precompact"
