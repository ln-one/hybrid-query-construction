from __future__ import annotations

from collections.abc import Sequence

from .fusion import complete_wrrf, wrrf_contribution
from .models import ReplayResult


def _precedes(score_a: float, id_a: str, score_b: float, id_b: str) -> bool:
    return score_a > score_b or (score_a == score_b and id_a < id_b)


def _certified_top_k(
    observed: dict[str, list[float | None]],
    positions: tuple[int, int],
    lengths: tuple[int, int],
    universe_size: int,
    top_k: int,
    constant: int,
) -> list[str] | None:
    if len(observed) < top_k:
        return None
    exhausted = (positions[0] == lengths[0], positions[1] == lengths[1])
    next_bounds = tuple(
        0.0 if exhausted[index] else wrrf_contribution(positions[index] + 1, constant)
        for index in range(2)
    )
    rows: list[tuple[str, float, float]] = []
    for document_id, contributions in observed.items():
        lower = sum(value or 0.0 for value in contributions)
        upper = lower + sum(
            next_bounds[index]
            for index, value in enumerate(contributions)
            if value is None and not exhausted[index]
        )
        rows.append((document_id, lower, upper))
    rows.sort(key=lambda row: (-row[1], row[0]))
    winners = rows[:top_k]
    outsiders = rows[top_k:]

    for left_index, left in enumerate(winners):
        for right in winners[left_index + 1 :]:
            if not _precedes(left[1], left[0], right[2], right[0]):
                return None
    boundary = winners[-1]
    for outsider in outsiders:
        if not _precedes(boundary[1], boundary[0], outsider[2], outsider[0]):
            return None

    if len(observed) < universe_size:
        fully_unseen_upper = next_bounds[0] + next_bounds[1]
        if boundary[1] <= fully_unseen_upper:
            return None
    return [row[0] for row in winners]


def replay_complete_wrrf(
    dense_ranking: Sequence[str],
    sparse_ranking: Sequence[str],
    *,
    top_k: int = 20,
    constant: int = 60,
    keep_trace: bool = True,
) -> ReplayResult:
    """Replay the frozen one-at-a-time schedule and certify its own fused result."""
    dense = list(dense_ranking)
    sparse = list(sparse_ranking)
    if len(set(dense)) != len(dense) or len(set(sparse)) != len(sparse):
        raise ValueError("rankings must not contain duplicate document ids")
    universe = set(dense) | set(sparse)
    if top_k > len(universe):
        raise ValueError("top_k exceeds ranking universe")

    positions = [0, 0]
    rankings = (dense, sparse)
    observed: dict[str, list[float | None]] = {}
    checks = 0
    trace: list[tuple[int, int, str]] = []
    while True:
        checks += 1
        certified = _certified_top_k(
            observed,
            (positions[0], positions[1]),
            (len(dense), len(sparse)),
            len(universe),
            top_k,
            constant,
        )
        if certified is not None:
            expected = complete_wrrf((dense, sparse), top_k=top_k, constant=constant)
            if certified != expected:
                raise AssertionError("replay certificate disagrees with complete WRRF")
            return ReplayResult(
                ordered_top_k=tuple(certified),
                dense_depth=positions[0],
                sparse_depth=positions[1],
                sparse_exhausted=positions[1] == len(sparse),
                checks=checks,
                trace=tuple(trace),
            )

        available = [index for index in range(2) if positions[index] < len(rankings[index])]
        if not available:
            raise AssertionError("rankings exhausted without certification")
        next_bounds = {
            index: wrrf_contribution(positions[index] + 1, constant) for index in available
        }
        channel = min(available, key=lambda index: (-next_bounds[index], index))
        rank = positions[channel] + 1
        document_id = rankings[channel][positions[channel]]
        contributions = observed.setdefault(document_id, [None, None])
        contributions[channel] = wrrf_contribution(rank, constant)
        positions[channel] += 1
        if keep_trace:
            trace.append((positions[0], positions[1], "dense" if channel == 0 else "sparse"))
