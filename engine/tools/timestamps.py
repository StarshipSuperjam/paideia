"""Canonical timestamp emission and parsing for the engine apparatus.

Per ADR 0058. The single point of authority for timestamp shapes in
``engine/tools/**/*.py``. Emission tightens forward (new sites use
canonical second-precision Z-suffix); parsing stays tolerant of legacy
shapes indefinitely (one-way back-compat with archive canon per ADR 0042).

Operational discipline lives at ``engine/operations/timestamp-discipline.md``.
``engine/tools/validate.py``'s ``timestamp_helper_bypass`` AST-walk soft-warn
mechanically detects ad-hoc ``strftime`` / ``isoformat`` calls in tool sources
that should route through this module instead.

Out-of-scope:
- ``time.time()`` / ``time.monotonic()`` for stopwatch (duration) math.
- Hook scripts under ``engine/tools/hooks/*.sh``: they emit canonical second
  precision via ``date -u +"%Y-%m-%dT%H:%M:%SZ"``; the format is shared, the
  implementation is per-runtime.
- ``engine/tools/apply_migration.py:302``: the supabase migration-version
  format ``%Y%m%d%H%M%S`` is allowlisted as a legacy contract.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

CANONICAL_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MICROS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT = "%Y-%m-%d"
COMPACT_TIME_FORMAT = "%Y%m%dT%H%M%SZ"

_COMPACT_TIME_RE = re.compile(r"^\d{8}T\d{6}Z$")


def emit() -> str:
    """Return the canonical now-string in UTC second precision.

    Inputs: none.
    Outputs: a string matching ``%Y-%m-%dT%H:%M:%SZ`` (e.g.,
    ``2026-05-08T12:34:56Z``). Always second precision; sub-second resolution
    is dropped.
    Invariants: the returned string is parseable by ``parse()`` and
    round-trips through ``datetime.fromisoformat`` (Python 3.11+ accepts the
    Z suffix natively).
    Edge cases: none — the system clock is always available; UTC is
    timezone-stable. The function is impure (reads the wall clock).
    Non-responsibilities: callers needing microsecond precision call
    ``emit_micros()`` instead. Callers needing date-only output call
    ``today()``. Callers needing duration measurement use ``time.monotonic()``
    directly (this helper does not cover stopwatch math per ADR 0058 Non-goal).
    """
    return datetime.now(timezone.utc).strftime(CANONICAL_FORMAT)


def emit_micros() -> str:
    """Return the microsecond-precision now-string in UTC.

    Inputs: none.
    Outputs: a string matching ``%Y-%m-%dT%H:%M:%S.NNNNNNZ`` (e.g.,
    ``2026-05-08T12:34:56.123456Z``). Six-digit microsecond suffix.
    Invariants: the returned string is parseable by ``parse()``.
    Edge cases: none — the wall clock supplies microsecond resolution on all
    supported platforms.
    Non-responsibilities: this is the single legitimate caller-shape for
    ``validate.py``'s telemetry-history record where same-second event
    ordering matters. Other callers should use ``emit()`` (per ADR 0058
    Decision element 1, microsecond emission is admitted for one specific
    use case, not as a default).
    """
    return datetime.now(timezone.utc).strftime(MICROS_FORMAT)


def today() -> str:
    """Return the UTC date-only string ``%Y-%m-%d``.

    Inputs: none.
    Outputs: a string matching ``%Y-%m-%d`` (e.g., ``2026-05-08``).
    Invariants: returns the UTC calendar date, NOT the local-timezone date —
    the asymmetry matters when the local time zone is well past midnight UTC.
    Edge cases: at the UTC date boundary, two calls within a few microseconds
    of each other can return adjacent dates; that is correct behavior.
    Non-responsibilities: callers needing event-time semantics use ``emit()``.
    The distinction is intentional: callers of ``today()`` are display sites
    where the type-of-time is day-of-event and same-day re-runs should be
    diff-stable (audit-report headers, citation buckets).
    """
    return datetime.now(timezone.utc).strftime(DATE_FORMAT)


def parse(s: str) -> datetime:
    """Parse a stored timestamp string into a tz-aware UTC ``datetime``.

    Inputs:
        s: a timestamp string. Accepted shapes:
            - canonical second-precision Z suffix (``%Y-%m-%dT%H:%M:%SZ``)
            - microsecond-precision Z suffix (``%Y-%m-%dT%H:%M:%S.NNNNNNZ``)
            - second-precision ``+00:00`` offset (Python ``.isoformat()``
              shape, no microseconds)
            - microsecond-precision ``+00:00`` offset (Python ``.isoformat()``
              with default precision — the legacy archive shape)
            - compact-time ``%Y%m%dT%H%M%SZ`` (legacy ``probe_push_gate.py``
              shape; e.g., ``20260508T123456Z``)
        Precondition: ``s`` is a string. Empty / non-string / unrecognized
        shapes raise ``ValueError`` (NOT a custom subclass — call sites that
        catch ``ValueError`` to skip malformed records continue to work).
    Outputs: a tz-aware ``datetime`` in UTC.
    Invariants: parsing is loss-tolerant on shape but lossless on time —
    every accepted shape parses to the same UTC instant the caller wrote.
    Edge cases:
        - The compact-time form has no microsecond representation; assumed
          second precision.
        - ``parse(emit())`` round-trips at second precision.
        - ``parse(emit_micros())`` round-trips at microsecond precision.
    Non-responsibilities: this function does not write timestamps; emission
    is via ``emit()`` / ``emit_micros()`` / ``today()``. It does not parse
    date-only strings — ``today()``-shaped output ``%Y-%m-%d`` is a display
    surface, not an event-time string, and roundtripping it is out of scope
    for this helper.
    """
    if not isinstance(s, str):
        raise ValueError(f"parse() expected a string, got {type(s).__name__}")
    if _COMPACT_TIME_RE.match(s):
        return datetime.strptime(s, COMPACT_TIME_FORMAT).replace(tzinfo=timezone.utc)
    normalized = s.replace("Z", "+00:00") if s.endswith("Z") else s
    return datetime.fromisoformat(normalized)
