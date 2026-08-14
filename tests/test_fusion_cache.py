import sqlite3
from pathlib import Path

import pytest

from hybrid_query_construction.fusion_cache import ALGORITHM, FusionReplayCache
from hybrid_query_construction.io import sha256_bytes


def test_fusion_replay_cache_matches_uncached_result(tmp_path: Path) -> None:
    path = tmp_path / "fusion.sqlite3"
    dense = ("d0", "d1", "d2", "d3")
    sparse = ("d2", "d1", "d3", "d0")
    dense_hash = sha256_bytes(b"dense")
    sparse_hash = sha256_bytes(b"sparse")
    with FusionReplayCache(path) as cache:
        first = cache.get_or_compute(
            dense,
            sparse,
            dense_sha256=dense_hash,
            sparse_sha256=sparse_hash,
            top_k=2,
            constant=60,
        )
        second = cache.get_or_compute(
            dense,
            sparse,
            dense_sha256=dense_hash,
            sparse_sha256=sparse_hash,
            top_k=2,
            constant=60,
        )
        assert cache.misses == cache.hits == 1

    assert not first.cache_hit
    assert second.cache_hit
    assert first.ordered_top_k == second.ordered_top_k
    assert first.dense_depth == second.dense_depth
    assert first.sparse_depth == second.sparse_depth
    assert first.trace_sha256 == second.trace_sha256


def test_fusion_replay_cache_rejects_corrupt_payload(tmp_path: Path) -> None:
    path = tmp_path / "fusion.sqlite3"
    dense_hash = sha256_bytes(b"dense")
    sparse_hash = sha256_bytes(b"sparse")
    with FusionReplayCache(path) as cache:
        cache.get_or_compute(
            ("d0", "d1"),
            ("d1", "d0"),
            dense_sha256=dense_hash,
            sparse_sha256=sparse_hash,
            top_k=1,
            constant=60,
        )
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE fusion_replay SET payload='{}' WHERE algorithm=?", (ALGORITHM,)
        )
    with FusionReplayCache(path) as cache:
        with pytest.raises(RuntimeError, match="payload hash mismatch"):
            cache.get_or_compute(
                ("d0", "d1"),
                ("d1", "d0"),
                dense_sha256=dense_hash,
                sparse_sha256=sparse_hash,
                top_k=1,
                constant=60,
            )
