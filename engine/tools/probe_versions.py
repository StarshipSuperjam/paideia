"""Boot-time version telemetry — surfaces the active venv's Python +
chromadb + mempalace versions plus which venv resolver won.

Per ADR 0080 (engine), S-0147. Closes the visibility gap that drove the
S-0144→S-0146 MemPalace cold-start confusion arc: knowing "mempalace
3.3.5" vs "mempalace 3.3.3 from system Python" changes diagnosis
entirely. ADR 0050's PATH wiring is opaque without a visibility surface;
this probe gives the AI a fact-anchor at every boot.

Purpose
-------
Compare ``sys.prefix`` against the expected worktree-local and main-repo
``.venv/`` paths (per ADR 0050 PATH-resolution order in
``scrub_env.sh``). When the prefix matches one of those, the surface is
informational. When it matches neither, the surface emits a LOUD warning
that ``scrub_env.sh`` did not source successfully (system Python won
silently).

Shape
-----
``[session-start] Versions: python=3.12.13 chromadb=1.5.9 mempalace=3.3.5
venv=<path> (worktree-local|main-repo|MISCONFIGURED).``

CLI
---
- ``probe_versions.py`` — emit one-line surface to stdout.
- ``probe_versions.py --json`` — emit JSON of the resolved facts (test
  fixture support).
- ``probe_versions.py --repo PATH`` — pass-through; defaults to
  ``git rev-parse --show-toplevel``.

Exit codes
----------
- ``0`` — probe succeeded (regardless of whether deps are installed).
- ``2`` — repo discovery failed (no git, no ``--repo``).

The probe is intentionally non-blocking. A LOUD surface is informational
attention, not a hard fail — the hook still exits 0 so the session can
boot and the AI can investigate.

Out of scope
------------
- Does not install or repair the venv (that's the user's recovery step,
  via ``uv sync``).
- Does not query Dependabot PRs (see ``scan_dependabot_prs.py``).
- Does not validate floor-pin freshness (see
  ``validate_uv_lock_freshness`` in ``validate.py``).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _safe_import_version(module_name: str) -> str:
    """Return ``module.__version__`` or ``'not-installed'`` on ImportError."""
    try:
        mod = __import__(module_name)
    except ImportError:
        return "not-installed"
    return str(getattr(mod, "__version__", "unknown"))


def _resolve_main_repo(repo: str) -> str | None:
    """Return the main-repo root, or ``None`` when git discovery fails.

    Uses ``git rev-parse --git-common-dir`` — when ``repo`` is a worktree,
    this returns the parent ``.git`` directory; otherwise it returns
    ``.git`` (or the absolute path). The main-repo root is the parent of
    that ``.git`` directory.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", repo, "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    common_dir = proc.stdout.strip()
    # `--git-common-dir` may return relative; resolve against repo.
    candidate = (Path(repo) / common_dir).resolve()
    # The main-repo root is the parent of the .git directory.
    return str(candidate.parent)


def classify_venv(prefix: str, repo: str) -> tuple[str, str]:
    """Return (label, location_descriptor).

    Compares ``prefix`` against the expected worktree-local
    (``<repo>/.venv``) and main-repo (``<main_repo>/.venv``) paths.
    Returns one of three labels: ``worktree-local``, ``main-repo``,
    ``MISCONFIGURED``.
    """
    real_prefix = str(Path(prefix).resolve())

    expected_worktree = str((Path(repo) / ".venv").resolve())
    if real_prefix == expected_worktree:
        return ("worktree-local", expected_worktree)

    main_repo = _resolve_main_repo(repo)
    if main_repo is not None:
        expected_main = str((Path(main_repo) / ".venv").resolve())
        if real_prefix == expected_main:
            return ("main-repo", expected_main)

    return ("MISCONFIGURED", real_prefix)


def gather(repo: str) -> dict[str, Any]:
    """Return the resolved facts dict.

    Pure: takes a repo path, queries ``sys`` and imports, computes
    classification.
    """
    python_version = sys.version.split()[0]
    chromadb_version = _safe_import_version("chromadb")
    mempalace_version = _safe_import_version("mempalace")
    label, venv_path = classify_venv(sys.prefix, repo)
    return {
        "python": python_version,
        "chromadb": chromadb_version,
        "mempalace": mempalace_version,
        "venv": venv_path,
        "label": label,
    }


def format_line(facts: dict[str, Any]) -> str:
    """Format the facts dict into the one-line boot surface."""
    label = facts["label"]
    if label == "MISCONFIGURED":
        venv_part = (
            f"venv={facts['venv']} "
            "(LIKELY MISCONFIGURED — scrub_env.sh did not source; "
            "system Python won)"
        )
    else:
        venv_part = f"venv={facts['venv']} ({label})"
    return (
        f"[session-start] Versions: python={facts['python']} "
        f"chromadb={facts['chromadb']} mempalace={facts['mempalace']} "
        f"{venv_part}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Boot-time version telemetry per ADR 0080 (engine). "
            "Surfaces active Python + chromadb + mempalace versions and "
            "which venv resolver won."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON of resolved facts (test fixture support).",
    )
    parser.add_argument(
        "--repo",
        help=("Repo path; defaults to `git rev-parse --show-toplevel` or os.getcwd()."),
    )
    args = parser.parse_args(argv)

    repo = args.repo
    if repo is None:
        try:
            proc = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode == 0:
                repo = proc.stdout.strip()
        except FileNotFoundError:
            repo = None
    if not repo:
        repo = os.getcwd()

    facts = gather(repo)
    if args.json:
        json.dump(facts, sys.stdout)
        sys.stdout.write("\n")
    else:
        print(format_line(facts), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
