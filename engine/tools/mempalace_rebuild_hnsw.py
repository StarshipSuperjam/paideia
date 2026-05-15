"""Non-destructive HNSW rebuild for a chromadb-backed mempalace palace.

Bypasses ``mempalace repair --mode legacy``, which S-0078 confirmed
destroys SQLite embedding rows (99.7% loss observed against the version
installed at S-0078; see engine/operations/mempalace-operations.md
"Known issues" and the S-0084 upstream tracker). Per ADR 0045 amendment
(S-0084).

Why SQLite-direct extraction instead of chromadb's get(include=["embeddings"])
-----------------------------------------------------------------------------
On a divergent palace (drawers in SQLite that aren't in HNSW), chromadb's
``collection.get(include=["embeddings"])`` raises
``InternalError: Error finding id`` — exactly the signal Issue #31
describes. The HNSW index is the authoritative store for vector data;
when the index is missing entries, the vectors for those entries are
genuinely lost in this palace.

Two implementation paths existed:
1. Read embeddings via chromadb's public API. Fast, preserves original
   vectors, BUT silently fails on divergent palaces — the operative case.
2. Read documents + metadata from SQLite directly. Pass to
   ``collection.add(ids, documents, metadatas)`` WITHOUT ``embeddings``
   — chromadb re-computes via the registered embedding function and
   writes both SQLite and HNSW fresh.

This tool implements path 2 because the operative case is restoration
of a divergent palace. Trade-off: the new embeddings are produced by
the current chromadb default embedding function. If that function has
shifted (chromadb version bump, model update), the rebuilt vectors
won't be byte-identical to originals. This is acceptable for the
restoration use case — semantic similarity behavior is preserved at
the model-family level, and the alternative is to permanently lose the
divergent drawers' data.

Algorithm (per collection):

1. Resolve the collection's METADATA segment in SQLite via
   ``segments.collection`` join.
2. Read all ``(embedding_id, document, metadata-dict)`` tuples by
   joining ``embeddings`` with ``embedding_metadata``.
3. Verify count matches ``collection.count()`` (the chromadb-layer
   ground truth). Refuse to proceed on mismatch (defensive against
   #1208's 10K cap pattern).
4. ``client.delete_collection(name)`` then
   ``client.create_collection(name, metadata=...)`` — preserves the
   user-facing ``hnsw:space`` and other collection metadata.
5. Re-add via paginated ``new_col.add(ids, documents, metadatas)``
   — chromadb re-computes embeddings AND writes HNSW + SQLite together.
6. Optionally verify post-rebuild divergence is < 1% via upstream's
   read-only ``mempalace repair-status``.

Run against a scratch copy of the palace first; only swap the rebuilt
copy into ``~/.mempalace/palace`` once divergence is confirmed.

Exit codes
----------
0
    Rebuild successful and post-verify divergence < 1% (or verify-only
    succeeded with that condition; or dry-run completed cleanly).
1
    Pre-rebuild count check failed (SQLite extraction returned fewer
    drawers than ``collection.count()`` reports). Refuses to proceed;
    live state untouched.
2
    Rebuild failed mid-flight. The collection was deleted but re-add
    did not complete; the palace is now missing this collection's
    drawers. Caller MUST restore from a pre-rebuild snapshot.
3
    Rebuild appeared to complete but post-verify divergence still
    >= 1%. The palace is in a "partially rebuilt" state — drawers are
    present but HNSW didn't close the gap.
4
    Refused to proceed because the collection uses a non-default
    embedding function (out-of-scope for this tool — re-embedding via
    a non-default model isn't safe to do automatically).
5
    Generic error before any destructive action — e.g., palace path
    missing, chromadb import failed, target collection absent, SQLite
    schema not as expected.
"""

from __future__ import annotations

import argparse
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Default batch size for paginated re-add. 5000 per the upstream Issue
# #1208 "Suggested Fix" — large enough to amortize round-trip cost,
# small enough to fit comfortably in memory and below chromadb's 10K-row
# internal cap that #1208 documents.
DEFAULT_BATCH_SIZE = 5000

# Divergence threshold for post-rebuild verification. <1% accommodates
# floating-point timing of concurrent writes during the rebuild
# (e.g., the MCP server adds a drawer between extraction and re-add).
POST_REBUILD_DIVERGENCE_PCT = 1.0

