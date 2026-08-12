import numpy as np

from hybrid_query_construction.fusion import rank_scores
from hybrid_query_construction.methods import orthogonal_residual, sparse_score_product


def test_orthogonal_residual_preserves_original_coefficient() -> None:
    original = np.asarray([2.0, 0.0, 0.0], dtype=np.float32)
    references = [np.asarray([3.0, 4.0, 0.0], dtype=np.float32)]
    result = orthogonal_residual(original, references)
    assert result[0] > 0.0
    assert result[1] > 0.0
    assert result[2] == 0.0


def test_orthogonal_residual_degenerates_to_original_without_new_direction() -> None:
    original = np.asarray([1.0, 2.0, 3.0], dtype=np.float32)
    references = [original * 2.0, original * 4.0]
    expected = original / np.linalg.norm(original)
    np.testing.assert_allclose(orthogonal_residual(original, references), expected, atol=1e-6)


def test_sparse_product_has_intersection_support() -> None:
    original = {"a": 2.0, "b": 3.0}
    rewrite = {"b": 4.0, "c": 5.0}
    assert sparse_score_product(original, rewrite) == {"b": 12.0}


def test_sparse_product_ranking_is_scale_invariant() -> None:
    original = {"a": 2.0, "b": 3.0}
    rewrite = {"a": 7.0, "b": 2.0}
    scaled = {key: value * 11.0 for key, value in original.items()}
    assert rank_scores(sparse_score_product(original, rewrite)) == rank_scores(
        sparse_score_product(scaled, rewrite)
    )
