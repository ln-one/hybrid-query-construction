import random

from hybrid_query_construction.fusion import complete_wrrf, fixed_top_l_wrrf
from hybrid_query_construction.replay import replay_complete_wrrf


def test_standard_rrf_formula_and_tie_rule() -> None:
    dense = ["b", "a", "c"]
    sparse = ["a", "b"]
    assert complete_wrrf((dense, sparse), top_k=3, constant=60) == ["a", "b", "c"]


def test_fixed_top_l_can_differ_from_complete_target() -> None:
    dense = ["a", "b", "c", "d", "e"]
    sparse = ["b", "c", "a", "d", "e"]
    assert fixed_top_l_wrrf((dense, sparse), 1, top_k=2, constant=2) != complete_wrrf(
        (dense, sparse), top_k=2, constant=2
    )


def test_replay_matches_complete_fusion_over_random_rankings() -> None:
    for seed in range(30):
        random.seed(seed)
        documents = [f"d{index:03d}" for index in range(80)]
        dense = random.sample(documents, len(documents))
        sparse = random.sample(documents, random.randint(20, len(documents)))
        replay = replay_complete_wrrf(dense, sparse, top_k=20, constant=60)
        assert list(replay.ordered_top_k) == complete_wrrf(
            (dense, sparse), top_k=20, constant=60
        )
        assert replay.dense_depth <= len(dense)
        assert replay.sparse_depth <= len(sparse)