# S-0187 amendment of ADR 0079. At collection-creation time during a
# rebuild, override mempalace's _HNSW_BLOAT_GUARD inheritance of
# ``hnsw:sync_threshold=50_000`` with a low value (3) so chromadb's
# ``_apply_batch`` _persist() fires after each pagination batch. The
# rebuilt segment's ``link_lists.bin`` + ``index_metadata.pickle``
# are written to disk by the time the rebuild finishes, instead of
# remaining in process memory until a process-exit that never flushes.
# The S-0186 audit documented the falsification: post-rebuild the
# segment's link_lists.bin was 0 bytes because the rebuild's adds
# never crossed the inherited 50_000 threshold. ADR 0079's
# ≥150-session recurrence interval premise was falsified at 39
# sessions for this reason. Chromadb's hnsw_params.py validator
# floors at ``int > 2`` so 3 is the minimum.
REBUILD_SYNC_THRESHOLD = 3

# Project steady-state sync_threshold per ADR 0079. Applied via
# ``collection.modify(configuration={...})`` after all paginated adds
# complete. The retrofit uses chromadb 1.5.x's authoritative
# ``configuration`` channel; the metadata channel is creation-time
# advisory only and does not reflect post-modify updates. Day-to-day
# 1-3-drawers-per-session writes accumulate to 100 every ~33 sessions
# under normal load; segment persist fires at that cadence under
# steady state and the recurrence vector is bounded.
STEADY_STATE_SYNC_THRESHOLD = 100

# Regex for `mempalace repair-status` drawer counts — same shape as
# probe_palace.py's _REPAIR_STATUS_DRAWERS_RE for consistency.
_REPAIR_STATUS_DRAWERS_RE = re.compile(
    r"\[drawers\][\s\S]*?sqlite\s+count:\s*([\d,]+)"
    r"[\s\S]*?hnsw\s+count:\s*([\d,]+)",
    re.IGNORECASE,
)

# Key under which chromadb stores the document text in embedding_metadata.
_DOCUMENT_KEY = "chroma:document"


def _emit(stream: str, line: str) -> None:
    target = sys.stderr if stream == "err" else sys.stdout
    print(line, file=target, flush=True)


