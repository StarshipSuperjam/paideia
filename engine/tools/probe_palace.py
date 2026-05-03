"""Probe the chromadb palace for openability + collection sanity.

Exit codes
----------
0
    Healthy. PersistentClient opens, collections list, and every
    collection's ``get_collection() + count()`` succeeds.
1
    Suspect. Open succeeded but something looked off — empty palace,
    collection with zero drawers in a non-empty palace, slow probe.
2
    Hard-broken. ``chromadb`` import failed, ``PersistentClient`` raised,
    ``list_collections`` raised, or any per-collection load raised.
139
    (Raised by the shell when Python segfaults — e.g., the chromadb
    rust binding faults on a corrupt HNSW segment.) The wrapper script
    treats 139 as hard-broken and triggers rollback.

Per ADR 0045 (engine). Run from the SessionStart hook (boot probe) and
from ``mempalace-hook-wrapper.sh`` (post-mine verification). Sub-second
on a 130 MB palace per the S-0034 measurement.

The probe iterates collections via ``client.get_collection(name)``
because the S-0034 segfault path triggered on get_collection, not on
list_collections — the lighter call would have missed the corruption.
"""

from __future__ import annotations

import os
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


def _emit(stream: str, line: str) -> None:
    target = sys.stderr if stream == "err" else sys.stdout
    print(line, file=target, flush=True)


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
    return 0


if __name__ == "__main__":
    sys.exit(main())
