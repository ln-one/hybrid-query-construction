from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def ndcg_at_k(ranking: Sequence[str], qrels: Mapping[str, int], k: int = 10) -> float:
    def dcg(relevances: Sequence[int]) -> float:
        return sum(
            (2**grade - 1) / math.log2(rank + 1) for rank, grade in enumerate(relevances, 1)
        )

    observed = [int(qrels.get(document_id, 0)) for document_id in ranking[:k]]
    ideal = sorted((int(value) for value in qrels.values()), reverse=True)[:k]
    denominator = dcg(ideal)
    return 0.0 if denominator == 0.0 else dcg(observed) / denominator


def recall_at_k(ranking: Sequence[str], qrels: Mapping[str, int], k: int = 20) -> float:
    relevant = {document_id for document_id, grade in qrels.items() if grade > 0}
    if not relevant:
        return 0.0
    return len(relevant & set(ranking[:k])) / len(relevant)
