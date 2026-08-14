import sqlite3
from pathlib import Path

import pytest

from hybrid_query_construction.storage import RankingStore, ranking_store_digest


def test_ranking_store_round_trip_and_hash_check(tmp_path: Path) -> None:
    path = tmp_path / "rankings.sqlite3"
    with RankingStore(path, "fixture", ["d0", "d1", "d2"]) as store:
        digest = store.put(
            query_id="q0",
            draw_id=1,
            track="controlled",
            channel="dense_residual",
            reference_count=5,
            ranking=["d2", "d0", "d1"],
            support=3,
            fallback=False,
            generation_sha256="a" * 64,
        )
        result = store.get(
            query_id="q0",
            draw_id=1,
            track="controlled",
            channel="dense_residual",
            reference_count=5,
        )
        assert result.ranking == ("d2", "d0", "d1")
        assert result.ranking_sha256 == digest
        assert list(store.keys()) == [("q0", 1, "controlled", "dense_residual", 5)]
    assert RankingStore.load_document_ids(path) == ("d0", "d1", "d2")


def test_ranking_store_rejects_unknown_documents(tmp_path: Path) -> None:
    with RankingStore(tmp_path / "rankings.sqlite3", "fixture", ["d0"]) as store:
        with pytest.raises(ValueError, match="unknown document"):
            store.put(
                query_id="q0",
                draw_id=0,
                track="base",
                channel="dense_original",
                reference_count=0,
                ranking=["other"],
                support=1,
                fallback=False,
                generation_sha256="0" * 64,
            )


def test_ranking_store_digest_ignores_sqlite_layout(tmp_path: Path) -> None:
    path = tmp_path / "rankings.sqlite3"
    with RankingStore(path, "fixture", ["d0", "d1"]) as store:
        store.put(
            query_id="q0",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
            ranking=["d1", "d0"],
            support=2,
            fallback=False,
            generation_sha256="0" * 64,
        )
    before = ranking_store_digest(path)
    with sqlite3.connect(path) as connection:
        connection.execute("VACUUM")
    assert ranking_store_digest(path) == before


def test_copy_verified_rankings_preserves_itemwise_order_and_hash(tmp_path: Path) -> None:
    source_path = tmp_path / "source.sqlite3"
    destination_path = tmp_path / "destination.sqlite3"
    documents = ["d0", "d1", "d2"]
    with RankingStore(source_path, "fixture", documents) as source:
        source.put(
            query_id="q0",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
            ranking=["d2", "d0", "d1"],
            support=3,
            fallback=False,
            generation_sha256="0" * 64,
        )
        source.put(
            query_id="q0",
            draw_id=1,
            track="controlled",
            channel="sparse_anchor",
            reference_count=5,
            ranking=["d1", "d2"],
            support=2,
            fallback=False,
            generation_sha256="a" * 64,
        )

    with RankingStore(destination_path, "fixture", documents) as destination:
        evidence = destination.copy_verified_from(
            source_path, select=lambda key: key[2] == "base"
        )
        copied = destination.get(
            query_id="q0",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
        )
    with RankingStore(source_path, "fixture", documents) as source:
        original = source.get(
            query_id="q0",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
        )

    assert evidence.selected == evidence.inserted == evidence.ordinal_rows_verified == 1
    assert evidence.already_present == 0
    assert copied.ranking == original.ranking
    assert copied.ranking_sha256 == original.ranking_sha256


def test_copy_verified_rankings_rejects_different_document_order(tmp_path: Path) -> None:
    source_path = tmp_path / "source.sqlite3"
    with RankingStore(source_path, "fixture", ["d0", "d1"]) as source:
        source.put(
            query_id="q0",
            draw_id=0,
            track="base",
            channel="dense_original",
            reference_count=0,
            ranking=["d0", "d1"],
            support=2,
            fallback=False,
            generation_sha256="0" * 64,
        )
    with RankingStore(tmp_path / "destination.sqlite3", "fixture", ["d1", "d0"]) as store:
        with pytest.raises(RuntimeError, match="different documents"):
            store.copy_verified_from(source_path, select=lambda _key: True)
