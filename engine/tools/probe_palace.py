"""Probe the chromadb palace for openability + collection sanity + HNSW divergence.

Exit codes
----------
0
    Healthy. PersistentClient opens, collections list, every
    collection's ``get_collection() + count()`` succeeds, AND HNSW
    divergence (if measurable) is below the 10% threshold.
1
    Suspect. Either the openability/sanity layer flagged something
    (empty palace, zero-drawer collection in non-empty palace, slow
    probe) OR the chromadb layer is fine but HNSW divergence is
    >= 10% (drawers exist in SQLite that the vector index can't see).
    A non-zero exit on the divergence path is a transient failure
    mode that requires action via
    ``engine/tools/mempalace_rebuild_hnsw.py`` (non-destructive
    direct chromadb rebuild on a scratch copy, then atomic-rename
    swap), not a working state to live with on BM25 fallback.
2
    Hard-broken. ``chromadb`` import failed, ``PersistentClient``
    raised, ``list_collections`` raised, or any per-collection load
    raised.
139
    (Raised by the shell when Python segfaults — e.g., the chromadb
    rust binding faults on a corrupt HNSW segment.) The wrapper
    script treats 139 as hard-broken and triggers rollback.

Per ADR 0045 (engine). Run from the SessionStart hook (boot probe)
and from ``mempalace-hook-wrapper.sh`` (post-mine verification).
Sub-second on a 130 MB palace per the S-0034 measurement; the
divergence step adds 5-15s on a ~450 MB palace (one
``mempalace repair-status`` subprocess that, per the upstream
``--help``, never opens a chromadb client but does open
``chroma.sqlite3`` for ground-truth counts).

The probe iterates collections via ``client.get_collection(name)``
because the S-0034 segfault path triggered on get_collection, not
on list_collections — the lighter call would have missed the
corruption.

Divergence detection is detection-only. The probe must not invoke
``mempalace repair`` in any form — S-0078 confirmed that command
destroys SQLite embedding rows under at least one failure shape
(99.7% loss; see engine/operations/mempalace-operations.md "Known
issues" and the upstream tracker filed at S-0084). The
``mempalace repair-status`` subcommand is read-only by upstream
contract and is the supported divergence query.
"""

from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import sys
import time
import warnings
from pathlib import Path

# urllib3 emits NotOpenSSLWarning to stderr at import on macOS's bundled
# LibreSSL Python. Suppressed so the boot-probe stderr surface stays
# quiet on healthy state — only real probe findings should reach the
# session-start hook's stderr.
warnings.filterwarnings("ignore", module="urllib3")


# Production: ~/.mempalace/palace. The MEMPALACE_PROBE_PALACE_PATH env
# var override exists for testing only — pytest can inject a tmp_path
# without resorting to HOME manipulation (which breaks chromadb's
# user-site sys.path discovery on macOS-bundled Python).
PALACE_PATH = Path(
    os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    or str(Path.home() / ".mempalace" / "palace")
)

# Threshold above which divergence promotes a healthy chromadb-layer
# probe (exit 0) to a suspect-level finding (exit 1). Mirrors the
# health-check.md "Maintenance probes" section threshold.
DIVERGENCE_PROMOTE_PCT = 10.0

# Regex for the [drawers] sqlite/hnsw counts in `mempalace repair-status`
# output. Tolerates comma-grouped numbers (e.g., "46,853") and arbitrary
# whitespace runs.
_REPAIR_STATUS_DRAWERS_RE = re.compile(
    r"\[drawers\][\s\S]*?sqlite\s+count:\s*([\d,]+)"
    r"[\s\S]*?hnsw\s+count:\s*([\d,]+)",
    re.IGNORECASE,
)


def _emit(stream: str, line: str) -> None:
    target = sys.stderr if stream == "err" else sys.stdout
    print(line, file=target, flush=True)


