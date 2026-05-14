"""Seed-graph QA census sharding tool.

Layer 1 contract per the S-0156 approved plan
(``~/.claude/plans/i-need-to-build-scalable-steele.md``); methodology
doc at ``engine/build_readiness/seed_qa_audit.md``.

Purpose
-------
The seed-graph QA census (routine target ``T-SEED-QA``) checks every
``pedagogical_prerequisite`` edge and every node in the Phase 5 seed
graph exactly once across 19 routine sessions, scoring three criteria:
C1 prerequisite soundness (edges), C2 teaching_notes traction (nodes),
C3 summary cold-readability (nodes).

Sampling without replacement across *unattended* routine sessions needs
a deterministic, pre-computed assignment — there is no shared mutable
state a routine session can safely append to mid-run. This tool solves
that: it reads the live graph once (interactive setup, so the
Production Reads gate per ADR 0055 does not apply), deterministically
shuffles, splits into N shards, and writes a single committed manifest
with **full element content embedded per shard**. Routine sessions then
only read that JSON file — no per-session DB access.

The tool is run **once** at routine setup and its output committed.
Re-running with the same ``--shards`` and ``--seed`` produces a
byte-identical manifest (modulo the ``generated_at`` timestamp and any
drift in the live graph itself).

Edge scope
----------
Only ``edge_type = 'pedagogical_prerequisite'`` edges enter the census.
C1 asks "is this a genuine pedagogical prerequisite?" — a question that
does not apply to ``historical_influence`` edges, which are a distinct,
deliberately-typed predicate per ``PREDICATE_MANIFEST.md``. All nodes
(every ``status``) enter the census; the evidence session sees each
node's ``status`` and can note it.

CLI
---
- (default) read the live graph, build shards, write the manifest::

      python3 engine/tools/seed_qa_shard.py

- ``--shards N`` — shard count (default 19; 516 edges / 19 ~= 27 per
  shard, 380 nodes / 19 = 20 per shard).
- ``--seed S`` — integer RNG seed (default :data:`SHARD_RANDOM_SEED`).
- ``--output PATH`` — manifest path (default
  ``engine/build_readiness/seed_qa_evidence/shards.json``).
- ``--dry-run`` — read the graph, compute shards, print the summary;
  write nothing.

Exit codes
----------
- ``0`` — manifest written (or dry-run summary printed).
- ``2`` — ``SUPABASE_DB_URL`` unresolved, or psycopg unavailable, or a
  DB error. Stderr names the cause.

Non-responsibilities
--------------------
- No DB writes. Read-only ``SELECT`` against ``public.nodes`` /
  ``public.edges``.
- Does not score anything — scoring is the routine session's job per
  ``seed_qa_audit.md``. This tool only partitions.
- Not for routine-session invocation. Routine sessions consume the
  manifest; they do not regenerate it.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _venv_reexec import ensure_venv_python  # noqa: E402

ensure_venv_python()  # re-exec under venv if psycopg is unavailable

from load_env import load_dotenv_walk_up  # noqa: E402
from timestamps import emit  # noqa: E402  # ADR 0058

# REPO_ROOT walks three levels up: seed_qa_shard.py -> tools/ -> engine/ -> root.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_OUTPUT = (
    REPO_ROOT / "engine" / "build_readiness" / "seed_qa_evidence" / "shards.json"
)
DEFAULT_SHARD_COUNT = 19

# Fixed integer seed — re-running the tool produces byte-identical shard
# assignments. The value is the S-0156 authoring date (2026-05-14); the
# specific number is immaterial, only its fixity matters.
SHARD_RANDOM_SEED = 20260514

SUPABASE_DB_URL_ENV = "SUPABASE_DB_URL"

CENSUS_EDGE_TYPE = "pedagogical_prerequisite"


# ---------------------------------------------------------------------------
# DB I/O — monkey-patched in tests
# ---------------------------------------------------------------------------


def read_graph(
    connection_string: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read census nodes and edges from the live Supabase DB via psycopg.

    Pure I/O. Tests monkey-patch this function with fixture data.

    Returns ``(nodes, edges)`` where:

    - ``nodes`` carry ``id, label, domain, summary, teaching_notes,
      confidence_level, status`` — every row of ``public.nodes``.
    - ``edges`` carry ``id, source_id, target_id, edge_type, weight,
      confidence, evidence`` — only ``pedagogical_prerequisite`` rows.
      ``id`` is coerced to ``str`` (the column is UUID) so the rest of
      the pipeline is JSON-native.

    psycopg is imported lazily so the module loads even when the
    dependency is absent; :func:`main` handles the ImportError.
    """
    import psycopg  # type: ignore[import-not-found,unused-ignore]
    from psycopg.rows import dict_row  # type: ignore[import-not-found,unused-ignore]

    with psycopg.connect(connection_string) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT id, label, domain, summary, teaching_notes, "
                "confidence_level, status FROM public.nodes"
            )
            nodes = [dict(r) for r in cur.fetchall()]
            cur.execute(
                "SELECT id, source_id, target_id, edge_type, weight, "
                "confidence, evidence FROM public.edges WHERE edge_type = %s",
                (CENSUS_EDGE_TYPE,),
            )
            edges = [dict(r) for r in cur.fetchall()]
    for e in edges:
        e["id"] = str(e["id"])
    return nodes, edges


