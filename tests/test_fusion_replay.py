import random

from hybrid_query_construction.fusion import complete_wrrf, fixed_top_l_wrrf
from hybrid_query_construction.replay import _precedes, replay_complete_wrrf


def _brute_replay(
    dense: list[str], sparse: list[str], top_k: int, constant: int
) -> tuple[int, int]:
    rankings = (dense, sparse)
    positions = [0, 0]
    observed: dict[str, list[float | None]] = {}
    universe = set(dense) | set(sparse)
    while True:
        if len(observed) >= top_k:
            next_bounds = tuple(
                0.0
                if positions[channel] == len(rankings[channel])
                else 1.0 / (constant + positions[channel] + 1)
                for channel in range(2)
            )
            rows = []
            for document_id, values in observed.items():
                lower = sum(value or 0.0 for value in values)
                upper = lower + sum(
                    next_bounds[channel]
                    for channel, value in enumerate(values)
                    if value is None
                )
                rows.append((document_id, lower, upper))
            rows.sort(key=lambda row: (-row[1], row[0]))
            winners = rows[:top_k]
            ordered = all(
                _precedes(left[1], left[0], right[2], right[0])
                for left_index, left in enumerate(winners)
                for right in winners[left_index + 1 :]
            )
            boundary = winners[-1]
            outsiders = all(
                _precedes(boundary[1], boundary[0], row[2], row[0]) for row in rows[top_k:]
            )
            unseen = len(observed) == len(universe) or boundary[1] > sum(next_bounds)
            if ordered and outsiders and unseen:
                return positions[0], positions[1]
        available = [
            channel for channel in range(2) if positions[channel] < len(rankings[channel])
        ]
        channel = min(
            available,
            key=lambda item: (-(1.0 / (constant + positions[item] + 1)), item),
        )
        rank = positions[channel] + 1
        document_id = rankings[channel][positions[channel]]
        observed.setdefault(document_id, [None, None])[channel] = 1.0 / (constant + rank)
        positions[channel] += 1


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
    for constant in (2, 20, 60, 100):
        for top_k in (1, 5, 20):
            for seed in range(20):
                generator = random.Random(constant * 10_000 + top_k * 100 + seed)
                documents = [f"d{index:03d}" for index in range(80)]
                dense = generator.sample(documents, len(documents))
                sparse = generator.sample(documents, generator.randint(top_k, len(documents)))
                replay = replay_complete_wrrf(dense, sparse, top_k=top_k, constant=constant)
                assert list(replay.ordered_top_k) == complete_wrrf(
                    (dense, sparse), top_k=top_k, constant=constant
                )
                assert replay.dense_depth <= len(dense)
                assert replay.sparse_depth <= len(sparse)
                assert (replay.dense_depth, replay.sparse_depth) == _brute_replay(
                    dense, sparse, top_k, constant
                )