def _read_divergence(palace_path: Path) -> tuple[int, int, float] | None:
    """Run ``mempalace repair-status`` against ``palace_path``; parse counts."""
    try:
        proc = subprocess.run(
            ["mempalace", "--palace", str(palace_path), "repair-status"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    except Exception:  # noqa: BLE001
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


def _extract_collection_from_sqlite(
    sqlite_path: Path, collection_name: str
) -> dict[str, list[Any]]:
    """Read all drawer (id, document, metadata) tuples from chroma.sqlite3.

    Returns a dict ``{"ids": [...], "documents": [...], "metadatas": [...]}``.
    Each metadatas entry is a dict (may be empty); chromadb's add() accepts
    None for "no metadata" but we always emit a (possibly empty) dict for
    consistency. Raises ``ValueError`` on schema violation or missing
    collection.
    """
    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    try:
        # Resolve collection_id by name.
        coll_row = cur.execute(
            "SELECT id FROM collections WHERE name = ?", (collection_name,)
        ).fetchone()
        if not coll_row:
            raise ValueError(f"collection {collection_name!r} not in SQLite")
        coll_id = coll_row[0]

        # Resolve METADATA segment id (chromadb's internal SQLite-backed
        # metadata segment; the HNSW vector segment is separate and is
        # what we're rebuilding).
        seg_row = cur.execute(
            "SELECT id FROM segments WHERE collection = ? AND scope = 'METADATA'",
            (coll_id,),
        ).fetchone()
        if not seg_row:
            raise ValueError(f"no METADATA segment for collection {collection_name!r}")
        seg_id = seg_row[0]

        # Pull all (embedding_id, embeddings.id) for this segment so we
        # know how many rows to expect and have the join key.
        embedding_rows = cur.execute(
            "SELECT id, embedding_id FROM embeddings WHERE segment_id = ?",
            (seg_id,),
        ).fetchall()
        if not embedding_rows:
            return {"ids": [], "documents": [], "metadatas": []}

        # Build (id -> embedding_id) reverse for assembling per-drawer dicts.
        id_to_embedding_id: dict[int, str] = dict(embedding_rows)
        all_internal_ids = list(id_to_embedding_id.keys())

        # Pull all metadata for these rows in one query (paginate by
        # internal id chunk to avoid SQL parameter limits).
        per_drawer: dict[str, dict[str, Any]] = {}
        documents: dict[str, str | None] = {}
        # SQLite default param limit is 999; chunk at 500 to stay safe.
        CHUNK = 500
        for start in range(0, len(all_internal_ids), CHUNK):
            chunk = all_internal_ids[start : start + CHUNK]
            placeholders = ",".join("?" * len(chunk))
            sql = f"""
                SELECT id, key, string_value, int_value, float_value, bool_value
                FROM embedding_metadata
                WHERE id IN ({placeholders})
                """  # nosec B608  # placeholder string construction; chunk values parameterized via execute(sql, chunk)
            rows = cur.execute(sql, chunk).fetchall()
            for row in rows:
                internal_id, key, sv, iv, fv, bv = row
                drawer_id = id_to_embedding_id[internal_id]
                # Pick the non-null typed value. Order matches chromadb's
                # write path: string > int > float > bool.
                if sv is not None:
                    value: object = sv
                elif iv is not None:
                    value = iv
                elif fv is not None:
                    value = fv
                elif bv is not None:
                    value = bool(bv)
                else:
                    continue
                if key == _DOCUMENT_KEY:
                    documents[drawer_id] = str(value) if value is not None else None
                else:
                    per_drawer.setdefault(drawer_id, {})[key] = value

        ids = [emb_id for _, emb_id in embedding_rows]
        out_documents: list[str | None] = [documents.get(i) for i in ids]
        out_metadatas: list[dict[str, Any]] = [per_drawer.get(i, {}) for i in ids]
        return {"ids": ids, "documents": out_documents, "metadatas": out_metadatas}
    finally:
        conn.close()


def _add_paginated(col: Any, content: dict[str, list[Any]], batch_size: int) -> None:
    """Re-add extracted content via ``col.add()`` in BATCH-sized chunks.

    Passes ``ids``, ``documents``, ``metadatas`` only — chromadb computes
    fresh embeddings via the collection's embedding_function and writes
    BOTH the SQLite metadata segment and the HNSW vector segment in
    one call. Documents/metadatas with ``None`` values use a partition-
    by-presence pattern to satisfy chromadb's all-or-nothing expectation.
    """
    ids = content["ids"]
    documents = content["documents"]
    metadatas = content["metadatas"]

    n = len(ids)
    n_batches = (n + batch_size - 1) // batch_size
    for batch_idx, start in enumerate(range(0, n, batch_size)):
        end = min(start + batch_size, n)
        batch_ids = ids[start:end]
        batch_docs = documents[start:end]
        batch_meta = metadatas[start:end]

        kwargs: dict[str, Any] = {"ids": batch_ids}
        # chromadb add() needs documents (or embeddings) — without either,
        # it raises. We always have documents since we read them from
        # SQLite; refuse to add a batch where any document is None.
        if any(d is None for d in batch_docs):
            missing = [i for i, d in zip(batch_ids, batch_docs) if d is None]
            raise RuntimeError(
                f"batch contains {len(missing)} drawer(s) with no document; "
                f"first id: {missing[0]!r}. Cannot re-embed without source text."
            )
        kwargs["documents"] = batch_docs
        if any(m for m in batch_meta):
            kwargs["metadatas"] = [m if m else None for m in batch_meta]
        t_batch_start = time.monotonic()
        col.add(**kwargs)
        t_batch = time.monotonic() - t_batch_start
        _emit(
            "out",
            f"[rebuild]   batch {batch_idx + 1}/{n_batches}: "
            f"added {end - start} drawers in {t_batch:.1f}s "
            f"(progress {end}/{n} = {end / n * 100:.1f}%)",
        )


def _build_embedding_function(preferred_providers: list[str] | None) -> Any:
    """Instantiate the chromadb default embedding function with preferred providers.

    Returns ``None`` to leave chromadb's default-init (CPU-only) in place
    when no preferred providers are specified. When provided, returns an
    ``ONNXMiniLM_L6_V2(preferred_providers=...)`` instance — chromadb
    stores the function's registered name in ``configuration_json``,
    so the providers override is process-local and doesn't pollute the
    persisted collection metadata.
    """
    if not preferred_providers:
        return None
    try:
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import (  # noqa: PLC0415
            ONNXMiniLM_L6_V2,
        )
    except Exception:
        return None
    return ONNXMiniLM_L6_V2(preferred_providers=list(preferred_providers))


def rebuild_collection(
    client: Any,
    palace_path: Path,
    collection_name: str,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    dry_run: bool = False,
    preferred_providers: list[str] | None = None,
) -> dict[str, Any]:
    """Rebuild ``collection_name`` in-place. Returns a summary dict."""
    summary: dict[str, Any] = {"collection": collection_name, "started_at": time.time()}

    col = client.get_collection(collection_name)
    metadata = dict(col.metadata or {})
    # S-0187 amendment of ADR 0079: at create-collection time below,
    # the rebuild inherits mempalace's _HNSW_BLOAT_GUARD
    # ``hnsw:sync_threshold=50_000`` which prevents chromadb's
    # ``_apply_batch`` _persist() from ever firing during the
    # rebuild's adds. Override to REBUILD_SYNC_THRESHOLD here so the
    # segment's HNSW metadata + edge connectivity actually land on
    # disk during the rebuild. Post-adds, ``_raise_to_steady_state``
    # below modifies the configuration channel to
    # STEADY_STATE_SYNC_THRESHOLD per ADR 0079. ``hnsw:batch_size``
    # is left at the inherited value (50_000) — that's the
    # anti-bloat protection PR #344 designed for; it controls HNSW
    # index resize cadence which is independent of persist cadence.
    rebuild_metadata = dict(metadata)
    rebuild_metadata["hnsw:sync_threshold"] = REBUILD_SYNC_THRESHOLD
    config_json = getattr(col, "configuration_json", None) or {}
    embed_fn = (config_json.get("embedding_function") or {}).get("name", "default")
    if embed_fn != "default":
        summary["error"] = (
            f"non-default embedding function: {embed_fn!r}. "
            "Manual embedding_function reconstruction required."
        )
        summary["exit_code"] = 4
        return summary

    expected_total = col.count()
    summary["expected_drawers"] = expected_total
    _emit(
        "out",
        f"[rebuild] {collection_name}: {expected_total} drawers, "
        f"metadata={metadata}, embed_fn={embed_fn}",
    )

    sqlite_path = palace_path / "chroma.sqlite3"
    if not sqlite_path.is_file():
        summary["error"] = f"chroma.sqlite3 not found at {sqlite_path}"
        summary["exit_code"] = 5
        return summary

    _emit("out", f"[rebuild] {collection_name}: extracting from SQLite")
    try:
        content = _extract_collection_from_sqlite(sqlite_path, collection_name)
    except (sqlite3.Error, ValueError) as exc:
        summary["error"] = f"SQLite extraction failed: {exc}"
        summary["exit_code"] = 5
        return summary

    extracted = len(content["ids"])
    summary["extracted_drawers"] = extracted

    if extracted != expected_total:
        summary["error"] = (
            f"extraction short: collection.count()={expected_total} but "
            f"SQLite extraction returned {extracted}. Refuse to rebuild "
            "(defensive against upstream Issues #1208 / #1238)."
        )
        summary["exit_code"] = 1
        return summary

    if dry_run:
        # Sanity: how many drawers carry documents?
        docs_present = sum(1 for d in content["documents"] if d is not None)
        _emit(
            "out",
            f"[rebuild] {collection_name}: DRY RUN — would delete and re-add "
            f"{extracted} drawers ({docs_present} with documents). No writes.",
        )
        if docs_present != extracted:
            _emit(
                "err",
                f"[rebuild] {collection_name}: WARNING — "
                f"{extracted - docs_present} drawer(s) have no document text. "
                "Real rebuild would refuse those rows.",
            )
        summary["dry_run"] = True
        summary["docs_present"] = docs_present
        summary["exit_code"] = 0
        return summary

    _emit("out", f"[rebuild] {collection_name}: deleting collection")
    try:
        client.delete_collection(collection_name)
    except Exception as exc:
        summary["error"] = f"delete_collection failed: {exc}"
        summary["exit_code"] = 5
        return summary

    _emit(
        "out",
        f"[rebuild] {collection_name}: recreating with metadata={rebuild_metadata} "
        f"(S-0187: sync_threshold={REBUILD_SYNC_THRESHOLD} at create; "
        f"raised to {STEADY_STATE_SYNC_THRESHOLD} after adds complete)",
    )
    try:
        embed_fn_instance = _build_embedding_function(preferred_providers)
        if embed_fn_instance is not None:
            _emit(
                "out",
                f"[rebuild] {collection_name}: using preferred providers "
                f"{preferred_providers} for embedding inference",
            )
            new_col = client.create_collection(
                name=collection_name,
                metadata=rebuild_metadata,
                embedding_function=embed_fn_instance,
            )
        else:
            new_col = client.create_collection(
                name=collection_name, metadata=rebuild_metadata
            )
    except Exception as exc:
        summary["error"] = (
            f"create_collection failed AFTER delete_collection succeeded: {exc}. "
            f"Palace is missing collection {collection_name!r}; restore from snapshot."
        )
        summary["exit_code"] = 2
        return summary

    _emit(
        "out",
        f"[rebuild] {collection_name}: re-adding {extracted} drawers "
        f"(chromadb re-embeds via default fn)",
    )
    try:
        _add_paginated(new_col, content, batch_size)
    except Exception as exc:
        summary["error"] = (
            f"add() failed mid-rebuild after delete_collection: {exc}. "
            f"Palace is missing collection {collection_name!r}'s drawers; "
            "restore from snapshot."
        )
        summary["exit_code"] = 2
        return summary

    final_count = new_col.count()
    summary["final_drawers"] = final_count
    if final_count != extracted:
        summary["error"] = (
            f"post-rebuild count mismatch: extracted={extracted}, "
            f"new_col.count()={final_count}"
        )
        summary["exit_code"] = 3
        return summary

    # S-0187 amendment of ADR 0079: now that all adds have completed
    # against the low REBUILD_SYNC_THRESHOLD (so the segment's HNSW
    # state has been persisted to disk), raise to the project
    # steady-state STEADY_STATE_SYNC_THRESHOLD via chromadb 1.5.x's
    # ``configuration`` channel — the authoritative runtime source
    # per ADR 0079 (the metadata channel is creation-time advisory
    # only and does not reflect post-modify updates).
    #
    # Failure here is non-fatal: the rebuild succeeded (drawers
    # persisted at threshold=3); a failed threshold-raise just means
    # the live state-going-forward will persist after every 3 writes
    # instead of every 100, which is wasteful but not broken. Logged
    # for visibility; summary records the threshold actually applied.
    try:
        new_col.modify(
            configuration={"hnsw": {"sync_threshold": STEADY_STATE_SYNC_THRESHOLD}}
        )
        summary["final_sync_threshold"] = STEADY_STATE_SYNC_THRESHOLD
        _emit(
            "out",
            f"[rebuild] {collection_name}: raised sync_threshold "
            f"{REBUILD_SYNC_THRESHOLD} → {STEADY_STATE_SYNC_THRESHOLD} "
            f"via configuration channel (steady-state per ADR 0079)",
        )
    except Exception as exc:  # noqa: BLE001  # post-rebuild non-fatal
        summary["final_sync_threshold"] = REBUILD_SYNC_THRESHOLD
        summary["threshold_raise_warning"] = str(exc)
        _emit(
            "err",
            f"[rebuild] {collection_name}: WARNING — could not raise "
            f"sync_threshold to {STEADY_STATE_SYNC_THRESHOLD} "
            f"({type(exc).__name__}: {exc}). Live writes will persist "
            f"at every {REBUILD_SYNC_THRESHOLD} drawers (wasteful but "
            f"correct). Run mempalace_set_sync_threshold.py manually "
            f"post-swap to fix.",
        )

    summary["finished_at"] = time.time()
    summary["elapsed_s"] = summary["finished_at"] - summary["started_at"]
    summary["exit_code"] = 0
    _emit(
        "out",
        f"[rebuild] {collection_name}: SUCCESS — {final_count} drawers "
        f"in {summary['elapsed_s']:.1f}s",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Non-destructive HNSW rebuild for a chromadb-backed mempalace "
            "palace. Reads (id, document, metadata) directly from SQLite, "
            "deletes + recreates the collection, and re-adds via "
            "collection.add() WITHOUT explicit embeddings — chromadb "
            "re-computes via the default embedding function and writes both "
            "SQLite and HNSW segments fresh. Always run on a scratch copy first."
        )
    )
    parser.add_argument(
        "--palace",
        required=True,
        help="Path to the palace directory (no default; explicit safety).",
    )
    parser.add_argument(
        "--collection",
        action="append",
        default=None,
        help=(
            "Collection name to rebuild (repeatable). Default: rebuild every "
            "collection chromadb knows about (mempalace_drawers + "
            "mempalace_closets in the standard mempalace layout)."
        ),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Pagination batch size (default: {DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read counts, print what would happen, write nothing.",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help=(
            "Run `mempalace repair-status` and exit. No rebuild. "
            "Useful as a sanity check pre/post."
        ),
    )
    parser.add_argument(
        "--embedding-providers",
        default=None,
        help=(
            "Comma-separated ONNX runtime providers to prefer for embedding "
            "inference (e.g., 'CoreMLExecutionProvider,CPUExecutionProvider'). "
            "Default: leave chromadb's default-init in place (CPU on most "
            "systems). On Apple Silicon, CoreMLExecutionProvider yields "
            "5-10x throughput vs CPU. Process-local; chromadb persists only "
            "the embedding function's registered name, not the providers."
        ),
    )
    args = parser.parse_args(argv)

    preferred_providers: list[str] | None = None
    if args.embedding_providers:
        preferred_providers = [
            p.strip() for p in args.embedding_providers.split(",") if p.strip()
        ]

    palace_path = Path(args.palace).expanduser().resolve()
    if not palace_path.exists():
        _emit("err", f"[rebuild] palace path not found: {palace_path}")
        return 5

    if args.verify_only:
        divergence = _read_divergence(palace_path)
        if divergence is None:
            _emit("err", "[rebuild] verify-only: divergence unavailable")
            return 5
        sqlite_n, hnsw_n, pct = divergence
        _emit(
            "out",
            f"[rebuild] verify-only: SQLite={sqlite_n} HNSW={hnsw_n} "
            f"divergence={pct:.2f}%",
        )
        return 0 if pct < POST_REBUILD_DIVERGENCE_PCT else 3

    try:
        import chromadb  # noqa: PLC0415 — deferred import keeps tool importable
    except Exception as exc:
        _emit("err", f"[rebuild] chromadb import failed: {exc}")
        return 5

    try:
        client = chromadb.PersistentClient(path=str(palace_path))
    except Exception as exc:
        _emit("err", f"[rebuild] PersistentClient open failed: {exc}")
        return 5

    if args.collection:
        target_collections = list(args.collection)
    else:
        target_collections = [c.name for c in client.list_collections()]

    overall_exit = 0
    for name in target_collections:
        result = rebuild_collection(
            client,
            palace_path,
            name,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
            preferred_providers=preferred_providers,
        )
        if "error" in result:
            _emit("err", f"[rebuild] {name}: {result['error']}")
        if result.get("exit_code", 0) != 0 and overall_exit == 0:
            overall_exit = result["exit_code"]

    if args.dry_run or overall_exit not in (0,):
        return overall_exit

    # Post-verify via upstream's repair-status (read-only, no chromadb client).
    divergence = _read_divergence(palace_path)
    if divergence is None:
        _emit(
            "err",
            "[rebuild] post-verify: divergence unavailable "
            "(mempalace repair-status not in PATH or output unrecognized). "
            "Rebuild itself completed; verify manually.",
        )
        return 0
    sqlite_n, hnsw_n, pct = divergence
    _emit(
        "out",
        f"[rebuild] post-verify: SQLite={sqlite_n} HNSW={hnsw_n} divergence={pct:.2f}%",
    )
    if pct >= POST_REBUILD_DIVERGENCE_PCT:
        return 3

    # Forward-pointer: per ADR 0079 (S-0145 + S-0187 amendment), the
    # rebuild now overrides ``hnsw:sync_threshold=3`` at create-collection
    # time (so the in-rebuild persist fires after each batch) and raises
    # to the project steady-state of 100 via ``collection.modify`` after
    # all adds complete. The pre-S-0187 forward-pointer instructed a
    # separate ``mempalace_set_sync_threshold.py --threshold 100`` step
    # post-swap — that's no longer needed; the rebuild self-applies.
    # ``mempalace_set_sync_threshold.py`` retains a narrower role:
    # standalone retrofit on a live palace where no rebuild has run.
    _emit(
        "err",
        "\n[rebuild] post-rebuild status (per ADR 0079 + S-0187 amendment):\n"
        "  Rebuilt collections were created with sync_threshold=3 (force\n"
        "  per-batch persist) and raised to 100 (project steady-state)\n"
        "  via collection.modify(configuration=...) after the adds\n"
        "  completed. ``link_lists.bin`` + ``index_metadata.pickle``\n"
        "  should now be present and non-zero on each segment.\n"
        "  Verify with:\n"
        "    ls -la <palace>/<segment-uuid>/link_lists.bin\n"
        "    ls -la <palace>/<segment-uuid>/index_metadata.pickle\n"
        "  Both files should exist with non-zero size. If link_lists.bin\n"
        "  is 0 or index_metadata.pickle missing, file an Issue: the\n"
        "  S-0187 amendment's premise has been falsified.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
