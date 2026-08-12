from pathlib import Path

import pytest

from hybrid_query_construction.storage import RankingStore


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