def _count_wings(palace_path: Path) -> int | None:
    """Count distinct ``wing`` metadata values via direct chromadb sqlite read.

    Returns the count, or ``None`` if the sqlite file is absent or the
    query fails. Read-only via the SQLite ``mode=ro`` URI form, so the
    open chromadb ``PersistentClient`` is not contended for write
    locks. Mirrors the upstream ``mempalace status`` enumeration (which
    parses the same metadata) without paying its 80+ s walk on a large
    palace — the SELECT runs in ~2 s on a 47 K-drawer palace per the
    S-0088 measurement, sub-second on smaller palaces.

    Failure is silent (returns ``None``) when:
    1. ``chroma.sqlite3`` is absent (palace dir exists but the chromadb
       layer never initialized — e.g., empty fresh palace).
    2. The ``embedding_metadata`` table is absent or its schema diverges
       from the chromadb version this probe was written against (the
       existing exit-code semantics still hold; the wing-count line just
       doesn't emit).
    """
    db_path = palace_path / "chroma.sqlite3"
    if not db_path.is_file():
        return None
    try:
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None
    try:
        cur = con.execute(
            "SELECT COUNT(DISTINCT string_value) FROM embedding_metadata "
            "WHERE key='wing'"
        )
        row = cur.fetchone()
    except sqlite3.Error:
        return None
    finally:
        con.close()
    if row is None:
        return None
    try:
        return int(row[0])
    except (TypeError, ValueError):
        return None


def _count_quarantine_dirs(palace_path: Path) -> tuple[int, int] | None:
    """Count ``.drift-*`` / ``.corrupt-*`` sibling dirs under the palace root.

    Returns ``(drift_count, corrupt_count)`` or ``None`` if the palace
    path doesn't exist. Both classes are placed by upstream
    ``quarantine_stale_hnsw`` (MemPalace/mempalace#1322 + #1342) when a
    backend client open sees a segment dir with absent
    ``index_metadata.pickle``: ``.drift-*`` for the never-flushed-metadata
    shape (PR #344 / Issue #1489), ``.corrupt-*`` for harder failure
    shapes the rename-aside intercepts before chromadb's native HNSW
    reader can fault on them. Each open replaces the bad segment with a
    fresh-empty placeholder; the next open sees the placeholder and
    quarantines it too, so the dirs compound silently across cold starts
    (the upstream MemPalace/mempalace#1489 comment thread records 9 dirs
    accumulated in one day on a 28K-drawer palace).

    Project-side relevance: ADR 0079's hybrid posture (live palace at
    threshold=100; bulk rebuilds keep mempalace's 50_000 anti-bloat
    default on scratch) reduces the rate at which the project palace
    can land in the never-flushed-metadata state, but the underlying
    quarantine mechanism runs on every backend client open regardless,
    so the surface is worth watching. Snapshot (not growth) — the
    measure is "how many dirs are accumulated right now"; the
    persistent-warn lifecycle (ADR 0042) handles cross-session signal.
    """
    if not palace_path.is_dir():
        return None
    drift = 0
    corrupt = 0
    for entry in palace_path.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith(".drift-"):
            drift += 1
        elif entry.name.startswith(".corrupt-"):
            corrupt += 1
    return (drift, corrupt)


