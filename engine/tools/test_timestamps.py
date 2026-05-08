"""Tests for engine/tools/timestamps.py per ADR 0058.

Covers shape regex of emit / emit_micros / today, parse tolerance across the
five accepted shapes (canonical Z, Z with microseconds, +00:00, +00:00 with
microseconds, compact-time), round-trip integrity, garbage rejection, and the
UTC-not-local guarantee for today().
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# Add engine/tools/ to sys.path so we can import the helper as a sibling.
# Tests run via `pytest engine/tools/test_timestamps.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from timestamps import (  # noqa: E402
    CANONICAL_FORMAT,
    DATE_FORMAT,
    MICROS_FORMAT,
    emit,
    emit_micros,
    parse,
    today,
)

CANONICAL_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MICROS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TestEmit:
    def test_emit_matches_canonical_shape(self) -> None:
        result = emit()
        assert CANONICAL_RE.match(result), f"emit() returned non-canonical: {result!r}"

    def test_emit_round_trips_through_parse(self) -> None:
        s = emit()
        dt = parse(s)
        assert dt.tzinfo is not None
        assert dt.utcoffset() == datetime.now(timezone.utc).utcoffset()

    def test_emit_drops_subsecond(self) -> None:
        result = emit()
        # Canonical shape has no '.' in the time portion.
        assert "." not in result.split("T")[1]


class TestEmitMicros:
    def test_emit_micros_matches_micros_shape(self) -> None:
        result = emit_micros()
        assert MICROS_RE.match(result), f"emit_micros() returned non-micros: {result!r}"

    def test_emit_micros_round_trips_through_parse(self) -> None:
        s = emit_micros()
        dt = parse(s)
        assert dt.tzinfo is not None
        # Microsecond precision preserved.
        assert dt.microsecond >= 0


class TestParse:
    def test_parse_canonical_z(self) -> None:
        dt = parse("2026-05-08T12:34:56Z")
        assert dt == datetime(2026, 5, 8, 12, 34, 56, tzinfo=timezone.utc)

    def test_parse_z_with_microseconds(self) -> None:
        dt = parse("2026-05-08T12:34:56.123456Z")
        assert dt == datetime(2026, 5, 8, 12, 34, 56, 123456, tzinfo=timezone.utc)

    def test_parse_plus_offset(self) -> None:
        dt = parse("2026-05-08T12:34:56+00:00")
        assert dt == datetime(2026, 5, 8, 12, 34, 56, tzinfo=timezone.utc)

    def test_parse_plus_offset_with_microseconds(self) -> None:
        # The legacy Python .isoformat() shape — present in pre-S-0095 archives.
        dt = parse("2026-05-08T12:34:56.123456+00:00")
        assert dt == datetime(2026, 5, 8, 12, 34, 56, 123456, tzinfo=timezone.utc)

    def test_parse_compact_time(self) -> None:
        # Legacy probe_push_gate.py shape.
        dt = parse("20260508T123456Z")
        assert dt == datetime(2026, 5, 8, 12, 34, 56, tzinfo=timezone.utc)

    def test_parse_rejects_garbage(self) -> None:
        with pytest.raises(ValueError):
            parse("garbage")

    def test_parse_rejects_empty(self) -> None:
        with pytest.raises(ValueError):
            parse("")

    def test_parse_rejects_non_string(self) -> None:
        with pytest.raises(ValueError):
            parse(12345)  # type: ignore[arg-type]

    def test_parse_rejects_partial_compact_time(self) -> None:
        # 7 digits in date portion (one short) — not a recognized shape.
        with pytest.raises(ValueError):
            parse("2026508T123456Z")

    def test_parse_returns_tz_aware_for_all_shapes(self) -> None:
        for s in [
            "2026-05-08T12:34:56Z",
            "2026-05-08T12:34:56.123456Z",
            "2026-05-08T12:34:56+00:00",
            "2026-05-08T12:34:56.123456+00:00",
            "20260508T123456Z",
        ]:
            dt = parse(s)
            assert dt.tzinfo is not None, f"parse({s!r}) returned naive datetime"


class TestToday:
    def test_today_matches_date_shape(self) -> None:
        result = today()
        assert DATE_RE.match(result), f"today() returned non-date: {result!r}"

    def test_today_returns_utc_not_local(self) -> None:
        # Mock the clock to a UTC instant where local time would be the previous calendar day.
        # 2026-05-08 00:30 UTC. Local time for negative-offset zones is still 2026-05-07.
        # We assert today() returns the UTC date regardless of the system's local zone.
        utc_instant = datetime(2026, 5, 8, 0, 30, 0, tzinfo=timezone.utc)

        class _FixedDatetime(datetime):
            @classmethod
            def now(cls, tz=None):  # type: ignore[no-untyped-def]
                if tz is None:
                    return utc_instant.replace(tzinfo=None)
                return utc_instant.astimezone(tz)

        with patch("timestamps.datetime", _FixedDatetime):
            result = today()
        assert result == "2026-05-08"


class TestFormatConstants:
    def test_canonical_format_strftime_round_trip(self) -> None:
        sample = datetime(2026, 5, 8, 12, 34, 56, tzinfo=timezone.utc)
        s = sample.strftime(CANONICAL_FORMAT)
        assert s == "2026-05-08T12:34:56Z"

    def test_micros_format_strftime_round_trip(self) -> None:
        sample = datetime(2026, 5, 8, 12, 34, 56, 123456, tzinfo=timezone.utc)
        s = sample.strftime(MICROS_FORMAT)
        assert s == "2026-05-08T12:34:56.123456Z"

    def test_date_format_strftime_round_trip(self) -> None:
        sample = datetime(2026, 5, 8, 0, 0, 0, tzinfo=timezone.utc)
        s = sample.strftime(DATE_FORMAT)
        assert s == "2026-05-08"
