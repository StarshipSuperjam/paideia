"""Tests for seed_qa_shard.py — the seed-graph QA census sharding tool.

Coverage per the S-0156 approved plan:
- even_split: near-equal sizes, full coverage, n=1, n > len, empty, n < 1 raises
- enrich_edges: endpoint label/domain attached, missing endpoint -> None, input not mutated
- build_shards: determinism (same seed -> identical), different seed -> different order,
  clean partition (every element exactly once), enrichment present, shard-key format
- assert_partition_invariants: passes clean, raises on duplicate / missing
- main: success writes manifest, dry-run writes nothing, missing env / ImportError /
  DB error / bad --shards all exit 2

Synthetic fixture graph only — generic concept_* ids, no real content.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seed_qa_shard import (  # noqa: E402
    assert_partition_invariants,
    build_shards,
    enrich_edges,
    even_split,
    main,
    read_graph,
)


# ---------------------------------------------------------------------------
# Fixtures — a small synthetic graph
# ---------------------------------------------------------------------------


def _make_nodes(count: int) -> list[dict[str, Any]]:
    """Return ``count`` synthetic node rows with stable ids."""
    return [
        {
            "id": f"concept_{i:02d}",
            "label": f"Concept {i:02d}",
            "domain": ["domain_x"] if i % 2 == 0 else ["domain_y"],
            "summary": f"Synthetic summary for concept {i:02d}.",
            "teaching_notes": f"Synthetic note {i:02d}." if i % 3 else None,
            "confidence_level": "INTERPRETED",
            "status": "active",
        }
        for i in range(count)
    ]


def _make_edges(count: int, node_count: int) -> list[dict[str, Any]]:
    """Return ``count`` synthetic edge rows wiring consecutive nodes."""
    return [
        {
            "id": f"edge-{i:04d}",
            "source_id": f"concept_{i % node_count:02d}",
            "target_id": f"concept_{(i + 1) % node_count:02d}",
            "edge_type": "pedagogical_prerequisite",
            "weight": 1.0,
            "confidence": 1.0,
            "evidence": f"Synthetic evidence {i}." if i % 2 else None,
        }
        for i in range(count)
    ]


# ---------------------------------------------------------------------------
# even_split
# ---------------------------------------------------------------------------


def test_even_split_sizes_differ_by_at_most_one() -> None:
    chunks = even_split(list(range(100)), 19)
    sizes = [len(c) for c in chunks]
    assert max(sizes) - min(sizes) <= 1
    assert sum(sizes) == 100
    assert len(chunks) == 19


def test_even_split_full_coverage_no_overlap() -> None:
    items = list(range(57))
    chunks = even_split(items, 8)
    flat = [x for c in chunks for x in c]
    assert sorted(flat) == items


def test_even_split_n_equals_one() -> None:
    chunks = even_split([1, 2, 3], 1)
    assert chunks == [[1, 2, 3]]


def test_even_split_n_greater_than_len_pads_empty() -> None:
    chunks = even_split([1, 2], 5)
    # First 2 chunks get one element each; the trailing 3 are empty.
    assert chunks == [[1], [2], [], [], []]


def test_even_split_empty_list() -> None:
    chunks = even_split([], 4)
    assert chunks == [[], [], [], []]


def test_even_split_rejects_zero_shards() -> None:
    with pytest.raises(ValueError):
        even_split([1, 2, 3], 0)


# ---------------------------------------------------------------------------
# enrich_edges
# ---------------------------------------------------------------------------


def test_enrich_edges_attaches_endpoint_label_and_domain() -> None:
    nodes = _make_nodes(4)
    edges = _make_edges(2, 4)
    enriched = enrich_edges(edges, nodes)
    e0 = enriched[0]
    assert e0["source_id"] == "concept_00"
    assert e0["source_label"] == "Concept 00"
    assert e0["source_domain"] == ["domain_x"]
    assert e0["target_label"] == "Concept 01"
    assert e0["target_domain"] == ["domain_y"]


def test_enrich_edges_missing_endpoint_yields_none() -> None:
    nodes = _make_nodes(2)
    dangling = [
        {
            "id": "edge-9999",
            "source_id": "concept_00",
            "target_id": "concept_absent",
            "edge_type": "pedagogical_prerequisite",
            "weight": 1.0,
            "confidence": 1.0,
            "evidence": None,
        }
    ]
    enriched = enrich_edges(dangling, nodes)
    assert enriched[0]["source_label"] == "Concept 00"
    assert enriched[0]["target_label"] is None
    assert enriched[0]["target_domain"] is None


def test_enrich_edges_does_not_mutate_input() -> None:
    nodes = _make_nodes(4)
    edges = _make_edges(2, 4)
    enrich_edges(edges, nodes)
    assert "source_label" not in edges[0]


# ---------------------------------------------------------------------------
# build_shards
# ---------------------------------------------------------------------------


def test_build_shards_is_deterministic() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    a = build_shards(nodes, edges, 19, seed=20260514)
    b = build_shards(nodes, edges, 19, seed=20260514)
    assert a == b


def test_build_shards_different_seed_changes_assignment() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    a = build_shards(nodes, edges, 19, seed=1)
    b = build_shards(nodes, edges, 19, seed=2)
    assert a != b


def test_build_shards_is_a_clean_partition() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    shards = build_shards(nodes, edges, 19, seed=20260514)
    edge_ids = [e["id"] for s in shards.values() for e in s["edges"]]
    node_ids = [n["id"] for s in shards.values() for n in s["nodes"]]
    assert sorted(edge_ids) == sorted(e["id"] for e in edges)
    assert sorted(node_ids) == sorted(n["id"] for n in nodes)
    assert len(edge_ids) == len(set(edge_ids))
    assert len(node_ids) == len(set(node_ids))


def test_build_shards_input_order_independence() -> None:
    """DB row order must not affect the partition — only id + seed do."""
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    shuffled_nodes = list(reversed(nodes))
    shuffled_edges = list(reversed(edges))
    a = build_shards(nodes, edges, 19, seed=20260514)
    b = build_shards(shuffled_nodes, shuffled_edges, 19, seed=20260514)
    assert a == b


def test_build_shards_embeds_edge_enrichment() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    shards = build_shards(nodes, edges, 19, seed=20260514)
    sample_edge = next(e for s in shards.values() for e in s["edges"])
    assert "source_label" in sample_edge
    assert "target_label" in sample_edge


def test_build_shards_key_format_zero_padded() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    shards = build_shards(nodes, edges, 19, seed=20260514)
    assert "shard_01" in shards
    assert "shard_19" in shards
    assert len(shards) == 19


def test_build_shards_near_equal_shard_sizes() -> None:
    nodes = _make_nodes(380)
    edges = _make_edges(516, 380)
    shards = build_shards(nodes, edges, 19, seed=20260514)
    edge_sizes = [len(s["edges"]) for s in shards.values()]
    node_sizes = [len(s["nodes"]) for s in shards.values()]
    assert max(edge_sizes) - min(edge_sizes) <= 1
    assert max(node_sizes) - min(node_sizes) <= 1
    assert set(node_sizes) == {20}  # 380 / 19 exactly


# ---------------------------------------------------------------------------
# assert_partition_invariants
# ---------------------------------------------------------------------------


def test_assert_partition_invariants_passes_clean() -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    shards = build_shards(nodes, edges, 19, seed=20260514)
    assert_partition_invariants(shards, enrich_edges(edges, nodes), nodes)


def test_assert_partition_invariants_raises_on_duplicate() -> None:
    nodes = _make_nodes(4)
    edges = _make_edges(4, 4)
    enriched = enrich_edges(edges, nodes)
    bad = {
        "shard_1": {"edges": [enriched[0]], "nodes": [nodes[0]]},
        "shard_2": {"edges": [enriched[0]], "nodes": [nodes[1]]},  # dup edge
    }
    with pytest.raises(AssertionError):
        assert_partition_invariants(bad, enriched, nodes)


def test_assert_partition_invariants_raises_on_missing() -> None:
    nodes = _make_nodes(4)
    edges = _make_edges(4, 4)
    enriched = enrich_edges(edges, nodes)
    bad = {
        "shard_1": {"edges": [enriched[0]], "nodes": [nodes[0]]},
        # edges 1-3 and nodes 1-3 dropped
    }
    with pytest.raises(AssertionError):
        assert_partition_invariants(bad, enriched, nodes)


# ---------------------------------------------------------------------------
# read_graph — psycopg stub
# ---------------------------------------------------------------------------


class _FakeCursor:
    def __init__(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> None:
        self._nodes = nodes
        self._edges = edges
        self._pending: list[dict[str, Any]] = []

    def __enter__(self) -> "_FakeCursor":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> None:
        self._pending = self._nodes if "FROM public.nodes" in sql else self._edges

    def fetchall(self) -> list[dict[str, Any]]:
        return self._pending


class _FakeConn:
    def __init__(
        self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]
    ) -> None:
        self._cursor = _FakeCursor(nodes, edges)

    def __enter__(self) -> "_FakeConn":
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def cursor(self, **kwargs: Any) -> _FakeCursor:
        return self._cursor


def test_read_graph_coerces_edge_id_to_str(monkeypatch: pytest.MonkeyPatch) -> None:
    import uuid

    raw_edges = [
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "source_id": "concept_00",
            "target_id": "concept_01",
            "edge_type": "pedagogical_prerequisite",
            "weight": 1.0,
            "confidence": 1.0,
            "evidence": None,
        }
    ]
    fake_psycopg = type(
        "psycopg",
        (),
        {"connect": staticmethod(lambda cs: _FakeConn(_make_nodes(2), raw_edges))},
    )
    fake_rows = type("rows", (), {"dict_row": object()})
    monkeypatch.setitem(sys.modules, "psycopg", fake_psycopg)
    monkeypatch.setitem(sys.modules, "psycopg.rows", fake_rows)
    nodes, edges = read_graph("postgresql://stub")
    assert len(nodes) == 2
    assert edges[0]["id"] == "00000000-0000-0000-0000-000000000001"
    assert isinstance(edges[0]["id"], str)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_writes_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    nodes = _make_nodes(40)
    edges = _make_edges(55, 40)
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    monkeypatch.setattr("seed_qa_shard.read_graph", lambda cs: (nodes, edges))
    out = tmp_path / "shards.json"
    rc = main(["--output", str(out), "--shards", "19"])
    assert rc == 0
    manifest = json.loads(out.read_text())
    assert manifest["shard_count"] == 19
    assert manifest["totals"] == {"edges": 55, "nodes": 40}
    assert manifest["edge_scope"] == "edge_type = 'pedagogical_prerequisite'"
    assert len(manifest["shards"]) == 19
    sharded_edges = [e["id"] for s in manifest["shards"].values() for e in s["edges"]]
    assert sorted(sharded_edges) == sorted(e["id"] for e in edges)


def test_main_dry_run_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    monkeypatch.setattr(
        "seed_qa_shard.read_graph",
        lambda cs: (_make_nodes(40), _make_edges(55, 40)),
    )
    out = tmp_path / "shards.json"
    rc = main(["--output", str(out), "--dry-run"])
    assert rc == 0
    assert not out.exists()


def test_main_missing_env_exits_2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_DB_URL", raising=False)
    # Neutralize the walk-up loader so a real .env cannot repopulate the env.
    monkeypatch.setattr("seed_qa_shard.load_dotenv_walk_up", lambda: {})
    assert main([]) == 2


def test_main_import_error_exits_2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

    def _raise_import() -> tuple[list[Any], list[Any]]:
        raise ImportError("no psycopg")

    monkeypatch.setattr("seed_qa_shard.read_graph", lambda cs: _raise_import())
    assert main([]) == 2


def test_main_db_error_exits_2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")

    def _raise_db() -> tuple[list[Any], list[Any]]:
        raise RuntimeError("connection refused")

    monkeypatch.setattr("seed_qa_shard.read_graph", lambda cs: _raise_db())
    assert main([]) == 2


def test_main_rejects_zero_shards(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPABASE_DB_URL", "postgresql://stub")
    assert main(["--shards", "0"]) == 2
