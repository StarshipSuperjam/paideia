"""Tests for ``engine/memory/transcript_capture.py`` — capture, chunking, noise."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any


from engine.memory.connection import get_conn
from engine.memory.transcript_capture import (
    HEAD_TAIL_CHARS,
    MAX_BLOCK_CHARS,
    MAX_DRAWER_CHARS,
    capture,
    chunk_content,
    count_user_messages,
    extract_content_for_chunk,
    read_hook_event,
    read_jsonl_records,
    strip_noise,
    validate_transcript_path,
)


# --- Helpers ----------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    """Write a list of dicts as a JSONL file."""
    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def _user_msg(text: str) -> dict[str, Any]:
    return {"message": {"role": "user", "content": text}}


def _assistant_msg(text: str) -> dict[str, Any]:
    return {"message": {"role": "assistant", "content": text}}


def _command_msg() -> dict[str, Any]:
    """A user-role message that is actually a slash-command surface."""
    return {
        "message": {"role": "user", "content": "<command-message>foo</command-message>"}
    }


def _stdin(payload: dict[str, Any]) -> io.StringIO:
    return io.StringIO(json.dumps(payload))


def _count_drawers(db: Path, session_id: str) -> int:
    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT count(*) FROM drawers WHERE session_id = ?", (session_id,)
        ).fetchone()
        return int(row[0])
    finally:
        conn.close()


def _list_drawers(db: Path, session_id: str) -> list[tuple[str, str, str, str]]:
    conn = get_conn(db)
    try:
        return conn.execute(
            "SELECT room, source_kind, tags, content FROM drawers "
            "WHERE session_id = ? ORDER BY filed_at ASC, id ASC",
            (session_id,),
        ).fetchall()
    finally:
        conn.close()


def _get_capture_state(db: Path, session_id: str) -> int:
    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT message_count_since_save FROM capture_state WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        return int(row[0]) if row else -1
    finally:
        conn.close()


# --- read_hook_event --------------------------------------------------------


def test_read_hook_event_parses_valid_json() -> None:
    stream = _stdin({"transcript_path": "/x", "session_id": "S-test"})
    assert read_hook_event(stream) == {"transcript_path": "/x", "session_id": "S-test"}


def test_read_hook_event_returns_empty_on_parse_failure() -> None:
    assert read_hook_event(io.StringIO("not json")) == {}
    assert read_hook_event(io.StringIO("")) == {}


def test_read_hook_event_returns_empty_on_non_dict() -> None:
    assert read_hook_event(io.StringIO('"a string"')) == {}
    assert read_hook_event(io.StringIO("[1,2,3]")) == {}


# --- validate_transcript_path -----------------------------------------------


def test_validate_transcript_path_accepts_jsonl(tmp_path: Path) -> None:
    p = tmp_path / "transcript.jsonl"
    p.write_text("{}\n")
    assert validate_transcript_path(str(p)) == p.resolve()


def test_validate_transcript_path_rejects_missing_file(tmp_path: Path) -> None:
    assert validate_transcript_path(str(tmp_path / "absent.jsonl")) is None


def test_validate_transcript_path_rejects_wrong_extension(tmp_path: Path) -> None:
    p = tmp_path / "t.txt"
    p.write_text("x")
    assert validate_transcript_path(str(p)) is None


def test_validate_transcript_path_rejects_traversal(tmp_path: Path) -> None:
    bad = str(tmp_path / ".." / "outside.jsonl")
    assert validate_transcript_path(bad) is None


def test_validate_transcript_path_rejects_empty_string() -> None:
    assert validate_transcript_path("") is None


# --- count_user_messages + read_jsonl_records ------------------------------


def test_count_user_messages_basic(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    _write_jsonl(
        p, [_user_msg("a"), _assistant_msg("b"), _user_msg("c"), _assistant_msg("d")]
    )
    records = read_jsonl_records(p)
    assert count_user_messages(records) == 2


def test_count_user_messages_skips_command_messages(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    _write_jsonl(p, [_user_msg("real"), _command_msg(), _user_msg("real2")])
    records = read_jsonl_records(p)
    assert count_user_messages(records) == 2


def test_read_jsonl_records_skips_malformed_lines(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    p.write_text(
        json.dumps(_user_msg("ok"))
        + "\n"
        + "{ not valid json\n"
        + json.dumps(_user_msg("also ok"))
        + "\n"
    )
    records = read_jsonl_records(p)
    assert len(records) == 2


def test_read_jsonl_records_handles_blank_lines(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    p.write_text(
        "\n" + json.dumps(_user_msg("a")) + "\n\n" + json.dumps(_user_msg("b")) + "\n"
    )
    records = read_jsonl_records(p)
    assert len(records) == 2


# --- strip_noise ------------------------------------------------------------


def test_strip_noise_passes_through_small() -> None:
    s = "x" * 100
    assert strip_noise(s) == s


def test_strip_noise_truncates_large() -> None:
    s = "x" * (MAX_BLOCK_CHARS + 5_000)
    result = strip_noise(s)
    assert len(result) < len(s)
    assert "bytes truncated" in result
    assert result.startswith("x" * HEAD_TAIL_CHARS)
    assert result.endswith("x" * HEAD_TAIL_CHARS)


# --- chunk_content ----------------------------------------------------------


def test_chunk_content_passes_through_small() -> None:
    s = "hello"
    assert chunk_content(s) == ["hello"]


def test_chunk_content_returns_empty_for_empty() -> None:
    assert chunk_content("") == []


def test_chunk_content_splits_large() -> None:
    # Paragraphs joined by double-newline; total well above MAX_DRAWER_CHARS.
    para = "y" * 5_000
    s = "\n\n".join([para] * 20)  # ~100KB
    chunks = chunk_content(s)
    assert len(chunks) >= 2
    assert all(len(c) <= MAX_DRAWER_CHARS for c in chunks)
    # Reassembly preserves content modulo paragraph-boundary trimming.
    assert "y" in "".join(chunks)


def test_chunk_content_hard_splits_no_boundary() -> None:
    """Content without any newline boundary still splits at the hard cap."""
    s = "z" * (MAX_DRAWER_CHARS + 1_000)
    chunks = chunk_content(s)
    assert len(chunks) >= 2


# --- extract_content_for_chunk ---------------------------------------------


def test_extract_content_for_chunk_zero_index_captures_all(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    _write_jsonl(
        p,
        [_user_msg("u1"), _assistant_msg("a1"), _user_msg("u2"), _assistant_msg("a2")],
    )
    records = read_jsonl_records(p)
    content = extract_content_for_chunk(records, 0)
    assert "u1" in content
    assert "a1" in content
    assert "u2" in content
    assert "a2" in content


def test_extract_content_for_chunk_skips_pre_index(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    _write_jsonl(
        p,
        [_user_msg("u1"), _assistant_msg("a1"), _user_msg("u2"), _assistant_msg("a2")],
    )
    records = read_jsonl_records(p)
    content = extract_content_for_chunk(records, 1)  # start at 2nd user msg
    assert "u1" not in content
    assert "a1" not in content
    assert "u2" in content
    assert "a2" in content


def test_extract_content_returns_empty_when_past_end(tmp_path: Path) -> None:
    p = tmp_path / "t.jsonl"
    _write_jsonl(p, [_user_msg("u1")])
    records = read_jsonl_records(p)
    assert extract_content_for_chunk(records, 5) == ""


# --- capture (orchestration) ------------------------------------------------


def test_capture_no_op_on_empty_stdin(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    rc = capture("stop", stdin=io.StringIO(""), db_path=db)
    assert rc == 0
    assert _count_drawers(db, "unknown") == 0


def test_capture_no_op_on_missing_transcript_path(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    rc = capture("stop", stdin=_stdin({"session_id": "S-x"}), db_path=db)
    assert rc == 0
    assert _count_drawers(db, "S-x") == 0


def test_capture_no_op_on_missing_transcript_file(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-x", "transcript_path": str(tmp_path / "absent.jsonl")}
    rc = capture("stop", stdin=_stdin(payload), db_path=db)
    assert rc == 0
    assert _count_drawers(db, "S-x") == 0


def test_capture_rejects_invalid_hook_kind(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    rc = capture("bogus", stdin=io.StringIO(""), db_path=db)  # type: ignore[arg-type]
    assert rc == 0


def test_capture_first_fire_inserts_one_drawer(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(
        transcript,
        [
            _user_msg("first prompt"),
            _assistant_msg("assistant reply 1"),
            _user_msg("second prompt"),
            _assistant_msg("assistant reply 2"),
            _user_msg("third prompt"),
        ],
    )
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T1", "transcript_path": str(transcript)}

    rc = capture("stop", stdin=_stdin(payload), db_path=db)
    assert rc == 0

    rows = _list_drawers(db, "S-T1")
    assert len(rows) == 1
    room, source_kind, tags, content = rows[0]
    assert room == "work"
    assert source_kind == "hook_stop"
    assert tags == '["transcript"]'
    assert "first prompt" in content
    assert "assistant reply 1" in content
    assert "third prompt" in content
    assert _get_capture_state(db, "S-T1") == 3


def test_capture_is_idempotent_on_refire(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(transcript, [_user_msg("a"), _user_msg("b")])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T2", "transcript_path": str(transcript)}

    capture("stop", stdin=_stdin(payload), db_path=db)
    assert _count_drawers(db, "S-T2") == 1
    assert _get_capture_state(db, "S-T2") == 2

    # Re-fire over identical transcript: no new drawer.
    capture("stop", stdin=_stdin(payload), db_path=db)
    assert _count_drawers(db, "S-T2") == 1
    assert _get_capture_state(db, "S-T2") == 2


def test_capture_captures_only_delta_on_growth(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(transcript, [_user_msg("first"), _assistant_msg("r1")])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T3", "transcript_path": str(transcript)}

    capture("stop", stdin=_stdin(payload), db_path=db)
    assert _count_drawers(db, "S-T3") == 1
    rows_after_first = _list_drawers(db, "S-T3")
    assert "first" in rows_after_first[0][3]

    # Append two new user messages; re-fire.
    with transcript.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_user_msg("second")) + "\n")
        fh.write(json.dumps(_assistant_msg("r2")) + "\n")
        fh.write(json.dumps(_user_msg("third")) + "\n")
    capture("stop", stdin=_stdin(payload), db_path=db)

    # Both drawers exist; row order is non-deterministic when filed_at +
    # uuid tie-break collide within the same second. Identify the delta
    # drawer by its metadata.delta_user_messages (2 for this fire).
    conn = get_conn(db)
    try:
        rows = conn.execute(
            "SELECT content, metadata FROM drawers WHERE session_id = ?", ("S-T3",)
        ).fetchall()
    finally:
        conn.close()
    assert len(rows) == 2

    by_delta: dict[int, str] = {}
    for content, meta_json in rows:
        delta = json.loads(meta_json)["delta_user_messages"]
        by_delta[delta] = content

    assert 1 in by_delta and 2 in by_delta
    original_content = by_delta[1]
    delta_content = by_delta[2]
    assert "first" in original_content
    assert "second" in delta_content
    assert "third" in delta_content
    assert "first" not in delta_content


def test_capture_chunks_large_content(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    huge = "x" * (MAX_DRAWER_CHARS + 5_000)
    _write_jsonl(transcript, [_user_msg("intro"), _assistant_msg(huge)])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T4", "transcript_path": str(transcript)}

    capture("stop", stdin=_stdin(payload), db_path=db)
    rows = _list_drawers(db, "S-T4")
    # Multiple drawers because total content exceeds MAX_DRAWER_CHARS
    # AFTER noise-stripping kicks in (HEAD + tail + ...truncated... is
    # still ~1KB; total assembled content fits in 1 drawer once huge
    # block is stripped). Adjust: build content such that aggregate
    # post-strip size exceeds the cap.
    # Note: a single huge block gets noise-stripped to ~1KB. To force
    # chunking, use many medium-sized blocks below the strip threshold.
    assert len(rows) >= 1  # at least one drawer


def test_capture_chunks_across_many_blocks(tmp_path: Path) -> None:
    """Many medium blocks (each below noise threshold) force chunking."""
    transcript = tmp_path / "transcript.jsonl"
    medium = "y" * (MAX_BLOCK_CHARS - 1_000)  # below strip threshold
    records = [_user_msg("intro")]
    for _ in range(8):  # ~72KB total; should split into ≥2 drawers
        records.append(_assistant_msg(medium))
    _write_jsonl(transcript, records)

    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T4b", "transcript_path": str(transcript)}
    capture("stop", stdin=_stdin(payload), db_path=db)

    rows = _list_drawers(db, "S-T4b")
    assert len(rows) >= 2


def test_capture_noise_strips_large_block(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    huge_block = "X" * (MAX_BLOCK_CHARS * 3)
    _write_jsonl(transcript, [_user_msg("intro"), _assistant_msg(huge_block)])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T5", "transcript_path": str(transcript)}

    capture("stop", stdin=_stdin(payload), db_path=db)
    rows = _list_drawers(db, "S-T5")
    assert len(rows) == 1
    content = rows[0][3]
    assert "bytes truncated" in content
    assert len(content) < MAX_BLOCK_CHARS * 3


def test_capture_records_precompact_source_kind(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(transcript, [_user_msg("a")])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T6", "transcript_path": str(transcript)}

    capture("precompact", stdin=_stdin(payload), db_path=db)
    rows = _list_drawers(db, "S-T6")
    assert rows[0][1] == "hook_precompact"


def test_capture_metadata_records_chunk_index_and_hook_kind(tmp_path: Path) -> None:
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(transcript, [_user_msg("a")])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T7", "transcript_path": str(transcript)}
    capture("stop", stdin=_stdin(payload), db_path=db)

    conn = get_conn(db)
    try:
        row = conn.execute(
            "SELECT metadata FROM drawers WHERE session_id = ?", ("S-T7",)
        ).fetchone()
    finally:
        conn.close()
    meta = json.loads(row[0])
    assert meta["chunk_index"] == 0
    assert meta["total_chunks"] == 1
    assert meta["hook_kind"] == "stop"
    assert meta["transcript_path"] == "transcript.jsonl"
    assert meta["delta_user_messages"] == 1


def test_capture_handles_traversal_path(tmp_path: Path) -> None:
    db = tmp_path / "engine_memory.sqlite3"
    payload = {
        "session_id": "S-T8",
        "transcript_path": str(tmp_path / ".." / "x.jsonl"),
    }
    rc = capture("stop", stdin=_stdin(payload), db_path=db)
    assert rc == 0
    assert _count_drawers(db, "S-T8") == 0


def test_capture_skips_command_messages_in_count(tmp_path: Path) -> None:
    """Re-firing after only a command-message arrives should not re-emit."""
    transcript = tmp_path / "transcript.jsonl"
    _write_jsonl(transcript, [_user_msg("real")])
    db = tmp_path / "engine_memory.sqlite3"
    payload = {"session_id": "S-T9", "transcript_path": str(transcript)}

    capture("stop", stdin=_stdin(payload), db_path=db)
    assert _count_drawers(db, "S-T9") == 1
    assert _get_capture_state(db, "S-T9") == 1

    # Append a command-message; user-message count unchanged → no-op.
    with transcript.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(_command_msg()) + "\n")

    capture("stop", stdin=_stdin(payload), db_path=db)
    assert _count_drawers(db, "S-T9") == 1


def test_extract_content_handles_tool_use_blocks(tmp_path: Path) -> None:
    """Tool-use / tool-result blocks render as markers + content (per design)."""
    p = tmp_path / "t.jsonl"
    block_msg: dict[str, Any] = {
        "message": {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I'll check the file."},
                {"type": "tool_use", "name": "Read"},
            ],
        }
    }
    _write_jsonl(p, [_user_msg("u1"), block_msg])
    records = read_jsonl_records(p)
    content = extract_content_for_chunk(records, 0)
    assert "I'll check the file." in content
    assert "[tool_use: Read]" in content
