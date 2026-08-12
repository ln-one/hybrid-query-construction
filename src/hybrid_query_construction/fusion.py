from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence


def rank_scores(scores: Mapping[str, float]) -> list[str]:
    return sorted(scores, key=lambda document_id: (-scores[document_id], document_id))


def wrrf_contribution(one_based_rank: int, constant: int = 60) -> float:
    if one_based_rank <= 0 or constant < 0:
        raise ValueError("rank must be positive and constant nonnegative")
    return 1.0 / (constant + one_based_rank)


def complete_wrrf(
    rankings: Sequence[Sequence[str]],
    *,
    top_k: int = 20,
    constant: int = 60,
    weights: Sequence[float] | None = None,
) -> list[str]:
    if weights is None:
        weights = [1.0] * len(rankings)
    if len(rankings) != len(weights):
        raise ValueError("rankings and weights must have equal length")
    scores: defaultdict[str, float] = defaultdict(float)
    for ranking, weight in zip(rankings, weights, strict=True):
        for rank, document_id in enumerate(ranking, start=1):
            scores[document_id] += weight * wrrf_contribution(rank, constant)
    return sorted(scores, key=lambda document_id: (-scores[document_id], document_id))[:top_k]


def fixed_top_l_wrrf(
    rankings: Sequence[Sequence[str]],
    top_l: int,
    *,
    top_k: int = 20,
    constant: int = 60,
) -> list[str]:
    if top_l <= 0:
        raise ValueError("top_l must be positive")
    return complete_wrrf(
        [ranking[:top_l] for ranking in rankings], top_k=top_k, constant=constant
    )
