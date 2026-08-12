from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence

import numpy as np


def mean_draws_within_query(
    rows: Iterable[Mapping[str, object]], metric: str
) -> dict[tuple[str, str, str], float]:
    cells: defaultdict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        key = (str(row["dataset"]), str(row["query_id"]), str(row["method"]))
        cells[key].append(float(row[metric]))
    return {key: float(np.mean(values)) for key, values in cells.items()}


def stratified_macro_bootstrap(
    differences: Mapping[str, Sequence[float]],
    *,
    resamples: int = 10_000,
    seed: int = 20260813,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    if not differences or any(not values for values in differences.values()):
        raise ValueError("each dataset needs at least one paired difference")
    observed = float(np.mean([np.mean(values) for values in differences.values()]))
    random = np.random.default_rng(seed)
    samples = np.empty(resamples, dtype=np.float64)
    arrays = [np.asarray(values, dtype=np.float64) for values in differences.values()]
    for sample_index in range(resamples):
        dataset_means = [
            np.mean(array[random.integers(0, len(array), size=len(array))]) for array in arrays
        ]
        samples[sample_index] = np.mean(dataset_means)
    alpha = 1.0 - confidence
    lower, upper = np.quantile(samples, [alpha / 2.0, 1.0 - alpha / 2.0])
    return observed, float(lower), float(upper)


def paired_sign_flip_pvalue(
    differences: Sequence[float], *, resamples: int = 10_000, seed: int = 20260813
) -> float:
    values = np.asarray(differences, dtype=np.float64)
    if len(values) == 0:
        raise ValueError("differences cannot be empty")
    observed = abs(float(np.mean(values)))
    random = np.random.default_rng(seed)
    extreme = 0
    for _ in range(resamples):
        signs = random.choice(np.asarray([-1.0, 1.0]), size=len(values))
        extreme += abs(float(np.mean(values * signs))) >= observed
    return (extreme + 1.0) / (resamples + 1.0)


def stratified_sign_flip_pvalue(
    differences: Mapping[str, Sequence[float]],
    *,
    resamples: int = 10_000,
    seed: int = 20260813,
) -> float:
    if not differences or any(not values for values in differences.values()):
        raise ValueError("each dataset needs at least one paired difference")
    arrays = [np.asarray(values, dtype=np.float64) for values in differences.values()]
    observed = abs(float(np.mean([array.mean() for array in arrays])))
    random = np.random.default_rng(seed)
    extreme = 0
    for _ in range(resamples):
        statistic = float(
            np.mean(
                [
                    np.mean(array * random.choice((-1.0, 1.0), size=len(array)))
                    for array in arrays
                ]
            )
        )
        extreme += abs(statistic) >= observed
    return (extreme + 1.0) / (resamples + 1.0)


def holm_adjust(pvalues: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(pvalues.items(), key=lambda item: item[1])
    adjusted: dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for index, (name, pvalue) in enumerate(ordered):
        running = max(running, min(1.0, (total - index) * pvalue))
        adjusted[name] = running
    return adjusted
