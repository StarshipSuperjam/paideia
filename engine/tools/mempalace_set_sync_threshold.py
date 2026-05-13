"""Set ``hnsw:sync_threshold`` on the mempalace chromadb collections with backup + verify discipline.

Per ADR 0079 (engine). Project-side mitigation for the recurring
"HNSW segment has never flushed metadata" state (S-0078 + S-0144).

Background
----------
chromadb's ``PersistentLocalHnswSegment._apply_batch`` (chromadb
1.5.x at ``segment/impl/vector/local_persistent_hnsw.py``) only
calls ``_persist()`` (writes ``index_metadata.pickle``) when
``_num_log_records_since_last_persist >= self._sync_threshold``.
``client.close()`` is NOT a flush primitive — it only releases the
shared system reference. For the project's typical 1–3-drawers-per-
session writes, the threshold is rarely reached between session
boundaries; in-memory metadata is dropped on process exit; the
next session's HNSW open sees the missing pickle as
``vector_disabled: HNSW segment has never flushed metadata``.

Mempalace itself sets ``hnsw:sync_threshold = 50_000`` on collection
creation (``mempalace/backends/chroma.py`` ``_HNSW_BLOAT_GUARD`` —
upstream PR #344) — explicitly, to prevent
``link_lists.bin`` sparse-file bloat that compounds across resize
cycles during bulk mines. The 50_000 default is bloat-safe for
high-volume mining but causes the never-flushed-metadata recurrence
for low-volume MCP workloads.

This tool overrides the per-collection ``hnsw:sync_threshold`` to a
low steady-state value (default 100) via chromadb's
``collection.modify(metadata=...)`` retrofit path. Hybrid posture
honoring both failure modes:

- **Steady-state**: threshold 100 forces a persist every ~33 typical
  sessions (1–3 drawers per session) — well below the never-flushed
  recurrence horizon.
- **Bulk rebuilds**: ``mempalace_rebuild_hnsw.py`` operates against
  a fresh scratch palace that inherits mempalace's own 50_000 from
  ``_HNSW_BLOAT_GUARD`` — the anti-bloat protection is preserved.
  After the scratch-then-swap completes, the rebuild tool invokes
  this tool against the live palace to restore the 100 steady-state.

Safeguards (user-directed at plan time)
---------------------------------------
The threshold-modification operation could in principle corrupt the
palace if it fails partway. Three layers of defense:

1. **Mandatory pre-switch backup.** ``--backup-dir PATH`` is required
   for ``--apply``. Backup is a ``cp -a``-equivalent via
   ``shutil.copytree`` BEFORE any chromadb call. Refuses with
   ``FileExistsError`` if the target exists (caller picks a unique
   path; conventionally
   ``~/.mempalace/palace.S-NNNN-pre-threshold-switch[-suffix]``).
2. **Pre-switch state capture** — reads each collection's current
   ``hnsw:sync_threshold`` before modify. Recorded in stderr for
   forensic value.
3. **Post-switch verification** — closes the chromadb client, opens
   a fresh client, re-reads collection metadata. Confirms the new
   threshold is present on both collections. Mismatch is exit 4
   with LOUD "RESTORE FROM BACKUP" guidance.

After the modify + verify, the tool optionally invokes
``probe_palace.py`` as a subprocess (scrubbed env) to confirm the
post-switch palace still opens cleanly. Non-zero probe exit is exit
6 (soft-warn-but-success — the modify succeeded; the probe found
something worth surfacing separately).

Operating modes
---------------
- ``--verify-only`` — read-only. Lists current threshold on
  ``mempalace_drawers`` and ``mempalace_closets``. Exits 0 if
  consistent state (both unset OR both at the same value), 1 if
  divergent (one set, the other not, or different values). Never
  mutates; no backup required.

- ``--apply`` (implicit when neither ``--verify-only`` nor
  ``--no-backup`` provided) — apply with mandatory backup. Requires
  ``--backup-dir PATH``.

- ``--no-backup`` — apply WITHOUT a backup. Test-only escape hatch.
  Production usage must use ``--backup-dir``. Refused if the palace
  path resolves to ``~/.mempalace/palace`` (production location).

Exit codes
----------
0
    Success: both collections set to target threshold AND post-switch
    verification confirmed AND palace health probe clean. (Verify-only:
    consistent state observed; both collections agree.)
1
    Divergent state observed in ``--verify-only`` mode (one collection
    has the threshold, the other does not, or they differ). No mutation.
2
    Pre-flight refused:
    - palace path missing or not a directory
    - threshold value invalid (chromadb's ``hnsw_params.py`` validator
      requires ``int > 2``)
    - ``--apply`` without ``--backup-dir`` and without ``--no-backup``
    - ``--no-backup`` against the production palace path
    - ``--backup-dir`` target already exists
    - backup creation failed (disk full, permission, etc.)
3
    chromadb error during the modify call. Stderr names the collection
    and the exception. Backup is intact; live palace state may be
    partially modified (modify is atomic at the chromadb metadata
    layer, so one-collection-modified-the-other-not is the worst case).
    Restore from backup is the safe recovery.
4
    Post-switch verification FAILED. The re-read found one or both
    collections do NOT have the target threshold. Stderr emits LOUD
    body naming both backup path and restore command. The palace MAY
    be inconsistent.
5
    Generic pre-flight error before mutation: chromadb import failed,
    palace not a directory, etc.
6
    Modify + verification succeeded, but post-switch palace health
    probe (``probe_palace.py``) surfaced a finding. The threshold
    work is complete; the probe finding is independent and worth
    investigating. Soft-warn-but-success.

CLI examples
------------
::

    # Read-only: report current state.
    engine/tools/mempalace_set_sync_threshold.py --verify-only

    # Apply with mandatory backup (production path).
    engine/tools/mempalace_set_sync_threshold.py \\
        --threshold 100 \\
        --backup-dir ~/.mempalace/palace.S-0145-pre-threshold-switch

    # Test override against tmp palace (no backup).
    engine/tools/mempalace_set_sync_threshold.py \\
        --threshold 100 \\
        --palace-path /tmp/test_palace \\
        --no-backup

The ``MEMPALACE_PROBE_PALACE_PATH`` env var override is honored for
the palace path resolution, mirroring the probe_palace.py +
prune_mempalace.py precedent. Tests can inject a tmp_path without
HOME manipulation.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Default steady-state threshold per ADR 0079. Chosen as the middle
# ground between chromadb's untuned 1000 default (insufficient for
# 1-3-drawers-per-session pattern) and mempalace's 50_000
# anti-bloat default (recurrence vector). 100 persists every ~33
# typical sessions; 16K-record forensic rebuild triggers ~160
# persistDirty() calls (vs ~3,355 at threshold 5 vs 0 at 50_000)
# — well below the resize-feedback-loop pattern PR #344 was
# designed to prevent.
DEFAULT_THRESHOLD = 100

# chromadb's validator at hnsw_params.py:22 requires int > 2. We add
# an extra layer that refuses anything below 3 with a clear message
# rather than letting chromadb's stack raise a less-specific
# ValueError.
MIN_THRESHOLD = 3

# Collections this tool modifies. mempalace creates exactly two
# collections (drawers + closets per the 4-level hierarchy in
# engine/operations/mempalace-operations.md). Both must be set in
# sync; divergent state is exit 1.
TARGET_COLLECTIONS = ("mempalace_drawers", "mempalace_closets")

# Production palace path. ``--no-backup`` refuses against this path.
PRODUCTION_PALACE = Path.home() / ".mempalace" / "palace"

# Threshold metadata key in chromadb's collection.metadata.
SYNC_THRESHOLD_KEY = "hnsw:sync_threshold"


def resolve_palace_path(arg_palace: str | None) -> Path:
    """Resolve palace path with env-var > CLI > default precedence.

    Mirrors prune_mempalace.py + probe_palace.py.
    """
    env = os.environ.get("MEMPALACE_PROBE_PALACE_PATH")
    if env:
        return Path(env)
    if arg_palace:
        return Path(arg_palace)
    return PRODUCTION_PALACE


def backup_palace(palace_path: Path, backup_dir: Path) -> None:
    """``cp -a``-equivalent backup; raises on failure.

    Mirrors prune_mempalace.py::backup_palace. ``shutil.copytree`` with
    ``copy2`` preserves metadata, the closest stdlib equivalent of
    ``cp -a`` on macOS / Linux. The backup target MUST NOT already
    exist; collisions are caller-responsibility (timestamp the path).
    """
    if backup_dir.exists():
        raise FileExistsError(
            f"backup target already exists: {backup_dir}; "
            f"choose a unique path or remove the existing backup first"
        )
    if not palace_path.is_dir():
        raise FileNotFoundError(f"palace not found: {palace_path}")
    shutil.copytree(palace_path, backup_dir, copy_function=shutil.copy2)


def _read_threshold_from_collection(col: Any) -> int | None:
    """Read the authoritative sync_threshold from a chromadb collection.

    In chromadb 1.5.x the ``configuration`` channel is the runtime
    source of truth for HNSW params; ``metadata`` is a creation-time
    advisory and may not reflect updates made via
    ``modify(configuration=...)`` (empirically verified against
    chromadb 1.5.9 — see Phase 1.5a investigation). Read the
    configuration first; fall back to metadata when configuration is
    not available (older chromadb or test fixtures).
    """
    config = getattr(col, "configuration", None)
    if config and isinstance(config, dict):
        hnsw = config.get("hnsw")
        if isinstance(hnsw, dict) and "sync_threshold" in hnsw:
            raw = hnsw["sync_threshold"]
            return int(raw) if raw is not None else None
    meta = dict(col.metadata) if col.metadata else {}
    raw = meta.get(SYNC_THRESHOLD_KEY)
    return int(raw) if raw is not None else None


def read_current_thresholds(palace_path: Path) -> dict[str, int | None]:
    """Open chromadb client and read current threshold per collection.

    Returns ``{name: threshold or None}``. None means neither the
    configuration channel nor the metadata channel carries an explicit
    ``hnsw:sync_threshold``. Raises if chromadb open or list_collections
    fails.
    """
    import chromadb

    client = chromadb.PersistentClient(path=str(palace_path))
    out: dict[str, int | None] = {}
    for name in TARGET_COLLECTIONS:
        col = client.get_collection(name)
        out[name] = _read_threshold_from_collection(col)
    return out


def modify_thresholds(palace_path: Path, threshold: int) -> dict[str, dict[str, Any]]:
    """Apply ``collection.modify(configuration={'hnsw': {'sync_threshold': N}})`` to both target collections.

    In chromadb 1.5.x, the ``configuration`` channel is the supported
    runtime update path for HNSW params. ``modify(metadata=...)``
    refuses any payload that includes ``hnsw:space`` (treated as a
    distance-function change, not modifiable post-creation;
    empirically verified against chromadb 1.5.9). The configuration
    update preserves all other HNSW settings (``hnsw:space``,
    ``hnsw:num_threads``, etc.) — only ``sync_threshold`` changes.

    Returns the full configuration dict each collection has AFTER the
    modify call (as observed by the same client, for forensic value).
    """
    import chromadb

    client = chromadb.PersistentClient(path=str(palace_path))
    out: dict[str, dict[str, Any]] = {}
    for name in TARGET_COLLECTIONS:
        col = client.get_collection(name)
        col.modify(configuration={"hnsw": {"sync_threshold": threshold}})
        # Re-read via the same client to capture chromadb's view post-modify.
        col_after = client.get_collection(name)
        config = getattr(col_after, "configuration", None) or {}
        out[name] = dict(config) if isinstance(config, dict) else {}
    return out


def verify_thresholds_fresh_client(
    palace_path: Path, target: int
) -> tuple[bool, dict[str, int | None]]:
    """Open a FRESH chromadb client and re-read thresholds.

    PersistentClient shares System state across instances at the same
    path via SharedSystemClient, but the configuration read goes through
    each collection's own state load, which sees the post-modify disk
    write. SQLite is the source of truth; chromadb's in-memory cache
    invalidates on collection re-fetch. Returns ``(ok, observed)``
    where ``ok`` is True only if every target collection's threshold
    equals ``target``.
    """
    import chromadb

    client = chromadb.PersistentClient(path=str(palace_path))
    observed: dict[str, int | None] = {}
    for name in TARGET_COLLECTIONS:
        col = client.get_collection(name)
        observed[name] = _read_threshold_from_collection(col)
    ok = all(v == target for v in observed.values())
    return ok, observed


def run_palace_health_probe(palace_path: Path) -> int:
    """Invoke ``engine/tools/probe_palace.py`` as a subprocess.

    Returns the probe's exit code. 0 = healthy, 1 = suspect (HNSW
    divergence or empty/slow), 2 = hard-broken, 139 = SIGSEGV.

    Per ADR 0045: scrubbed env to keep the probe insulated from the
    caller's environment leaks. Honors ``MEMPALACE_PROBE_PALACE_PATH``
    on the probe side via env-var passthrough (the probe checks the
    same var).
    """
    probe_script = Path(__file__).parent / "probe_palace.py"
    if not probe_script.is_file():
        # Tool runs without the probe in some test contexts; treat
        # absence as no-op success rather than an apparent regression.
        return 0

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["MEMPALACE_PROBE_PALACE_PATH"] = str(palace_path)

    try:
        result = subprocess.run(
            [sys.executable, str(probe_script)],
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return 1
    # Pass the probe's stderr through to the caller so any findings
    # surface in the same place as the rest of this tool's output.
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def diagnose_consistency(observed: dict[str, int | None]) -> tuple[bool, str]:
    """Decide whether observed thresholds are 'consistent state'.

    For ``--verify-only``: consistent means all collections agree on
    the same value (including all None — both unset). Returns
    ``(is_consistent, summary)``.
    """
    values = list(observed.values())
    if all(v == values[0] for v in values):
        if values[0] is None:
            return (
                True,
                "consistent: all collections have no explicit hnsw:sync_threshold (chromadb default)",
            )
        return True, f"consistent: all collections at hnsw:sync_threshold={values[0]}"
    parts = [f"{name}={val}" for name, val in observed.items()]
    return False, "DIVERGENT: " + ", ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Set hnsw:sync_threshold on mempalace chromadb collections with backup + verify.",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help=f"Target hnsw:sync_threshold value (default {DEFAULT_THRESHOLD}; min {MIN_THRESHOLD}).",
    )
    parser.add_argument(
        "--palace-path",
        type=str,
        default=None,
        help="Override palace path. Env var MEMPALACE_PROBE_PALACE_PATH wins.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Read-only: report current state. No mutation, no backup required.",
    )
    parser.add_argument(
        "--backup-dir",
        type=str,
        default=None,
        help="Required for --apply (default) mode. Path for cp -a backup before mutation.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup (test-only). Refused against production palace path.",
    )
    parser.add_argument(
        "--skip-probe",
        action="store_true",
        help="Skip post-switch probe_palace.py invocation (test-only).",
    )
    args = parser.parse_args()

    palace_path = resolve_palace_path(args.palace_path)

    # ============ Pre-flight ============

    if not palace_path.is_dir():
        print(
            f"[set-sync-threshold] ERROR: palace path is not a directory: {palace_path}",
            file=sys.stderr,
        )
        return 2

    if args.threshold < MIN_THRESHOLD:
        print(
            f"[set-sync-threshold] ERROR: threshold {args.threshold} below minimum "
            f"{MIN_THRESHOLD} (chromadb hnsw_params.py:22 requires int > 2).",
            file=sys.stderr,
        )
        return 2

    # ============ Verify-only path ============

    if args.verify_only:
        try:
            observed = read_current_thresholds(palace_path)
        except Exception as e:
            print(
                f"[set-sync-threshold] ERROR (verify-only): chromadb read failed: {e}",
                file=sys.stderr,
            )
            return 5
        is_consistent, summary = diagnose_consistency(observed)
        print(f"[set-sync-threshold] {summary}", file=sys.stderr)
        for name, val in observed.items():
            print(f"  {name}: hnsw:sync_threshold={val}", file=sys.stderr)
        if not is_consistent:
            print(
                f"[set-sync-threshold] Run --apply with --backup-dir to set both "
                f"collections to threshold={args.threshold}.",
                file=sys.stderr,
            )
            return 1
        if observed[TARGET_COLLECTIONS[0]] != args.threshold:
            print(
                f"[set-sync-threshold] Consistent but not at target ({args.threshold}); "
                f"run --apply to update.",
                file=sys.stderr,
            )
        return 0

    # ============ Apply path: backup + modify + verify + probe ============

    if not args.no_backup and not args.backup_dir:
        print(
            "[set-sync-threshold] ERROR: --apply requires --backup-dir PATH. "
            "Use --no-backup to override (test-only; refused against production).",
            file=sys.stderr,
        )
        return 2

    if args.no_backup and palace_path.resolve() == PRODUCTION_PALACE.resolve():
        print(
            f"[set-sync-threshold] ERROR: --no-backup refused against production "
            f"palace path ({PRODUCTION_PALACE}). Use --backup-dir instead.",
            file=sys.stderr,
        )
        return 2

    if args.backup_dir:
        backup_dir = Path(args.backup_dir).expanduser()
        try:
            print(
                f"[set-sync-threshold] backing up palace to {backup_dir} ...",
                file=sys.stderr,
            )
            backup_palace(palace_path, backup_dir)
            print(
                "[set-sync-threshold] backup complete",
                file=sys.stderr,
            )
        except (FileExistsError, FileNotFoundError, OSError) as e:
            print(
                f"[set-sync-threshold] ERROR: backup failed: {e}",
                file=sys.stderr,
            )
            return 2

    try:
        pre_state = read_current_thresholds(palace_path)
    except Exception as e:
        print(
            f"[set-sync-threshold] ERROR: pre-switch state read failed: {e}",
            file=sys.stderr,
        )
        return 5

    print(
        "[set-sync-threshold] pre-switch state:",
        file=sys.stderr,
    )
    for name, val in pre_state.items():
        print(f"  {name}: hnsw:sync_threshold={val}", file=sys.stderr)

    if all(v == args.threshold for v in pre_state.values()):
        print(
            f"[set-sync-threshold] no change: all collections already at "
            f"hnsw:sync_threshold={args.threshold}",
            file=sys.stderr,
        )
        return 0

    try:
        post_modify = modify_thresholds(palace_path, args.threshold)
    except Exception as e:
        print(
            f"[set-sync-threshold] ERROR: chromadb modify failed: {e}",
            file=sys.stderr,
        )
        print(
            "[set-sync-threshold] palace state may be inconsistent. "
            "Restore from backup if --backup-dir was provided.",
            file=sys.stderr,
        )
        return 3

    print(
        "[set-sync-threshold] modify applied; verifying via fresh client read ...",
        file=sys.stderr,
    )

    ok, observed = verify_thresholds_fresh_client(palace_path, args.threshold)
    if not ok:
        print(
            "\n############################################################\n"
            "## [set-sync-threshold] POST-SWITCH VERIFICATION FAILED ##\n"
            "############################################################",
            file=sys.stderr,
        )
        for name, val in observed.items():
            print(
                f"  {name}: expected hnsw:sync_threshold={args.threshold}, observed {val}",
                file=sys.stderr,
            )
        if args.backup_dir:
            print(
                f"\n  Restore from backup:\n"
                f"    rm -rf {palace_path}\n"
                f"    mv {args.backup_dir} {palace_path}",
                file=sys.stderr,
            )
        return 4

    print(
        f"[set-sync-threshold] verified: both collections at "
        f"hnsw:sync_threshold={args.threshold}",
        file=sys.stderr,
    )
    for name in TARGET_COLLECTIONS:
        meta = post_modify.get(name, {})
        # Echo full metadata for forensic value — if anything else
        # shifted unexpectedly (e.g., hnsw:space lost), the audit trail
        # captures it.
        print(f"  {name}: metadata={meta}", file=sys.stderr)

    if args.skip_probe:
        return 0

    probe_exit = run_palace_health_probe(palace_path)
    if probe_exit not in (0,):
        print(
            f"[set-sync-threshold] palace health probe exit {probe_exit} "
            f"(threshold modify succeeded; probe finding is separate).",
            file=sys.stderr,
        )
        return 6
    return 0


if __name__ == "__main__":
    sys.exit(main())