# ---------------------------------------------------------------------------
# Pure transforms — fully unit-testable without a DB
# ---------------------------------------------------------------------------


def enrich_edges(
    edges: list[dict[str, Any]], nodes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return ``edges`` with each endpoint's label and domain attached.

    Adds ``source_label``, ``source_domain``, ``target_label``,
    ``target_domain`` so a routine session reviewing an edge does not
    need a separate node lookup. A missing endpoint (should not happen —
    ``validate.py`` hard-fails dangling edges) yields ``None`` for that
    endpoint's label/domain rather than raising.

    Does not mutate the input list; returns new dicts.
    """
    by_id = {n["id"]: n for n in nodes}
    enriched: list[dict[str, Any]] = []
    for e in edges:
        src = by_id.get(e["source_id"])
        tgt = by_id.get(e["target_id"])
        enriched.append(
            {
                **e,
                "source_label": src["label"] if src else None,
                "source_domain": src["domain"] if src else None,
                "target_label": tgt["label"] if tgt else None,
                "target_domain": tgt["domain"] if tgt else None,
            }
        )
    return enriched


def even_split(items: list[Any], n: int) -> list[list[Any]]:
    """Split ``items`` into ``n`` contiguous chunks of near-equal size.

    Chunk sizes differ by at most 1; the first ``len(items) % n`` chunks
    get the extra element. When ``n > len(items)`` the trailing chunks
    are empty. ``n`` must be >= 1.

    Contiguous (not round-robin) so a shard is a prefix-range of the
    shuffled list — intuitive for anyone inspecting the manifest.
    """
    if n < 1:
        raise ValueError(f"shard count must be >= 1, got {n}")
    base, extra = divmod(len(items), n)
    chunks: list[list[Any]] = []
    start = 0
    for i in range(n):
        size = base + (1 if i < extra else 0)
        chunks.append(items[start : start + size])
        start += size
    return chunks


def build_shards(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    shard_count: int,
    seed: int,
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Partition the census graph into ``shard_count`` shards.

    Deterministic: the same ``(nodes, edges, shard_count, seed)`` always
    yields the identical result. Edges are enriched (per
    :func:`enrich_edges`), then both populations are sorted by ``id``
    (DB row order is not guaranteed) and independently shuffled with a
    single :class:`random.Random` instance, then :func:`even_split`.

    Returns ``{"shard_01": {"edges": [...], "nodes": [...]}, ...}`` with
    one-based, zero-padded shard keys. Every input edge and node appears
    in exactly one shard.
    """
    enriched = enrich_edges(edges, nodes)
    edges_sorted = sorted(enriched, key=lambda e: e["id"])
    nodes_sorted = sorted(nodes, key=lambda n: n["id"])

    rng = random.Random(seed)
    rng.shuffle(edges_sorted)
    rng.shuffle(nodes_sorted)

    edge_chunks = even_split(edges_sorted, shard_count)
    node_chunks = even_split(nodes_sorted, shard_count)

    width = len(str(shard_count))
    shards: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for i in range(shard_count):
        key = f"shard_{i + 1:0{width}d}"
        shards[key] = {"edges": edge_chunks[i], "nodes": node_chunks[i]}
    return shards


def assert_partition_invariants(
    shards: dict[str, dict[str, list[dict[str, Any]]]],
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
) -> None:
    """Raise ``AssertionError`` if the shards are not a clean partition.

    Checks, for both edges and nodes: every input id appears in exactly
    one shard, and no shard carries an id absent from the input. A cheap
    self-check the tool runs before writing the manifest — a corrupt
    partition must never reach a routine session.
    """
    for kind, population in (("edges", edges), ("nodes", nodes)):
        input_ids = sorted(_element_id(kind, x) for x in population)
        sharded_ids: list[str] = []
        for shard in shards.values():
            sharded_ids.extend(_element_id(kind, x) for x in shard[kind])
        if len(sharded_ids) != len(set(sharded_ids)):
            raise AssertionError(f"{kind}: an id appears in more than one shard")
        if sorted(sharded_ids) != input_ids:
            raise AssertionError(
                f"{kind}: shard union does not equal the input population"
            )


def _element_id(kind: str, element: dict[str, Any]) -> str:
    """Return the identity key for an edge or node dict."""
    return str(element["id"])


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _build_manifest(
    shards: dict[str, dict[str, list[dict[str, Any]]]],
    edges: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    shard_count: int,
    seed: int,
) -> dict[str, Any]:
    """Assemble the committed manifest dict around the shard partition."""
    return {
        "generated_by": "S-0156",
        "generated_at": emit(),
        "random_seed": seed,
        "shard_count": shard_count,
        "edge_scope": f"edge_type = '{CENSUS_EDGE_TYPE}'",
        "node_scope": "all rows of public.nodes (every status)",
        "totals": {"edges": len(edges), "nodes": len(nodes)},
        "shards": shards,
    }


def _print_summary(manifest: dict[str, Any]) -> None:
    """Print a one-block human summary of the manifest to stdout."""
    totals = manifest["totals"]
    print(
        f"[seed-qa-shard] {totals['edges']} edges + {totals['nodes']} nodes "
        f"-> {manifest['shard_count']} shards (seed={manifest['random_seed']})"
    )
    for key, shard in manifest["shards"].items():
        print(f"  {key}: {len(shard['edges'])} edges, {len(shard['nodes'])} nodes")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. See the module docstring for behavior + exit codes."""
    parser = argparse.ArgumentParser(
        description="Shard the seed graph for the QA census routine (T-SEED-QA)."
    )
    parser.add_argument(
        "--shards",
        type=int,
        default=DEFAULT_SHARD_COUNT,
        help=f"shard count (default {DEFAULT_SHARD_COUNT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SHARD_RANDOM_SEED,
        help=f"integer RNG seed (default {SHARD_RANDOM_SEED})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="manifest output path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="read the graph and compute shards, but write nothing",
    )
    args = parser.parse_args(argv)

    if args.shards < 1:
        print("[seed-qa-shard] --shards must be >= 1", file=sys.stderr)
        return 2

    load_dotenv_walk_up()
    conn_str = os.environ.get(SUPABASE_DB_URL_ENV)
    if not conn_str:
        print(
            f"[seed-qa-shard] {SUPABASE_DB_URL_ENV} unresolved — cannot read "
            "the live graph. Set it or run from a tree with a reachable .env.",
            file=sys.stderr,
        )
        return 2

    try:
        nodes, edges = read_graph(conn_str)
    except ImportError:
        print(
            "[seed-qa-shard] psycopg unavailable — install it in the venv "
            "(uv sync) and re-run.",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:  # noqa: BLE001  (psycopg connect/query errors)
        print(f"[seed-qa-shard] DB read failed: {exc}", file=sys.stderr)
        return 2

    shards = build_shards(nodes, edges, args.shards, args.seed)
    assert_partition_invariants(shards, edges, nodes)
    manifest = _build_manifest(shards, edges, nodes, args.shards, args.seed)

    _print_summary(manifest)

    if args.dry_run:
        print("[seed-qa-shard] dry-run — manifest not written")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, default=str, indent=2, sort_keys=True) + "\n"
    )
    print(f"[seed-qa-shard] manifest written: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