def _check_divergence(palace_path: Path) -> tuple[int, int, float] | None:
    """Run ``mempalace repair-status --palace <path>`` and parse divergence.

    Returns ``(sqlite_count, hnsw_count, divergence_pct)`` for the drawers
    collection, or ``None`` if the upstream tool is unavailable or its
    output cannot be parsed. Read-only — the upstream subcommand is
    contracted to never open a chromadb client.

    Failure is silent (returns ``None``) for two cases:
    1. The ``mempalace`` binary isn't in PATH (legitimate on a fresh
       clone before the venv is wired; the probe should not hard-fail
       on a missing optional capability).
    2. The output shape is unrecognized (upstream may rev the format
       in a future version; the existing exit-code semantics still
       hold).
    """
    try:
        proc = subprocess.run(
            ["mempalace", "--palace", str(palace_path), "repair-status"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    except Exception:  # noqa: BLE001 — best-effort divergence check; never blocks
        return None

    output = proc.stdout + proc.stderr
    match = _REPAIR_STATUS_DRAWERS_RE.search(output)
    if not match:
        return None

    try:
        sqlite_count = int(match.group(1).replace(",", ""))
        hnsw_count = int(match.group(2).replace(",", ""))
    except ValueError:
        return None

    if sqlite_count <= 0:
        return (sqlite_count, hnsw_count, 0.0)

    pct = (sqlite_count - hnsw_count) / sqlite_count * 100.0
    return (sqlite_count, hnsw_count, pct)


def main() -> int:
    if not PALACE_PATH.exists():
        _emit(
            "err",
            f"[probe-palace] suspect: palace path {PALACE_PATH} does not exist",
        )
        return 1

    try:
        import chromadb  # noqa: PLC0415 — deferred import keeps probe importable
    except Exception as exc:
        _emit("err", f"[probe-palace] hard-broken: chromadb import failed: {exc}")
        return 2

    start = time.monotonic()
    try:
        client = chromadb.PersistentClient(path=str(PALACE_PATH))
    except Exception as exc:
        _emit("err", f"[probe-palace] hard-broken: PersistentClient open failed: {exc}")
        return 2

    try:
        collections_meta = client.list_collections()
    except Exception as exc:
        _emit("err", f"[probe-palace] hard-broken: list_collections failed: {exc}")
        return 2

    if not collections_meta:
        _emit("err", "[probe-palace] suspect: no collections in palace")
        return 1

    total = 0
    for col_meta in collections_meta:
        name = col_meta.name
        try:
            col = client.get_collection(name)
            n = col.count()
        except Exception as exc:
            _emit(
                "err",
                f"[probe-palace] hard-broken: get/count '{name}' raised: {exc}",
            )
            return 2
        total += n

    elapsed = time.monotonic() - start
    _emit(
        "out",
        f"[probe-palace] healthy: {len(collections_meta)} collections, "
        f"{total} drawers, {elapsed:.2f}s",
    )

    # Wing-count surface (per Issue #46, S-0088). MemPalace stores all
    # drawers in two chromadb collections (`mempalace_drawers` + a
    # closets collection) with `wing` carried as a metadata field, so
    # `len(collections_meta)` is always 2 — a meaningless wing
    # accumulation signal. Distinct wings via direct sqlite is the
    # accurate surface. Always emit on stderr when measurable so
    # validate.py can apply the configured thresholds.
    wing_count = _count_wings(PALACE_PATH)
    if wing_count is not None:
        _emit("err", f"[probe-palace] wings: {wing_count} (total)")

    # Quarantine accumulation surface (corroborating
    # MemPalace/mempalace#1489 Sarah Novotny comment, 2026-05-13).
    # Always emit on stderr when measurable so validate.py can apply the
    # configured threshold. Snapshot count (not growth); severity is
    # validate.py's call — this matches the wing-count pattern, not the
    # divergence pattern (no exit-code promotion from probe_palace
    # itself; the persistent-warn lifecycle per ADR 0042 handles
    # cross-session signal).
    quarantine = _count_quarantine_dirs(PALACE_PATH)
    if quarantine is not None:
        drift_count, corrupt_count = quarantine
        _emit(
            "err",
            f"[probe-palace] quarantine: drift={drift_count} corrupt={corrupt_count}",
        )

    # Divergence check: read-only via upstream `mempalace repair-status`.
    # Always emit on stderr when parseable so validate.py can promote
    # suspect-level severity. Best-effort — None means the tool wasn't
    # available or output didn't match the expected shape.
    divergence = _check_divergence(PALACE_PATH)
    if divergence is not None:
        sqlite_count, hnsw_count, pct = divergence
        _emit(
            "err",
            f"[probe-palace] divergence: HNSW={hnsw_count} "
            f"SQLite={sqlite_count} ({pct:.1f}%)",
        )
        if pct >= DIVERGENCE_PROMOTE_PCT:
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
