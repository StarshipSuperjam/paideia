"""Tests for engine/tools/probe_palace.py.

Covers the probe's behavior across healthy / suspect / hard-broken
exit codes by running it as a subprocess against synthetic palace
directories under tmp_path. Avoids touching the user's real palace
at ~/.mempalace/.

Test isolation strategy
-----------------------
- Each test sets HOME=tmp_path so the probe's PALACE_PATH expansion
  resolves to a tmp directory, not the real palace.
- The probe is run as a subprocess so its sys.path manipulation and
  module-level path constants are exercised the same way they would
  be at the SessionStart hook.

Non-responsibilities
--------------------
- Does not test chromadb internals — those are a third-party
  dependency. The healthy-case test creates a real chromadb palace
  under tmp_path because that's the cheapest way to verify the probe
  walks a working palace; if chromadb is unavailable, the test skips.
- Does not exercise the SIGSEGV (exit 139) path. Synthetic segfault
  is impractical from pytest; the wrapper-side handling is covered by
  inspecting the disposition logic in test_palace_atomic_wrapper.py.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROBE_PATH = Path(__file__).resolve().parent / "probe_palace.py"


def _run_probe(palace_dir: Path) -> subprocess.CompletedProcess[str]:
    """Run probe_palace.py against ``palace_dir`` via env-var override.

    Uses MEMPALACE_PROBE_PALACE_PATH (test-only override) instead of HOME
    redirection, because HOME redirection breaks chromadb's user-site
    sys.path discovery on macOS-bundled Python (`/usr/bin/python3`).
    """
    env = dict(os.environ)
    env["MEMPALACE_PROBE_PALACE_PATH"] = str(palace_dir)
    return subprocess.run(
        [sys.executable, str(PROBE_PATH)],
        capture_output=True,
        text=True,
        env=env,
    )


def test_probe_returns_suspect_when_palace_dir_missing(tmp_path: Path) -> None:
    """A nonexistent palace path yields exit 1 and a suspect message."""
    # Don't create the palace dir.
    proc = _run_probe(tmp_path / ".mempalace" / "palace")

    assert proc.returncode == 1
    assert "suspect" in proc.stderr
    assert "does not exist" in proc.stderr


def test_probe_returns_suspect_when_palace_has_no_collections(
    tmp_path: Path,
) -> None:
    """An empty palace dir (no chromadb state) yields exit 1 or 2.

    Without any chromadb files, ``PersistentClient(path=...)`` either
    creates a fresh empty palace (recent chromadb versions) or raises
    (older versions). Both outcomes are non-zero — the probe correctly
    flags an empty palace as suspect (1) and any open failure as
    hard-broken (2).
    """
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)

    proc = _run_probe(tmp_path / ".mempalace" / "palace")

    # Either suspect (1: empty/no collections) or hard-broken (2: open
    # failed) is acceptable for an empty dir; just not 0.
    assert proc.returncode in (1, 2)


def test_probe_healthy_on_real_chromadb_palace(tmp_path: Path) -> None:
    """A palace populated via chromadb yields exit 0."""
    chromadb = pytest.importorskip("chromadb")

    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)

    # Create a minimal palace with one collection and one drawer.
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("test_collection")
    col.add(ids=["d1"], documents=["hello world"])
    # Release any open handles before subprocess probe.
    del col
    del client

    proc = _run_probe(tmp_path / ".mempalace" / "palace")

    assert proc.returncode == 0
    assert "healthy" in proc.stdout
    assert "1 collections" in proc.stdout


def test_probe_emits_findings_on_stderr_not_stdout(tmp_path: Path) -> None:
    """Findings (suspect or hard-broken) emit to stderr, not stdout."""
    # Use the missing-palace case (suspect, exit 1).
    proc = _run_probe(tmp_path / ".mempalace" / "palace")

    assert proc.returncode == 1
    # The suspect message goes to stderr.
    assert "suspect" in proc.stderr
    # Stdout is empty (or at least doesn't carry the finding).
    assert "suspect" not in proc.stdout


# ---------------------------------------------------------------------------
# Divergence detection (S-0084 per ADR 0045 amendment, Issue #31)
# ---------------------------------------------------------------------------


def _write_stub_mempalace(
    bin_dir: Path,
    *,
    sqlite_count: int,
    hnsw_count: int,
    extra_invocation_log: Path | None = None,
    unflushed: bool = False,
) -> Path:
    """Create a fake ``mempalace`` script that mimics the upstream tool.

    The stub responds to ``mempalace --palace <X> repair-status`` with a
    minimal output shape matching the regexes in probe_palace.py. Any other
    subcommand exits 1 — particularly bare ``repair`` (without ``-status``)
    must NEVER be invoked by the probe; the caller can verify by reading
    the invocation log.

    When ``unflushed=True`` the stub emits the UNKNOWN / unflushed-metadata
    shape — ``hnsw count: (no flushed metadata yet)`` + ``status: UNKNOWN``
    — that the live palace produced for Issue #127. ``hnsw_count`` is
    ignored in that mode.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "mempalace"
    log_arg = f'\necho "$@" >> {extra_invocation_log}' if extra_invocation_log else ""
    if unflushed:
        drawers_block = """  [drawers]
    sqlite count:   %d
    hnsw count:     (no flushed metadata yet)
    status:         UNKNOWN
    note:           HNSW capacity unavailable: metadata has not been flushed""" % (
            sqlite_count,
        )
    else:
        drawers_block = """  [drawers]
    sqlite count:   %d
    hnsw count:     %d
    divergence:     %d
    status:         DIVERGED""" % (
            sqlite_count,
            hnsw_count,
            sqlite_count - hnsw_count,
        )
    stub.write_text(
        f"""#!/bin/bash{log_arg}
# Stub mempalace for probe_palace.py tests. Recognizes only repair-status.
# Form: mempalace --palace <X> repair-status
mode=""
for arg in "$@"; do
    if [ "$arg" = "repair-status" ]; then
        mode="repair-status"
    elif [ "$arg" = "repair" ]; then
        mode="repair"
    fi
done

if [ "$mode" = "repair-status" ]; then
    cat <<EOF
=======================================================
  MemPalace Repair — Status
=======================================================

  Palace: /tmp/test
{drawers_block}
EOF
    exit 0
elif [ "$mode" = "repair" ]; then
    # Should NEVER run from probe_palace.py — destructive.
    echo "ERROR: stub repair invoked (should not happen)" >&2
    exit 99
else
    echo "ERROR: stub doesn't recognize args: $@" >&2
    exit 1
fi
"""
    )
    stub.chmod(0o755)
    return stub


