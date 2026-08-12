import pytest

from hybrid_query_construction.metrics import ndcg_at_k, recall_at_k
from hybrid_query_construction.statistics import (
    holm_adjust,
    stratified_macro_bootstrap,
    stratified_sign_flip_pvalue,
)


def test_metrics() -> None:
    ranking = ["a", "b", "c"]
    qrels = {"a": 2, "c": 1}
    assert ndcg_at_k(ranking, qrels, 1) == pytest.approx(1.0)
    assert recall_at_k(ranking, qrels, 2) == pytest.approx(0.5)


def test_stratified_macro_bootstrap_is_deterministic() -> None:
    values = {"d1": [1.0, 2.0], "d2": [3.0, 4.0]}
    first = stratified_macro_bootstrap(values, resamples=100, seed=9)
    second = stratified_macro_bootstrap(values, resamples=100, seed=9)
    assert first == second
    assert first[0] == pytest.approx(2.5)


def test_holm_adjustment_is_monotone_in_sorted_order() -> None:
    adjusted = holm_adjust({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted["a"] <= adjusted["c"] <= adjusted["b"]


def test_stratified_sign_flip_is_bounded() -> None:
    value = stratified_sign_flip_pvalue(
        {"a": [1.0, 2.0], "b": [0.5, 0.25]}, resamples=100, seed=4
    )
    assert 0.0 <= value <= 1.0
