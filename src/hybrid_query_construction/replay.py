from __future__ import annotations

import heapq
from collections.abc import Sequence

from .fusion import complete_wrrf, wrrf_contribution
from .models import ReplayResult


def _precedes(score_a: float, id_a: str, score_b: float, id_b: str) -> bool:
    return score_a > score_b or (score_a == score_b and id_a < id_b)


class _IncrementalCertificate:
    """Maintain the replay certificate without sorting every observed item per step."""

    def __init__(self, universe_size: int, top_k: int, constant: int) -> None:
        self.universe_size = universe_size
        self.top_k = top_k
        self.constant = constant
        self.contributions: dict[str, list[float | None]] = {}
        self.versions: dict[str, int] = {}
        self.lower_heap: list[tuple[float, str, int]] = []
        self.category_heaps: dict[int, list[tuple[float, str, int]]] = {
            1: [],
            2: [],
            3: [],
        }

    def observe(self, document_id: str, channel: int, contribution: float) -> None:
        values = self.contributions.setdefault(document_id, [None, None])
        values[channel] = contribution
        version = self.versions.get(document_id, 0) + 1
        self.versions[document_id] = version
        lower = sum(value or 0.0 for value in values)
        category = (1 if values[0] is not None else 0) | (2 if values[1] is not None else 0)
        entry = (-lower, document_id, version)
        heapq.heappush(self.lower_heap, entry)
        heapq.heappush(self.category_heaps[category], entry)

    def _valid(self, entry: tuple[float, str, int], category: int | None = None) -> bool:
        _, document_id, version = entry
        if self.versions.get(document_id) != version:
            return False
        if category is None:
            return True
        values = self.contributions[document_id]
        current = (1 if values[0] is not None else 0) | (2 if values[1] is not None else 0)
        return current == category

    def _top_documents(self) -> list[str]:
        selected: list[tuple[float, str, int]] = []
        while self.lower_heap and len(selected) < self.top_k:
            entry = heapq.heappop(self.lower_heap)
            if self._valid(entry):
                selected.append(entry)
        for entry in selected:
            heapq.heappush(self.lower_heap, entry)
        return [entry[1] for entry in selected]

    def _best_outsider(self, category: int, winners: set[str]) -> str | None:
        heap = self.category_heaps[category]
        held: list[tuple[float, str, int]] = []
        result: str | None = None
        while heap:
            entry = heapq.heappop(heap)
            if not self._valid(entry, category):
                continue
            held.append(entry)
            if entry[1] not in winners:
                result = entry[1]
                break
        for entry in held:
            heapq.heappush(heap, entry)
        return result

    def certify(self, positions: Sequence[int], lengths: Sequence[int]) -> list[str] | None:
        if len(self.contributions) < self.top_k:
            return None
        next_bounds = tuple(
            0.0
            if positions[index] == lengths[index]
            else wrrf_contribution(positions[index] + 1, self.constant)
            for index in range(2)
        )
        winners = self._top_documents()
        if len(winners) < self.top_k:
            return None

        def lower(document_id: str) -> float:
            return sum(value or 0.0 for value in self.contributions[document_id])

        def upper(document_id: str) -> float:
            values = self.contributions[document_id]
            return lower(document_id) + sum(
                next_bounds[index] for index, value in enumerate(values) if value is None
            )

        for left_index, left_id in enumerate(winners):
            for right_id in winners[left_index + 1 :]:
                if not _precedes(lower(left_id), left_id, upper(right_id), right_id):
                    return None

        winner_set = set(winners)
        boundary_id = winners[-1]
        boundary_lower = lower(boundary_id)
        for category in (1, 2, 3):
            outsider_id = self._best_outsider(category, winner_set)
            if outsider_id is not None and not _precedes(
                boundary_lower, boundary_id, upper(outsider_id), outsider_id
            ):
                return None

        if len(self.contributions) < self.universe_size:
            fully_unseen_upper = next_bounds[0] + next_bounds[1]
            if boundary_lower <= fully_unseen_upper:
                return None
        return winners


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
    certificate = _IncrementalCertificate(len(universe), top_k, constant)
    checks = 0
    trace: list[tuple[int, int, str]] = []
    while True:
        checks += 1
        certified = certificate.certify(positions, (len(dense), len(sparse)))
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
        certificate.observe(document_id, channel, wrrf_contribution(rank, constant))
        positions[channel] += 1
        if keep_trace:
            trace.append((positions[0], positions[1], "dense" if channel == 0 else "sparse"))
