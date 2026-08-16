import numpy as np

from hybrid_query_construction.fusion import rank_scores
from hybrid_query_construction.mechanism import dense_geometry, sparse_reordering
from hybrid_query_construction.methods import (
    contextual_mean,
    mugi_sparse_rewrite,
    orthogonal_residual,
    sparse_score_product,
)


def test_contextual_mean_accepts_encoder_array() -> None:
    references = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    expected = np.asarray([1.0, 1.0], dtype=np.float32) / np.sqrt(2.0)
    np.testing.assert_allclose(contextual_mean(references), expected, atol=1e-6)


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


def test_orthogonal_residual_stays_within_45_degrees_for_unit_inputs() -> None:
    original = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    references = [np.asarray([0.0, 1.0, 0.0], dtype=np.float32)]
    result = orthogonal_residual(original, references)
    cosine = float(np.dot(result, original))
    assert cosine >= (1.0 / np.sqrt(2.0)) - 1e-6


def test_sparse_product_has_intersection_support() -> None:
    original = {"a": 2.0, "b": 3.0}
    rewrite = {"b": 4.0, "c": 5.0}
    assert sparse_score_product(original, rewrite) == {"b": 12.0}


def test_sparse_product_preserves_original_support_for_expanded_query() -> None:
    original = {"a": 2.0, "b": 3.0}
    rewrite = {"a": 5.0, "b": 4.0, "c": 7.0}
    assert sparse_score_product(original, rewrite).keys() == original.keys()


def test_sparse_product_preserves_ranking_without_new_evidence() -> None:
    original = {"a": 2.0, "b": 3.0, "c": 5.0}
    rewrite = {key: value * 7.0 for key, value in original.items()}
    assert rank_scores(sparse_score_product(original, rewrite)) == rank_scores(original)


def test_sparse_product_ranking_is_scale_invariant() -> None:
    original = {"a": 2.0, "b": 3.0}
    rewrite = {"a": 7.0, "b": 2.0}
    scaled = {key: value * 11.0 for key, value in original.items()}
    assert rank_scores(sparse_score_product(original, rewrite)) == rank_scores(
        sparse_score_product(scaled, rewrite)
    )


def test_dense_geometry_reports_known_angle() -> None:
    geometry = dense_geometry(
        np.asarray([1.0, 0.0], dtype=np.float32),
        [np.asarray([0.0, 1.0], dtype=np.float32)],
    )
    assert geometry.residual_norm == 1.0
    assert geometry.angle_degrees == 45.0


def test_sparse_reordering_reports_support_and_relevant_rank_gain() -> None:
    diagnostics = sparse_reordering(
        ["a", "b", "c", "d"],
        ["b", "a", "d", "c"],
        {"b": 1, "c": 1, "missing": 1},
    )
    assert diagnostics.support_equal
    assert diagnostics.support_retention == 1.0
    assert diagnostics.missing_documents == 0
    assert diagnostics.top20_overlap == 1.0
    assert diagnostics.ranked_relevant_documents == 2
    assert diagnostics.relevant_mean_rank_gain == 0.0
    assert diagnostics.relevant_reciprocal_rank_delta > 0.0


def test_mugi_repetition_matches_public_integer_rule() -> None:
    query = "abcd"
    references = ["x" * 32]
    assert mugi_sparse_rewrite(query, references, beta=4).split().count(query) == 2
