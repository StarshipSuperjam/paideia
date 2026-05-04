"""Tests for engine/tools/scan_context_telemetry.py.

Covers the encoding helper, tokenizer fallback, write-to-current,
and the auto-detection path against synthetic transcripts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_context_telemetry import (  # noqa: E402
    _encoded_project_dir,
    find_transcript_for_repo,
    main,
    tokenize,
    write_telemetry_to_current,
)


# ---------------------------------------------------------------------------
# _encoded_project_dir
# ---------------------------------------------------------------------------


def test_encoded_dir_replaces_slashes_dots_underscores() -> None:
    """Every non-alphanumeric character becomes a dash."""
    p = Path("/Users/shanekidd/Documents/Claude_Files/Paideia/.claude/worktrees/foo")
    encoded = _encoded_project_dir(p)
    expected = "-Users-shanekidd-Documents-Claude-Files-Paideia--claude-worktrees-foo"
    assert encoded == expected


def test_encoded_dir_preserves_alphanumeric_and_dashes() -> None:
    p = Path("/repo-name-123")
    assert _encoded_project_dir(p) == "-repo-name-123"


# ---------------------------------------------------------------------------
# tokenize
# ---------------------------------------------------------------------------


def test_tokenize_empty_string() -> None:
    count, label = tokenize("")
    assert count == 0
    assert label in ("tiktoken-o200k_base", "chars-div-4-fallback")


def test_tokenize_returns_positive_for_nonempty() -> None:
    count, label = tokenize("hello world this is a test")
    assert count > 0
    assert label in ("tiktoken-o200k_base", "chars-div-4-fallback")


def test_tokenize_fallback_label_when_tiktoken_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Force the fallback path by simulating tiktoken ImportError."""
    import builtins
    from typing import Any

    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "tiktoken":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    text = "this is a test of the fallback tokenizer"
    count, label = tokenize(text)
    assert label == "chars-div-4-fallback"
    assert count == len(text) // 4


# ---------------------------------------------------------------------------
# find_transcript_for_repo
# ---------------------------------------------------------------------------


def test_find_transcript_returns_none_when_dir_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No project dir under ~/.claude/projects → None."""
    monkeypatch.setenv("HOME", str(tmp_path))
    result = find_transcript_for_repo(tmp_path / "fake-repo")
    assert result is None


def test_find_transcript_returns_most_recent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When multiple .jsonl files exist, the most recently modified wins."""
    monkeypatch.setenv("HOME", str(tmp_path))
    # Real path doesn't exist; we synthesize the encoded dir directly.
    fake_repo = Path("/synthetic/repo")
    project_dir = tmp_path / ".claude" / "projects" / _encoded_project_dir(fake_repo)
    project_dir.mkdir(parents=True)
    older = project_dir / "older.jsonl"
    newer = project_dir / "newer.jsonl"
    older.write_text("{}")
    newer.write_text("{}")
    # Stamp older's mtime in the past, newer's now.
    import os
    import time

    now = time.time()
    os.utime(older, (now - 100, now - 100))
    os.utime(newer, (now, now))

    result = find_transcript_for_repo(fake_repo)
    assert result == newer


# ---------------------------------------------------------------------------
# write_telemetry_to_current
# ---------------------------------------------------------------------------


def test_write_telemetry_adds_three_fields(tmp_path: Path) -> None:
    sess = tmp_path / "engine" / "session"
    sess.mkdir(parents=True)
    current = sess / "current.json"
    current.write_text(json.dumps({"id": "S-0042", "status": "in_progress"}))

    write_telemetry_to_current(tmp_path, 500_000, "tiktoken-o200k_base")

    data = json.loads(current.read_text())
    assert data["transcript_token_estimate"] == 500_000
    assert data["transcript_token_pct"] == 0.5
    assert data["tokenizer_used"] == "tiktoken-o200k_base"
    # Pre-existing fields preserved.
    assert data["id"] == "S-0042"
    assert data["status"] == "in_progress"


def test_write_telemetry_overwrites_existing_fields(tmp_path: Path) -> None:
    """Re-running with new values overwrites — idempotent on outputs."""
    sess = tmp_path / "engine" / "session"
    sess.mkdir(parents=True)
    current = sess / "current.json"
    current.write_text(
        json.dumps(
            {
                "transcript_token_estimate": 1000,
                "transcript_token_pct": 0.001,
                "tokenizer_used": "stale",
            }
        )
    )

    write_telemetry_to_current(tmp_path, 800_000, "chars-div-4-fallback")

    data = json.loads(current.read_text())
    assert data["transcript_token_estimate"] == 800_000
    assert data["transcript_token_pct"] == 0.8
    assert data["tokenizer_used"] == "chars-div-4-fallback"


def test_write_telemetry_raises_when_current_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        write_telemetry_to_current(tmp_path, 100, "stub")


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_dry_run_does_not_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--dry-run prints but does not modify current.json."""
    sess = tmp_path / "engine" / "session"
    sess.mkdir(parents=True)
    current = sess / "current.json"
    current.write_text(json.dumps({"id": "S-0042"}))

    transcript = tmp_path / "synthetic.jsonl"
    transcript.write_text("hello world hello world")

    rc = main(
        [
            "--repo-root",
            str(tmp_path),
            "--transcript",
            str(transcript),
            "--dry-run",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "tokens~" in out
    # current.json untouched.
    data = json.loads(current.read_text())
    assert "transcript_token_estimate" not in data


def test_main_writes_to_current(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sess = tmp_path / "engine" / "session"
    sess.mkdir(parents=True)
    current = sess / "current.json"
    current.write_text(json.dumps({"id": "S-0042"}))

    transcript = tmp_path / "synthetic.jsonl"
    transcript.write_text("a" * 4000)  # Predictable for char/4 fallback.

    rc = main(
        [
            "--repo-root",
            str(tmp_path),
            "--transcript",
            str(transcript),
        ]
    )
    assert rc == 0
    data = json.loads(current.read_text())
    assert data["transcript_token_estimate"] >= 1
    assert "transcript_token_pct" in data
    assert "tokenizer_used" in data


def test_main_handles_missing_transcript_gracefully(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No transcript found → stderr note, exit 0, no exception."""
    monkeypatch.setenv("HOME", str(tmp_path))
    rc = main(["--repo-root", str(tmp_path / "fake-repo")])
    assert rc == 0
    err = capsys.readouterr().err
    assert "no transcript found" in err


def test_main_handles_missing_current_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Transcript present, current.json absent → stderr note, exit 0."""
    transcript = tmp_path / "synthetic.jsonl"
    transcript.write_text("test")

    rc = main(
        [
            "--repo-root",
            str(tmp_path),
            "--transcript",
            str(transcript),
        ]
    )
    assert rc == 0
    err = capsys.readouterr().err
    assert "current.json not found" in err
