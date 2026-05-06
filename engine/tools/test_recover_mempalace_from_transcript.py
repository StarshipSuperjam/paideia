"""Tests for recover_mempalace_from_transcript.py — ADR 0056 Part B / S-0079.

Covers path resolution (suffix-match + full-encode fallback), transcript
window picking, prompt template generation, and progress file round-trip.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recover_mempalace_from_transcript import (  # noqa: E402
    build_recovery_prompt,
    encode_worktree_path,
    find_project_dir,
    pick_transcript,
    progress_load,
    progress_render,
    progress_write_entry,
    resolve_transcript,
)


def test_encode_worktree_path() -> None:
    assert (
        encode_worktree_path("/Users/shanekidd/Documents")
        == "-Users-shanekidd-Documents"
    )
    assert (
        encode_worktree_path("/Users/shanekidd/Documents/Claude_Files/Paideia")
        == "-Users-shanekidd-Documents-Claude-Files-Paideia"
    )
    assert (
        encode_worktree_path("/path/.claude/worktrees/foo-bar-12345")
        == "-path--claude-worktrees-foo-bar-12345"
    )


def test_find_project_dir_full_encode_match(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "-tmp-X-claude-worktrees-foo-bar").mkdir()
    found, reason = find_project_dir("/tmp/X/.claude/worktrees/foo-bar", projects)
    assert reason is None
    assert found is not None
    assert found.name == "-tmp-X-claude-worktrees-foo-bar"


def test_find_project_dir_suffix_match(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    # Encoded path that doesn't quite match what we'd derive (extra prefix).
    (projects / "encoded-from-elsewhere-foo-bar-12345").mkdir()
    found, reason = find_project_dir("/some/other/path/foo-bar-12345", projects)
    assert reason is None
    assert found is not None
    assert found.name.endswith("foo-bar-12345")


def test_find_project_dir_missing(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    found, reason = find_project_dir("/nonexistent/path/x", projects)
    assert found is None
    assert reason == "no_matching_project_dir"


def test_find_project_dir_ambiguous_suffix(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "first-foo").mkdir()
    (projects / "second-foo").mkdir()
    found, reason = find_project_dir("/x/y/foo", projects)
    assert found is None
    assert reason == "ambiguous_suffix_match:2"


def test_pick_transcript_single_file(tmp_path: Path) -> None:
    pdir = tmp_path / "pdir"
    pdir.mkdir()
    t = pdir / "abc.jsonl"
    t.write_text("{}\n")
    chosen, candidates, reason = pick_transcript(pdir, None, None)
    assert chosen == t
    assert candidates == [t]
    assert reason is None


def test_pick_transcript_window_pick(tmp_path: Path) -> None:
    pdir = tmp_path / "pdir"
    pdir.mkdir()
    a = pdir / "a.jsonl"
    b = pdir / "b.jsonl"
    a.write_text("{}\n" * 10)
    b.write_text("{}\n" * 100)
    now = time.time()
    import os

    os.utime(a, (now - 86400, now - 86400))
    os.utime(b, (now - 60, now - 60))
    started = datetime.now(timezone.utc).replace(microsecond=0)
    closed = started
    chosen, _, _ = pick_transcript(pdir, started, closed)
    assert chosen == b


def test_pick_transcript_falls_back_to_largest(tmp_path: Path) -> None:
    pdir = tmp_path / "pdir"
    pdir.mkdir()
    a = pdir / "a.jsonl"
    b = pdir / "b.jsonl"
    a.write_text("{}\n")
    b.write_text("{}\n" * 1000)
    chosen, _, reason = pick_transcript(pdir, None, None)
    # No window: returns largest only when >1 candidate via fallback.
    # When started_at/closed_at None we fall through to the multi-file fallback path.
    assert chosen == b
    assert reason == "fallback_largest_no_window_match"


def test_resolve_transcript_end_to_end(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    projects = tmp_path / "projects"
    pdir = projects / "-tmp-x-foo-bar"
    pdir.mkdir(parents=True)
    transcript = pdir / "abc.jsonl"
    transcript.write_text("{}\n")
    archive = archive_dir / "S-0067.json"
    archive.write_text(
        json.dumps(
            {
                "id": "S-0067",
                "started_at": "2026-05-04T20:00:00Z",
                "closed_at": "2026-05-04T20:30:00Z",
                "worktree": "/tmp/x/foo/bar",
            }
        )
    )
    res = resolve_transcript(archive, projects)
    assert res.session_id == 67
    assert res.transcript_path == transcript
    assert res.reason is None


def test_resolve_transcript_no_worktree_field_falls_back_to_default(
    tmp_path: Path,
) -> None:
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir()
    projects = tmp_path / "projects"
    projects.mkdir()
    archive = archive_dir / "S-0010.json"
    archive.write_text(json.dumps({"id": "S-0010"}))
    res = resolve_transcript(archive, projects)
    assert res.transcript_path is None
    assert res.reason == "no_matching_project_dir"


def test_build_recovery_prompt_dry_run(tmp_path: Path) -> None:
    archive = tmp_path / "S-0067.json"
    archive.write_text("{}")
    transcript = tmp_path / "x.jsonl"
    transcript.write_text("{}")
    p = build_recovery_prompt(archive, transcript, "S-0079", dry_run=True)
    assert "DRY-RUN" in p
    assert "S-0067" in p
    # Prompt must NOT instruct any S-NNNN-style attribution (impersonation
    # shape was rejected at S-0079; recovery is analytical-voice only).
    assert "S-0067-recovery-S-0079" not in p
    assert "S-NNNN-recovery" not in p
    # Dry-run JSON shape carries observation_diary, not a synthetic diary.
    assert "observation_diary" in p
    # Prompt must mark the analytical-voice framing.
    assert "analytical" in p.lower()


def test_build_recovery_prompt_write(tmp_path: Path) -> None:
    archive = tmp_path / "S-0067.json"
    archive.write_text("{}")
    transcript = tmp_path / "x.jsonl"
    transcript.write_text("{}")
    p = build_recovery_prompt(archive, transcript, "S-0079", dry_run=False)
    # Write mode points at MCP tools.
    assert "mempalace_add_drawer" in p
    assert "mempalace_diary_write" in p
    # No impersonation attribution: the recovery session is exploration mode,
    # not slot-claimed; added_by must be a non-S-NNNN form.
    assert "S-0067-recovery-S-0079" not in p
    assert "recovery-observer" in p
    # Drawer body framing must be analytical, not first-person.
    assert "Pattern observed in S-0067" in p
    # Default-mode framing must be explicit.
    assert "DEFAULT mode" in p or "default mode" in p
    assert "do NOT invoke /start-engine" in p
    assert "do NOT eager-claim" in p


def test_progress_round_trip(tmp_path: Path) -> None:
    progress = tmp_path / "progress.md"
    progress_write_entry(
        progress, "S-0067", "completed", summary="diary 1, pushback 2", reason=None
    )
    progress_write_entry(
        progress, "S-0073", "unrecoverable", summary=None, reason="empty_extraction"
    )
    loaded = progress_load(progress)
    assert "S-0067" in loaded
    assert loaded["S-0067"]["status"] == "completed"
    assert loaded["S-0067"]["summary"] == "diary 1, pushback 2"
    assert "S-0073" in loaded
    assert loaded["S-0073"]["status"] == "unrecoverable"
    assert loaded["S-0073"]["reason"] == "empty_extraction"
    rendered = progress_render(loaded)
    assert "S-0067" in rendered
    assert "completed=1 unrecoverable=1 total=2" in rendered
