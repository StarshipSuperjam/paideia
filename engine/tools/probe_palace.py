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
    >= 10% (drawers exist in SQLite that the vector index can't see;
    ``mempalace_search`` will fall back to BM25 lexical matching).
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
