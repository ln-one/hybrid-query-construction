from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .methods import l2_normalize

FloatArray = NDArray[np.float32]


@dataclass(frozen=True)
class DenseGeometry:
    residual_norm: float
    angle_degrees: float


@dataclass(frozen=True)
class SparseReordering:
    support_equal: bool
    support_retention: float
    missing_documents: int
    top20_overlap: float
    top100_overlap: float
    relevant_reciprocal_rank_delta: float
    relevant_mean_rank_gain: float
    ranked_relevant_documents: int


def dense_geometry(
    original_vector: FloatArray,
    contextual_reference_vectors: Sequence[FloatArray],
) -> DenseGeometry:
    """Measure the orthogonal semantic increment used by DESA."""
    if len(contextual_reference_vectors) == 0:
        raise ValueError("at least one contextual reference vector is required")
    original = l2_normalize(original_vector)
    references = np.stack(
        [
            l2_normalize(np.asarray(vector, dtype=np.float32))
            for vector in contextual_reference_vectors
        ]
    )
    reference_mean = np.mean(references, axis=0, dtype=np.float32)
    residual = reference_mean - float(np.dot(original, reference_mean)) * original
    residual_norm = float(np.linalg.norm(residual))
    return DenseGeometry(
        residual_norm=residual_norm,
        angle_degrees=float(np.degrees(np.arctan(residual_norm))),
    )


def _overlap(left: Sequence[str], right: Sequence[str], cutoff: int) -> float:
    denominator = min(cutoff, len(left), len(right))
    if denominator == 0:
        return 1.0
    return float(
        len(np.intersect1d(np.asarray(left[:cutoff]), np.asarray(right[:cutoff])))
        / denominator
    )


def sparse_reordering(
    original_ranking: Sequence[str],
    anchored_ranking: Sequence[str],
    qrels: Mapping[str, int],
) -> SparseReordering:
    """Describe how anchoring reorders the original Sparse support."""
    original_array = np.asarray(original_ranking)
    anchored_array = np.asarray(anchored_ranking)
    support_equal = len(original_array) == len(anchored_array) and np.array_equal(
        np.sort(original_array), np.sort(anchored_array)
    )
    missing_documents = len(np.setdiff1d(original_array, anchored_array))
    support_retention = (
        1.0
        if len(original_array) == 0
        else 1.0 - missing_documents / len(original_array)
    )
    relevant = {document_id for document_id, grade in qrels.items() if grade > 0}
    original_positions: dict[str, int] = {}
    anchored_positions: dict[str, int] = {}
    for rank, document_id in enumerate(original_array, 1):
        if document_id in relevant:
            original_positions[document_id] = rank
    for rank, document_id in enumerate(anchored_array, 1):
        if document_id in relevant:
            anchored_positions[document_id] = rank
    common = sorted(original_positions.keys() & anchored_positions.keys())
    if common:
        reciprocal_delta = float(
            np.mean(
                [
                    1.0 / anchored_positions[document_id]
                    - 1.0 / original_positions[document_id]
                    for document_id in common
                ]
            )
        )
        rank_gain = float(
            np.mean(
                [
                    original_positions[document_id] - anchored_positions[document_id]
                    for document_id in common
                ]
            )
        )
    else:
        reciprocal_delta = 0.0
        rank_gain = 0.0
    return SparseReordering(
        support_equal=support_equal,
        support_retention=support_retention,
        missing_documents=missing_documents,
        top20_overlap=_overlap(original_ranking, anchored_ranking, 20),
        top100_overlap=_overlap(original_ranking, anchored_ranking, 100),
        relevant_reciprocal_rank_delta=reciprocal_delta,
        relevant_mean_rank_gain=rank_gain,
        ranked_relevant_documents=len(common),
    )
