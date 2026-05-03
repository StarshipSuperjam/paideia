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
