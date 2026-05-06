"""Tests for engine/tools/mempalace_rebuild_hnsw.py.

Exercises the rebuild against a synthetic chromadb palace under
``tmp_path``. Avoids touching the user's real palace at
``~/.mempalace/``. ChromaDB is required (the underlying API is the
unit under test); tests skip cleanly if it's unavailable.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from mempalace_rebuild_hnsw import rebuild_collection  # noqa: E402


def _seed_palace(palace_dir: Path, *, drawer_count: int, with_metadata: bool) -> Any:
    """Create a chromadb palace with ``drawer_count`` drawers; return client."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection(
        name="test_collection",
        metadata={"hnsw:space": "cosine"} if with_metadata else None,
    )
    ids = [f"d{i}" for i in range(drawer_count)]
    documents = [f"document number {i}" for i in range(drawer_count)]
    embeddings = [[0.1 * (i + j) for j in range(8)] for i in range(drawer_count)]
    metadatas = [{"index": i} for i in range(drawer_count)]
    col.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
    return client


def test_rebuild_against_synthetic_palace_preserves_count_and_metadata(
    tmp_path: Path,
) -> None:
    """End-to-end: SQLite extract, delete, recreate, re-add — counts + docs + metadata round-trip."""
    palace_dir = tmp_path / ".mempalace" / "palace"
    client = _seed_palace(palace_dir, drawer_count=20, with_metadata=True)

    pre = client.get_collection("test_collection")
    pre_count = pre.count()
    pre_metadata = dict(pre.metadata or {})
    assert pre_count == 20
    del pre

    summary = rebuild_collection(client, palace_dir, "test_collection", batch_size=5)
    assert summary.get("exit_code") == 0, summary
    assert summary["expected_drawers"] == 20
    assert summary["extracted_drawers"] == 20
    assert summary["final_drawers"] == 20

    post = client.get_collection("test_collection")
    assert post.count() == 20
    assert dict(post.metadata or {}) == pre_metadata

    # Documents and per-drawer metadata round-trip via SQLite extraction +
    # chromadb re-embedding. (Embeddings themselves are recomputed by
    # chromadb's default embedding function — not byte-identical to seed.)
    sample = post.get(ids=["d5"], include=["documents", "metadatas"])
    assert sample["documents"][0] == "document number 5"
    assert sample["metadatas"][0] == {"index": 5}


def test_rebuild_dry_run_does_not_mutate_palace(tmp_path: Path) -> None:
    """--dry-run reads + reports but performs no destructive actions."""
    chromadb = pytest.importorskip("chromadb")
    palace_dir = tmp_path / ".mempalace" / "palace"
    client = _seed_palace(palace_dir, drawer_count=10, with_metadata=True)

    pre = client.get_collection("test_collection")
    pre_drawer_ids = sorted(pre.get(include=[])["ids"])
    del pre

    summary = rebuild_collection(
        client, palace_dir, "test_collection", batch_size=5, dry_run=True
    )
    assert summary.get("exit_code") == 0
    assert summary.get("dry_run") is True

    # Reopen client; verify nothing changed structurally.
    del client
    client2 = chromadb.PersistentClient(path=str(palace_dir))
    post = client2.get_collection("test_collection")
    assert post.count() == 10
    post_drawer_ids = sorted(post.get(include=[])["ids"])
    assert post_drawer_ids == pre_drawer_ids


class _FakeCollection:
    """Minimal Collection-like stub for the non-default-embedding test.

    Real chromadb 1.5.x exposes ``configuration_json`` as a read-only
    property; the safety branch can't be exercised against a real
    Collection without forking the upstream API. This stub lets the
    test verify the rebuild_collection function reads the field and
    refuses correctly when it isn't ``"default"``.
    """

    def __init__(self, name: str, embed_fn_name: str) -> None:
        self.name = name
        self.metadata = {"hnsw:space": "cosine"}
        self.configuration_json = {
            "embedding_function": {"type": "known", "name": embed_fn_name}
        }

    def count(self) -> int:
        return 3


class _FakeClient:
    def __init__(self, embed_fn_name: str) -> None:
        self._col = _FakeCollection("test_collection", embed_fn_name)

    def get_collection(self, name: str) -> _FakeCollection:
        if name != self._col.name:
            raise KeyError(name)
        return self._col


def test_rebuild_refuses_non_default_embedding_function(tmp_path: Path) -> None:
    """Per Issue #1255, non-default embedding_function is out-of-scope.

    ChromaDB's ``configuration_json.embedding_function.name`` defaults to
    ``"default"``. The rebuild tool must refuse to proceed if the
    collection uses something else. Uses a minimal fake client because
    ``configuration_json`` is a read-only property on real chromadb
    Collections.
    """
    fake_client = _FakeClient(embed_fn_name="multilingual-e5-base")

    summary = rebuild_collection(fake_client, tmp_path, "test_collection")
    assert summary.get("exit_code") == 4
    assert "non-default embedding function" in summary.get("error", "")
