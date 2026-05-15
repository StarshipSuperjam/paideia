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
    """End-to-end: SQLite extract, delete, recreate, re-add — counts + docs + metadata round-trip.

    S-0187 note: the rebuild intentionally adds
    ``hnsw:sync_threshold=REBUILD_SYNC_THRESHOLD`` to the metadata at
    create-collection time per the ADR 0079 amendment, then raises
    sync_threshold on the configuration channel to STEADY_STATE_SYNC_THRESHOLD
    post-adds. So the metadata is NOT byte-identical pre/post; only
    user-facing fields (``hnsw:space``) round-trip unchanged. The
    test asserts that subset explicitly.
    """
    import mempalace_rebuild_hnsw as mrh  # noqa: PLC0415

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
    # User-facing metadata round-trips: hnsw:space and any
    # non-amendment-touched keys (any future addition to _HNSW_BLOAT_GUARD
    # would need to be added here).
    post_metadata = dict(post.metadata or {})
    for key, expected in pre_metadata.items():
        if key == "hnsw:sync_threshold":
            # Intentionally overridden by the S-0187 amendment.
            continue
        assert post_metadata.get(key) == expected, (
            f"User-facing metadata key {key!r} must round-trip through "
            f"rebuild unchanged. pre={expected!r}, post={post_metadata.get(key)!r}"
        )
    # The amendment's effect: sync_threshold on metadata reflects the
    # rebuild-time value (creation-time advisory); configuration channel
    # reflects the post-modify steady-state. ADR 0079 explicitly notes
    # the metadata channel is creation-time advisory and does NOT
    # reflect post-modify updates.
    assert post_metadata.get("hnsw:sync_threshold") == mrh.REBUILD_SYNC_THRESHOLD, (
        f"S-0187: post-rebuild metadata.hnsw:sync_threshold reflects "
        f"the creation-time override ({mrh.REBUILD_SYNC_THRESHOLD}). "
        f"Got {post_metadata.get('hnsw:sync_threshold')!r}."
    )

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


def test_rebuild_sets_steady_state_sync_threshold_post_adds(tmp_path: Path) -> None:
    """S-0187 amendment of ADR 0079: post-rebuild sync_threshold is the
    project steady-state (100), not the rebuild-time floor (3) nor
    mempalace's inherited _HNSW_BLOAT_GUARD default (50_000).

    The amendment overrides ``hnsw:sync_threshold = REBUILD_SYNC_THRESHOLD``
    at create-collection time so chromadb's ``_apply_batch`` persist
    fires after each pagination batch — the rebuild's HNSW segment
    state actually lands on disk. Post-adds, the tool raises to
    ``STEADY_STATE_SYNC_THRESHOLD`` via ``collection.modify(configuration=
    {'hnsw': {'sync_threshold': N}})`` (chromadb 1.5.x's authoritative
    runtime channel per ADR 0079).
    """
    import mempalace_rebuild_hnsw as mrh  # noqa: PLC0415

    palace_dir = tmp_path / ".mempalace" / "palace"
    client = _seed_palace(palace_dir, drawer_count=15, with_metadata=True)

    summary = mrh.rebuild_collection(
        client, palace_dir, "test_collection", batch_size=5
    )
    assert summary.get("exit_code") == 0, summary
    assert summary.get("final_sync_threshold") == mrh.STEADY_STATE_SYNC_THRESHOLD
    assert "threshold_raise_warning" not in summary, summary

    # Verify post-rebuild via fresh client read of the configuration
    # channel (the authoritative source per ADR 0079).
    import chromadb  # noqa: PLC0415

    del client
    client2 = chromadb.PersistentClient(path=str(palace_dir))
    post = client2.get_collection("test_collection")
    config = getattr(post, "configuration", None)
    assert config is not None, "chromadb 1.5.x exposes configuration"
    hnsw = (
        config.get("hnsw")
        if isinstance(config, dict)
        else getattr(config, "hnsw", None)
    )
    assert hnsw is not None, (
        f"configuration.hnsw missing on rebuilt collection; cfg={config}"
    )
    threshold = (
        hnsw.get("sync_threshold")
        if isinstance(hnsw, dict)
        else getattr(hnsw, "sync_threshold", None)
    )
    assert threshold == mrh.STEADY_STATE_SYNC_THRESHOLD, (
        f"S-0187 amendment: post-rebuild configuration.hnsw.sync_threshold "
        f"must equal {mrh.STEADY_STATE_SYNC_THRESHOLD} (project steady-state). "
        f"Got {threshold!r}. The rebuild's post-adds collection.modify "
        f"step is either missing or silently broken."
    )