def _run_probe_with_stub(
    palace_dir: Path,
    stub_dir: Path,
    *,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run probe_palace.py with a stubbed mempalace binary on PATH."""
    env = dict(os.environ)
    env["MEMPALACE_PROBE_PALACE_PATH"] = str(palace_dir)
    env["PATH"] = f"{stub_dir}:{env.get('PATH', '')}"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(PROBE_PATH)],
        capture_output=True,
        text=True,
        env=env,
    )


def _make_minimal_palace(palace_dir: Path) -> None:
    """Build a minimal real chromadb palace under ``palace_dir``."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("test_collection")
    col.add(ids=["d1"], documents=["hello world"])
    del col
    del client


def test_probe_emits_divergence_line_when_repair_status_available(
    tmp_path: Path,
) -> None:
    """When mempalace is on PATH, probe emits the divergence stderr line."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    stub_dir = tmp_path / "bin"
    _write_stub_mempalace(stub_dir, sqlite_count=100, hnsw_count=98)

    proc = _run_probe_with_stub(palace_dir, stub_dir)

    # 2/100 divergence = 2.0% — below 10% threshold; probe still exit 0.
    assert proc.returncode == 0
    assert "divergence: HNSW=98 SQLite=100 (2.0%)" in proc.stderr


def test_probe_promotes_to_suspect_on_10pct_divergence(tmp_path: Path) -> None:
    """Divergence >= 10% promotes a healthy probe to exit 1 (suspect)."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    stub_dir = tmp_path / "bin"
    _write_stub_mempalace(stub_dir, sqlite_count=100, hnsw_count=80)

    proc = _run_probe_with_stub(palace_dir, stub_dir)

    # 20/100 divergence = 20% — above 10% threshold.
    assert proc.returncode == 1
    assert "divergence: HNSW=80 SQLite=100 (20.0%)" in proc.stderr
    # The healthy chromadb-layer line still appears on stdout.
    assert "healthy" in proc.stdout


def test_probe_handles_missing_mempalace_binary_gracefully(tmp_path: Path) -> None:
    """When mempalace isn't on PATH, probe exits 0 with no divergence line."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    # Empty bin dir (no mempalace stub) + minimal-PATH = FileNotFoundError.
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()

    proc = _run_probe_with_stub(palace_dir, stub_dir, extra_env={"PATH": str(stub_dir)})

    # No divergence available, but chromadb layer is healthy.
    assert proc.returncode == 0
    assert "divergence:" not in proc.stderr
    assert "healthy" in proc.stdout


def test_probe_emits_wing_count_line_on_healthy_palace(tmp_path: Path) -> None:
    """Probe emits the wing-count line when the chromadb sqlite holds wing metadata."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("mempalace_drawers")
    # Three distinct wings across five drawers.
    col.add(
        ids=[f"d{i}" for i in range(5)],
        documents=[f"doc {i}" for i in range(5)],
        metadatas=[
            {"wing": "paideia"},
            {"wing": "paideia"},
            {"wing": "wing_abc"},
            {"wing": "wing_def"},
            {"wing": "wing_def"},
        ],
    )
    del col
    del client

    proc = _run_probe(palace_dir)

    assert proc.returncode == 0
    assert "[probe-palace] wings: 3 (total)" in proc.stderr


def test_probe_emits_wing_count_zero_when_no_wing_metadata(tmp_path: Path) -> None:
    """Drawers without a `wing` metadata field yield a zero count, not a missing line."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection("mempalace_drawers")
    col.add(
        ids=["d0"],
        documents=["doc"],
        metadatas=[{"room": "general"}],  # no `wing` key
    )
    del col
    del client

    proc = _run_probe(palace_dir)

    assert proc.returncode == 0
    assert "[probe-palace] wings: 0 (total)" in proc.stderr


def test_probe_skips_wing_count_line_when_sqlite_absent(tmp_path: Path) -> None:
    """If chroma.sqlite3 is absent (legacy/empty palace), the wing-count line is silently skipped.

    The healthy line still emits if list_collections() succeeds. The wing-
    count surface is best-effort — its absence must never block the probe.
    """
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    # Don't init chromadb. The probe will try to open PersistentClient,
    # which on recent chromadb creates a fresh empty palace; the wing
    # query then runs but finds no matching rows (count = 0). The
    # negative-skip path is exercised by the absent-sqlite branch
    # explicitly; on a real fresh palace chromadb writes the file
    # before our query, so we test the absent-sqlite path via the
    # function directly instead of via subprocess.
    import importlib.util

    spec = importlib.util.spec_from_file_location("probe_palace", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module._count_wings(palace_dir) is None


def _load_probe_module() -> ModuleType:
    """Import probe_palace.py for direct function-level tests."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("probe_palace", PROBE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_count_quarantine_dirs_empty_palace_returns_zero(tmp_path: Path) -> None:
    """An empty palace directory carries zero quarantine dirs."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    module = _load_probe_module()
    assert module._count_quarantine_dirs(palace_dir) == (0, 0)


def test_count_quarantine_dirs_mixed(tmp_path: Path) -> None:
    """Mixed `.drift-*`, `.corrupt-*`, segment dirs, and files counted correctly."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    (palace_dir / ".drift-abc-001").mkdir()
    (palace_dir / ".drift-def-002").mkdir()
    (palace_dir / ".drift-ghi-003").mkdir()
    (palace_dir / ".corrupt-xyz-001").mkdir()
    (palace_dir / ".corrupt-uvw-002").mkdir()
    # Ordinary segment dir (UUID-like) — must not be counted.
    (palace_dir / "abcdef01-2345-6789-abcd-ef0123456789").mkdir()
    # chroma.sqlite3 placeholder — file, must not match drift/corrupt.
    (palace_dir / "chroma.sqlite3").write_bytes(b"")
    module = _load_probe_module()
    assert module._count_quarantine_dirs(palace_dir) == (3, 2)


def test_count_quarantine_dirs_only_drift(tmp_path: Path) -> None:
    """Drift-only state — typical never-flushed-metadata accumulation."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    for i in range(7):
        (palace_dir / f".drift-seg{i:03d}").mkdir()
    module = _load_probe_module()
    assert module._count_quarantine_dirs(palace_dir) == (7, 0)


def test_count_quarantine_dirs_only_corrupt(tmp_path: Path) -> None:
    """Corrupt-only state — harder-failure intercepts."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    for i in range(2):
        (palace_dir / f".corrupt-seg{i:03d}").mkdir()
    module = _load_probe_module()
    assert module._count_quarantine_dirs(palace_dir) == (0, 2)


def test_count_quarantine_dirs_palace_missing(tmp_path: Path) -> None:
    """Non-existent palace path returns None, not (0, 0)."""
    module = _load_probe_module()
    assert module._count_quarantine_dirs(tmp_path / "nonexistent") is None


def test_count_quarantine_dirs_ignores_matching_files(tmp_path: Path) -> None:
    """A FILE named `.drift-foo` is not a quarantine dir — must not be counted."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    (palace_dir / ".drift-foo").write_bytes(b"not a dir")
    (palace_dir / ".corrupt-bar").write_bytes(b"not a dir")
    module = _load_probe_module()
    assert module._count_quarantine_dirs(palace_dir) == (0, 0)


def test_probe_emits_quarantine_line_when_dirs_present(tmp_path: Path) -> None:
    """Full probe run emits the quarantine line on stderr when dirs are present."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    # Init chromadb so the probe reaches the post-wing emission block.
    client = chromadb.PersistentClient(path=str(palace_dir))
    client.get_or_create_collection("mempalace_drawers")
    del client
    # Seed two drift dirs + one corrupt dir.
    (palace_dir / ".drift-aaa-001").mkdir()
    (palace_dir / ".drift-bbb-002").mkdir()
    (palace_dir / ".corrupt-ccc-001").mkdir()

    proc = _run_probe(palace_dir)

    assert proc.returncode == 0
    assert "[probe-palace] quarantine: drift=2 corrupt=1" in proc.stderr


def test_probe_emits_quarantine_zero_on_healthy_palace(tmp_path: Path) -> None:
    """Healthy palace emits the quarantine line with both counts at zero.

    Always emitting (even at zero) lets validate.py's add_check be
    unconditional — the in-session checks_run array always records that
    the check ran, even when the soft-warn doesn't fire. Mirrors the
    wing-count contract.
    """
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    client.get_or_create_collection("mempalace_drawers")
    del client

    proc = _run_probe(palace_dir)

    assert proc.returncode == 0
    assert "[probe-palace] quarantine: drift=0 corrupt=0" in proc.stderr


def test_probe_never_invokes_mempalace_repair(tmp_path: Path) -> None:
    """Negative test: probe must never spawn `mempalace repair` (destructive).

    Per S-0078 forensic and ADR 0045 amendment (S-0084), the probe is
    detection-only. Verified by inspecting the stub's invocation log
    after a probe run.
    """
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    stub_dir = tmp_path / "bin"
    invocation_log = tmp_path / "stub-invocations.log"
    _write_stub_mempalace(
        stub_dir,
        sqlite_count=50000,
        hnsw_count=10,  # extreme divergence — probe must still not invoke repair
        extra_invocation_log=invocation_log,
    )

    proc = _run_probe_with_stub(palace_dir, stub_dir)

    assert proc.returncode == 1  # very-high divergence promotes to suspect
    assert invocation_log.exists()
    invocations = invocation_log.read_text().strip().splitlines()
    # Every stub invocation must include `repair-status`, never bare `repair`.
    for line in invocations:
        # Token-level check: split args; reject if "repair" appears without
        # being the literal string "repair-status".
        tokens = line.split()
        assert "repair" not in tokens, (
            f"probe spawned bare `repair` (destructive): {line!r}"
        )
        assert any("repair-status" in t for t in tokens), (
            f"probe stub invocation missing `repair-status`: {line!r}"
        )


# ---------------------------------------------------------------------------
# HNSW UNKNOWN / unflushed-metadata detection (S-0163 per Issue #127)
# ---------------------------------------------------------------------------


def test_probe_emits_hnsw_status_line_when_unflushed(tmp_path: Path) -> None:
    """An UNKNOWN / unflushed-metadata repair-status emits the hnsw-status line.

    The divergence counts are unparseable in that state (`hnsw count: (no
    flushed metadata yet)`), so the divergence line does NOT emit — the
    hnsw-status line is the only signal. Emit-only: no exit-code promotion.
    """
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    stub_dir = tmp_path / "bin"
    _write_stub_mempalace(stub_dir, sqlite_count=20261, hnsw_count=0, unflushed=True)

    proc = _run_probe_with_stub(palace_dir, stub_dir)

    assert proc.returncode == 0  # emit-only — no exit-code promotion
    assert "[probe-palace] hnsw-status: UNKNOWN" in proc.stderr
    assert "divergence:" not in proc.stderr  # counts unparseable → no line


def test_probe_no_hnsw_status_line_when_divergence_parseable(
    tmp_path: Path,
) -> None:
    """When the divergence counts parse, the hnsw-status line is NOT emitted.

    The two signals are mutually exclusive: divergence parses iff the HNSW
    count is a number, which means the index IS flushed (status not UNKNOWN).
    """
    palace_dir = tmp_path / ".mempalace" / "palace"
    _make_minimal_palace(palace_dir)
    stub_dir = tmp_path / "bin"
    _write_stub_mempalace(stub_dir, sqlite_count=100, hnsw_count=98)

    proc = _run_probe_with_stub(palace_dir, stub_dir)

    assert proc.returncode == 0
    assert "divergence: HNSW=98 SQLite=100 (2.0%)" in proc.stderr
    assert "hnsw-status:" not in proc.stderr


def test_parse_divergence_numeric_counts() -> None:
    """`_parse_divergence` returns the (sqlite, hnsw, pct) tuple for numbers."""
    module = _load_probe_module()
    output = "  [drawers]\n    sqlite count: 100\n    hnsw count: 80\n"
    assert module._parse_divergence(output) == (100, 80, 20.0)


def test_parse_divergence_unflushed_returns_none() -> None:
    """`_parse_divergence` returns None for the unflushed shape (no numbers)."""
    module = _load_probe_module()
    output = (
        "  [drawers]\n    sqlite count: 20261\n"
        "    hnsw count: (no flushed metadata yet)\n    status: UNKNOWN\n"
    )
    assert module._parse_divergence(output) is None


def test_parse_hnsw_status_unknown() -> None:
    """`_parse_hnsw_status` reads the [drawers] status token, upper-cased."""
    module = _load_probe_module()
    output = (
        "  [drawers]\n    sqlite count: 20261\n"
        "    hnsw count: (no flushed metadata yet)\n    status: UNKNOWN\n"
    )
    assert module._parse_hnsw_status(output) == "UNKNOWN"


def test_parse_hnsw_status_ok_and_absent() -> None:
    """`_parse_hnsw_status` returns the token for OK, None when absent."""
    module = _load_probe_module()
    assert module._parse_hnsw_status("  [drawers]\n    status: OK\n") == "OK"
    assert module._parse_hnsw_status("no drawers block here") is None


def test_run_repair_status_missing_binary_returns_none(tmp_path: Path) -> None:
    """`_run_repair_status` returns None when the mempalace binary is absent."""
    module = _load_probe_module()
    # A path that definitely has no `mempalace` resolvable — the function
    # catches FileNotFoundError and returns None.
    import os as _os

    old_path = _os.environ.get("PATH", "")
    try:
        _os.environ["PATH"] = str(tmp_path)  # empty dir, no mempalace
        assert module._run_repair_status(tmp_path / "palace") is None
    finally:
        _os.environ["PATH"] = old_path