def test_rebuild_uses_rebuild_threshold_at_create_collection(tmp_path: Path) -> None:
    """S-0187 amendment of ADR 0079: at create-collection time, the
    rebuild MUST override ``hnsw:sync_threshold`` to a low value so
    chromadb's ``_persist()`` fires during the rebuild's adds. The
    raise-to-steady-state happens AFTER all adds complete.

    This test intercepts the create-collection call to assert the
    overridden metadata reaches chromadb, regardless of what the
    final-state value is (covered by the sibling test above).
    """
    import mempalace_rebuild_hnsw as mrh  # noqa: PLC0415

    palace_dir = tmp_path / ".mempalace" / "palace"
    palace_dir.mkdir(parents=True, exist_ok=True)
    chromadb = pytest.importorskip("chromadb")
    # Seed an initial collection with mempalace's default
    # _HNSW_BLOAT_GUARD inherited via metadata. We use a fresh
    # PersistentClient and emulate mempalace's metadata via the
    # _HNSW_BLOAT_GUARD constants.
    client = chromadb.PersistentClient(path=str(palace_dir))
    col = client.get_or_create_collection(
        name="test_collection",
        metadata={
            "hnsw:space": "cosine",
            "hnsw:batch_size": 50000,
            "hnsw:sync_threshold": 50000,
        },
    )
    col.add(
        ids=["d0", "d1", "d2"],
        documents=["a", "b", "c"],
        embeddings=[[0.0, 1.0], [0.1, 0.9], [0.2, 0.8]],
        metadatas=[{"i": 0}, {"i": 1}, {"i": 2}],
    )
    del col

    captured_create_metadata: dict[str, Any] = {}
    original_create = client.create_collection

    def _instrumented_create(*args: Any, **kwargs: Any) -> Any:
        # Capture the metadata dict the rebuild_collection function
        # passes; assert REBUILD_SYNC_THRESHOLD is in there.
        captured_create_metadata.update(kwargs.get("metadata", {}))
        return original_create(*args, **kwargs)

    # Wrap the client's create_collection in a thin instrumentation
    # closure. The wrapper preserves the original behavior.
    client.create_collection = _instrumented_create

    summary = mrh.rebuild_collection(
        client, palace_dir, "test_collection", batch_size=2
    )
    assert summary.get("exit_code") == 0, summary
    assert (
        captured_create_metadata.get("hnsw:sync_threshold")
        == mrh.REBUILD_SYNC_THRESHOLD
    ), (
        f"S-0187: rebuild_collection must override hnsw:sync_threshold "
        f"to {mrh.REBUILD_SYNC_THRESHOLD} at create-collection time so "
        f"chromadb's _persist() fires during the rebuild's adds. "
        f"Captured metadata: {captured_create_metadata!r}"
    )
    # Sibling assertion: hnsw:batch_size left at the inherited 50_000
    # — that's the anti-bloat protection PR #344 designed; the rebuild
    # should not touch it.
    assert captured_create_metadata.get("hnsw:batch_size") == 50000, (
        f"S-0187: rebuild_collection must NOT override hnsw:batch_size "
        f"(it's the anti-bloat protection from PR #344). Captured: "
        f"{captured_create_metadata!r}"
    )


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
